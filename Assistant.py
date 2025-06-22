import os

IS_RENDER = os.environ.get("RENDER") == "true"

if not IS_RENDER:
    import speech_recognition as sr
    import pyttsx3
    engine = pyttsx3.init()

    def speak(text):
        engine.say(text)
        engine.runAndWait()

    def take_command():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source)

            try:
                print("Recognizing...")
                query = recognizer.recognize_google(audio, language='en-in')
                print(f"Nejamul Haque: {query}")
                return query.lower()
            except sr.UnknownValueError:
                print("Could not understand, skipping...")
                return None
            except sr.RequestError:
                print("Could not request results; check your internet connection")
                speak("I am having trouble connecting to the internet.")
                return None
else:
    def speak(text):
        print("Assistant:", text)

    def take_command():
        return input("Type your command: ")


import json

import datetime
import webbrowser
import wikipedia
import os
import requests
import pywhatkit
import groq
from dotenv import load_dotenv
from groq import Groq
import mysql.connector
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Groq API client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = db.cursor()

print("ASSISTANT IS READY TO USE")



def speak(text):
    engine.say(text)
    engine.runAndWait()


def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"Nejamul Haque: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Could not understand, skipping...")
            return None
        except sr.RequestError:
            print("Could not request results; check your internet connection")
            speak("I am having trouble connecting to the internet.")
            return None


def greet():
    hour = int(datetime.now().hour)
    if hour < 12:
        speak("Good morning!")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am your personal assistant. How can I help you, Nejamul?")


def chat_with_gpt_context(user_input):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        print("AI:", reply)
        return reply
    except groq.GroqError as e:
        print(f"Groq API Error: {e}")
        speak("Sorry, something went wrong while talking to the AI.")
        return "Error"


API_KEY = os.getenv("OPENWEATHER_API")


def get_weather(city="Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
        else:
            return "Sorry, I couldn't fetch the weather. Please check the city name."
    except requests.exceptions.RequestException:
        return "There was an issue fetching the weather. Please check your internet connection."


def search_google(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Here are the search results for {query}.")


def play_youtube(song):
    speak(f"Playing {song} on YouTube.")
    pywhatkit.playonyt(song)


MEMORY_FILE = "memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding='utf-8') as file:
        json.dump(memory, file)


def remember_something(key, value):
    memory = load_memory()
    memory[key.lower()] = value
    save_memory(memory)


def recall_something(key):
    memory = load_memory()
    return memory.get(key.lower(), None)


def log_chat(user_input, ai_response):
    try:
        query = "INSERT INTO chat_history (user_input, ai_response) VALUES (%s, %s)"
        cursor.execute(query, (user_input, ai_response))
        db.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")


def recall_previous_queries(hours=24):
    try:
        since = datetime.now() - timedelta(hours=hours)
        cursor.execute("SELECT user_input, timestamp FROM chat_history WHERE timestamp >= %s ORDER BY timestamp", (since,))
        records = cursor.fetchall()
        if not records:
            speak("You haven't asked anything recently.")
        else:
            speak(f"You asked me {len(records)} questions in the last {hours} hours.")
            for r in records:
                print(f"[{r[1]}] You said: {r[0]}")
    except Exception as e:
        print(f"Error recalling memory: {e}")
        speak("I couldn't recall your recent memory.")


def perform_task(query):
    if query is None:
        return False

    if 'time' in query:
        speak(f"The current time is {datetime.now().strftime('%I:%M %p')}")
        return True

    elif 'weather' in query:
        words = query.split()
        if 'in' in words:
            city_index = words.index('in') + 1
            if city_index < len(words):
                city = words[city_index]
                speak(get_weather(city))
        else:
            speak("Fetching the weather for Delhi.")
            speak(get_weather())
        return True

    elif 'remember that' in query:
        try:
            info = query.replace('remember that', '').strip()
            key, value = info.split(' is ')
            remember_something(key, value)
            speak(f"I'll remember that {key} is {value}.")
        except ValueError:
            speak("Sorry, I couldn't remember that. Please say it like: 'Remember that my WiFi password is xyz123'.")
        return True

    elif 'what did i ask yesterday' in query:
        recall_previous_queries(24)
        return True

    elif 'what is' in query or 'do you remember' in query:
        words = query.replace('do you remember', '').replace('what is', '').strip()
        value = recall_something(words)
        if value:
            speak(f"You told me that {words} is {value}.")
        else:
            speak(f"Sorry, I don't remember anything about {words}.")
        return True

    elif 'show chat history' in query:
        cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC")
        for record in cursor.fetchall():
            print(f"[{record[3]}] You: {record[1]}\nAssistant: {record[2]}\n")
        return True

    elif 'open' in query or 'close' in query:
        apps = {
            'chrome': 'Google Chrome',
            'vs code': 'Visual Studio Code',
            'whatsapp': 'WhatsApp',
            'cursor': 'Cursor',
            'youtube': 'YouTube',
            'instagram': 'Instagram',
            'telegram': 'Telegram',
            'linkedin': 'Linkedin',
            'jupyterlab': 'JupyterLab',
            'xcode': 'Xcode',
            'snapchat': 'Snapchat',
            'imo': 'IMo',
            'threads': 'Threads',
            'botim': 'Botim',
            'intellij idea': 'IntelliJ IDEA',
            'notepad': 'TextEdit'
        }
        for key, app_name in apps.items():
            if f"open {key}" in query:
                os.system(f"open -a '{app_name}'")
                speak(f"Opening {app_name}")
                return True
            elif f"close {key}" in query:
                os.system(f"killall '{app_name}'")
                speak(f"Closing {app_name}")
                return True

    elif 'wikipedia' in query:
        speak("Searching Wikipedia...")
        query = query.replace("wikipedia", "").strip()
        if query:
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except wikipedia.exceptions.DisambiguationError:
                speak("There are multiple results. Searching on Google instead.")
                search_google(query)
            except wikipedia.exceptions.PageError:
                speak("I couldn't find anything on Wikipedia. Searching on Google.")
                search_google(query)
        else:
            speak("Please specify what you want to search on Wikipedia.")
        return True

    elif 'search for' in query:
        search_query = query.replace('search for', '').strip()
        search_google(search_query)
        return True

    elif 'play' in query and 'on youtube' in query:
        song = query.replace('play', '').replace('on youtube', '').strip()
        play_youtube(song)
        return True

    elif 'exit' in query or 'quit' in query:
        speak("Goodbye Nejamul Haque! Have a nice day, I will be back soon.")
        exit()

    return False


def main():
    greet()
    while True:
        print("Waiting for wake word...")
        wake_query = take_command()
        if wake_query and "hey assistant" in wake_query:
            speak("Yes Nejamul, I am listening.")
            query = take_command()
            if query:
                if 'exit' in query or 'quit' in query:
                    speak("Goodbye Nejamul Haque! Have a nice day.")
                    break

                is_command = perform_task(query)

                if not is_command:
                    response = chat_with_gpt_context(query)
                    if response and response != "Error":
                        speak(response)
                        log_chat(query, response)


if __name__ == "__main__":
    main()