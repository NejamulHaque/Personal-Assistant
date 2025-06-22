from groq import Groq
import os
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
import requests
import wikipedia

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = db.cursor()

def ask_assistant(message):
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
        return f"Error: {str(e)}"

def log_chat(user_input, ai_response):
    try:
        cursor.execute("INSERT INTO chat_history (user_input, ai_response) VALUES (%s, %s)", (user_input, ai_response))
        db.commit()
    except Exception as e:
        print("DB Error:", e)