# 🧠 AI Personal Assistant (Flask Version)

A voice-enabled AI assistant with a web dashboard that supports:
- ✅ User login/logout
- 📄 Export chat history to PDF
- 📊 View daily usage stats with charts
- 💾 Stores history in MySQL (e.g., freesqldatabase.com)
- 🔒 Password-protected backend
- 🧠 Memory recall with timestamps

---

## 🚀 Features

- 🎙️ Wake-word-based assistant (`Hey Assistant`)
- 🌐 Web search fallback when Wikipedia fails
- 💾 Save queries and responses to a MySQL DB
- 📄 Download entire chat history as a PDF
- 📊 Daily stats visualization (Chart.js)
- ✅ Login system with bcrypt password hashing

---

## 🖥️ Web Dashboard Pages

| Route         | Purpose                        |
|---------------|--------------------------------|
| `/login`      | Login screen                   |
| `/`           | Main dashboard with chat table |
| `/export`     | Export chat history to PDF     |
| `/stats`      | Visual stats (queries per day) |
| `/logout`     | Logout                         |

---

## ⚙️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
