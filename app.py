from flask import Flask, render_template, request, redirect, url_for, session, send_file
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import bcrypt
import io
from xhtml2pdf import pisa

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "supersecret")

# MySQL connector setup (not flask_mysqldb!)
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = db.cursor(dictionary=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user["password"].encode("utf-8")):
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    search = request.form.get("search")
    filter = request.form.get("filter")

    query = "SELECT * FROM chat_history"
    params = []

    if search:
        query += " WHERE user_input LIKE %s OR ai_response LIKE %s"
        params.extend([f"%{search}%", f"%{search}%"])
    elif filter == "last_24":
        since = datetime.now() - timedelta(hours=24)
        query += " WHERE timestamp >= %s"
        params.append(since)
    elif filter == "last_7":
        since = datetime.now() - timedelta(days=7)
        query += " WHERE timestamp >= %s"
        params.append(since)

    query += " ORDER BY timestamp DESC"
    cursor.execute(query, params)
    results = cursor.fetchall()

    return render_template("index.html", results=results)

@app.route("/export")
def export_pdf():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC")
    results = cursor.fetchall()

    rendered = render_template("export.html", results=results)
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(rendered), dest=pdf)
    pdf.seek(0)
    return send_file(pdf, as_attachment=True, download_name="chat_history.pdf")

@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect(url_for("login"))

    cursor.execute("SELECT DATE(timestamp) as date, COUNT(*) as count FROM chat_history GROUP BY DATE(timestamp)")
    data = cursor.fetchall()
    dates = [row["date"].strftime("%Y-%m-%d") for row in data]
    counts = [row["count"] for row in data]

    return render_template("stats.html", dates=dates, counts=counts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 locally
    app.run(host="0.0.0.0", port=port, debug=True)