# assistant_core.py
import os
import wikipedia
import requests
from groq import Groq
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Database connection
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = db.cursor()

# Groq API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API = os.getenv("OPENWEATHER_API")

def get_weather(city="Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API}&units=metric"
    try:
        res = requests.get(url)
        data = res.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"The weather in {city} is {weather} with {temp}°C."
        else:
            return "City not found."
    except:
        return "Failed to fetch weather."

def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {summary}"
    except:
        return "Couldn't find results on Wikipedia."

def log_chat(user_input, ai_response):
    try:
        cursor.execute(
            "INSERT INTO chat_history (user_input, ai_response) VALUES (%s, %s)",
            (user_input, ai_response)
        )
        db.commit()
    except Exception as e:
        print("DB Error:", e)

def ask_assistant(message):
    if not message:
        return "Please say something."

    # Special triggers
    if "weather" in message:
        return get_weather()
    elif "wikipedia" in message:
        return search_wikipedia(message.replace("wikipedia", "").strip())

    # Default: AI reply
    try:
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