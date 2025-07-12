from werkzeug.utils import secure_filename
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, send_file, g, jsonify, stream_with_context, Response
from dotenv import load_dotenv
import mysql.connector
import base64
import os
from datetime import datetime, timedelta
import bcrypt
import io
from xhtml2pdf import pisa
from assistant_core import ask_assistant

# Load environment variables
load_dotenv()

# ✅ App setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "fallback-secret-key")
app.permanent_session_lifetime = timedelta(minutes=10)

@app.before_request
def make_session_permanent():
    session.permanent = True

# ------------------- DB CONNECTION -------------------

def get_db():
    if "db" not in g or not g.db.is_connected():
        g.db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            #password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            autocommit=True
        )
    return g.db

def get_cursor():
    return get_db().cursor(dictionary=True)

@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop("db", None)
    if db and db.is_connected():
        db.close()

# ------------------- AUTH ROUTES -------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return render_template("signup.html", error="Email already registered.")

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (name, email, hashed_pw))
        get_db().commit()
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user["password"].encode("utf-8")):
            session["user"] = username
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]

        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if not cursor.fetchone():
            return render_template("forgot_password.html", error="Username not found.")

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_pw, username))
        get_db().commit()
        return redirect(url_for("login"))

    return render_template("forgot_password.html")

# ------------------- CHAT & HOME -------------------

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC")
    results = cursor.fetchall()
    return render_template("index.html", results=results)

@app.route("/assistant-chat")
def assistant_chat():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "No message received"}), 400

    response = ask_assistant(message, username=session["user"])

    # Save to DB
    cursor = get_cursor()
    cursor.execute("INSERT INTO chat_history (user_input, ai_response) VALUES (%s, %s)", (message, response))
    get_db().commit()

    return jsonify({"reply": response})

@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    if "user" not in session:
        return "Unauthorized", 401

    data = request.json
    message = data.get("message")

    def generate():
        for chunk in ask_assistant(message, stream=True):
            yield f"data: {chunk}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

# ------------------- PDF EXPORT -------------------

@app.route("/export")
def export_pdf():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC")
    results = cursor.fetchall()

    rendered = render_template("export.html", results=results)
    pdf = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(rendered.encode("utf-8")), dest=pdf)
    pdf.seek(0)

    return send_file(pdf, as_attachment=True, download_name="chat_history.pdf")

# ------------------- STATS -------------------

@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT DATE(timestamp) AS date, COUNT(*) AS count FROM chat_history GROUP BY DATE(timestamp)")
    data = cursor.fetchall()
    dates = [row["date"].strftime("%Y-%m-%d") for row in data]
    counts = [row["count"] for row in data]

    return render_template("stats.html", dates=dates, counts=counts)

# ------------------- PROFILE -------------------

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (session["user"],))
    user = cursor.fetchone()

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form.get("password", "")
        profile_pic_filename = user.get("profile_pic")

        # Handle profile pic
        file = request.files.get("profile_pic")
        if file and file.filename and allowed_file(file.filename):
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(save_path)
            profile_pic_filename = unique_filename

        update_query = "UPDATE users SET username = %s, email = %s"
        params = [new_username, new_email]

        if new_password:
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            update_query += ", password = %s"
            params.append(hashed_pw)

        if profile_pic_filename:
            update_query += ", profile_pic = %s"
            params.append(profile_pic_filename)

        update_query += " WHERE username = %s"
        params.append(session["user"])

        cursor.execute(update_query, tuple(params))
        get_db().commit()
        session["user"] = new_username
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user)
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (session["user"],))
    user = cursor.fetchone()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        # Handle profile pic (optional)
        profile_pic = request.files.get("profile_pic")
        if profile_pic:
            pic_data = profile_pic.read()
            cursor.execute("UPDATE users SET profile_pic=%s WHERE username=%s", (pic_data, session["user"]))

        cursor.execute("UPDATE users SET username=%s, email=%s WHERE username=%s",
                       (name, email, session["user"]))
        get_db().commit()
        session["user"] = name  # Update session if username changed
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

# ------------------- MAIN -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
