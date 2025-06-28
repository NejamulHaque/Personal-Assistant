# 🤖 Personal AI Assistant

Your smart, voice-activated AI assistant powered by Python and Flask — built to help you with tasks like searching the web, controlling apps, saving memory, and more, all with a beautiful web dashboard.

---

## 🧠 Key Features

- 🎤 Voice interaction (STT + TTS)
- 📚 Wikipedia & web search fallback
- 🌦️ Weather updates
- 🎵 Play music on YouTube
- 📅 Smart memory with timestamps (stored in MySQL)
- 📄 Chat history view and PDF export
- 🔐 Login/Logout system (web dashboard)
- 📊 Query charts using Chart.js / Recharts
- 📦 Deploy-ready (Render, Clever Cloud, etc.)

---

## 📂 Project Structure
├── assistant_core.py        # Core voice logic
├── app.py                   # Flask backend (Web UI)
├── templates/               # HTML files (dashboard, login, history)
├── static/                  # CSS/JS/images
├── database/                # MySQL setup
├── utils/                   # PDF export, chat logic, memory utils
├── .env                     # Secure credentials
├── requirements.txt
└── README.md

  ---

## 🔧 Tech Stack

- **Python 3.10+**
- **Flask** (Web framework)
- **SpeechRecognition + pyttsx3**
- **MySQL** (Database for memory & history)
- **xhtml2pdf** (PDF export)
- **HTML, CSS, JavaScript** (Frontend)
- **Chart.js / Recharts** (for visual analytics)

---

## 🚀 Installation & Setup

1. **Clone the repo:**

   ```bash
   git clone https://github.com/yourusername/personal-assistant.git
   cd personal-assistant'''

2.	Create a virtual environment and install dependencies: 
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt

3.	Set up .env file with:
    MYSQL_HOST=your_host
    MYSQL_USER=your_user
    MYSQL_PASSWORD=your_password
    MYSQL_DB=your_database
    SECRET_KEY=your_secret_key

	4.	Run the assistant:
      ```bash
      python app.py

 ## 🌐 Web Dashboard Features
	•	👤 Login/Logout
	•	💬 Chat history display
	•	📄 Export to PDF
	•	📊 Query frequency chart
	•	🔍 Search by date/keywords
	•	🧠 View saved memories

## 🛡️ Security & Production
	•	✅ Use .env for secrets
	•	🔒 MySQL credentials protected
	•	📦 Deploy to Render, Vercel, or Clever Cloud
	•	🔑 Optional password hashing using bcrypt 

## 📸 Demo Screenshots



## 🙏 Credits

Built by Nejamul Haque
Voice Assistant + Web Integration by [OpenAI GPT & Python Libraries]
Inspired by productivity and accessibility tools

⸻

## 📬 Contact

📧 Email: nejamulhaque.05@gmail.com
🌐 Portfolio: https://nejamulportfolio.vercel.app/
