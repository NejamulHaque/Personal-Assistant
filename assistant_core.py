import os
import wikipedia
import requests
from groq import Groq
import mysql.connector
from dotenv import load_dotenv
# from datetime import datetime, timedelta

load_dotenv()

# Database connection
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = db.cursor()

# Groq API client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API = os.getenv("OPENWEATHER_API")

# ------------------ Utilities ------------------

def get_weather(city="Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API}&units=metric"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"The weather in {city} is {weather} with {temp}°C."
        else:
            return "City not found."
    except requests.exceptions.RequestException:
        return "Failed to fetch weather."
    except KeyError:
        return "Unexpected response format from weather service."

def search_wikipedia(query):
    """
    Search Wikipedia for information about the given query.
    
    Args:
        query (str): The search term to look up on Wikipedia
        
    Returns:
        str: A formatted string containing the Wikipedia summary or an error message
             if the search fails
    """
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {summary}"
    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
        return "Couldn't find results on Wikipedia."

def log_chat(user_input, ai_response):
    try:
        cursor.execute(
            "INSERT INTO chat_history (user_input, ai_response) VALUES (%s, %s)",
            (user_input, ai_response)
        )
        db.commit()
    except mysql.connector.Error as e:
        print("DB Error:", e)

# ------------------ Core Assistant ------------------
def ask_assistant(message, username=None, stream=False):
    if not message:
        return "Please say something."

    # Memory Save
    if message.lower().startswith("remember that"):
        try:
            info = message.replace("remember that", "").strip()
            key, value = info.split(" is ")
            save_memory(username, key.strip(), value.strip())
            return f"Got it! I’ll remember that {key.strip()} is {value.strip()}."
        except:
            return "Please say it like: 'Remember that my birthday is 12 July'"

    # Memory Recall
    if message.lower().startswith("what is") or "do you remember" in message.lower():
        key = message.lower().replace("what is", "").replace("do you remember", "").strip()
        value = recall_memory(username, key)
        if value:
            return f"You told me that {key} is {value}."
        else:
            return f"I don't remember anything about {key}."

    # Wikipedia & Weather (existing)
    if "weather" in message:
        return get_weather()
    elif "wikipedia" in message:
        return search_wikipedia(message.replace("wikipedia", "").strip())

    # 🧠 AI Reply (Stream or Not)
    try:
        if stream:
            full_reply = ""
            stream_resp = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": message}
                ],
                stream=True
            )
            for chunk in stream_resp:
                delta = chunk.choices[0].delta.content or ""
                full_reply += delta
                yield delta
            log_chat(message, full_reply)
        else:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": message}
                ]
            )
            reply = response.choices[0].message.content
            log_chat(message, reply)
            return reply
    except Exception as e:
        print("Groq Error:", e)
        return "I'm having trouble connecting to the AI."
        
def save_memory(username, key, value):
    try:
        cursor.execute("REPLACE INTO memory (username, memory_key, memory_value) VALUES (%s, %s, %s)", (username, key.lower(), value))
        db.commit()
    except mysql.connector.Error as e:
        print("Memory Save Error:", e)

def recall_memory(username, key):
    try:
        cursor.execute("SELECT memory_value FROM memory WHERE username = %s AND memory_key = %s", (username, key.lower()))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print("Memory Recall Error:", e)
        return None
