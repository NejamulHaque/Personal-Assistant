<<<<<<< HEAD
# ✅ Use official lightweight Python image
FROM python:3.12-slim

# 🧱 Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🧰 Create working directory
WORKDIR /app

# 🧩 Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copy project files
COPY . .

# ✅ Expose port (Railway will auto bind to PORT env)
EXPOSE 5000

# 🚀 Start app
CMD ["python", "app.py"]
# Fix invalid kernel version causing pip failure
ENV PYTHON_VERSION_OVERRIDE=3.10
=======
# ✅ Use official Python slim image (small & fast)
FROM python:3.12-slim

# ✅ Set environment variables to avoid .pyc files and enable buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ✅ Set working directory
WORKDIR /app

# ✅ Install required OS packages for MySQL connector
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev default-libmysqlclient-dev pkg-config

# ✅ Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Copy all project files into the container
COPY . .

# ✅ Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# ✅ Expose the port Railway will map
EXPOSE 8080

# ✅ Default command to run the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
>>>>>>> 9a88812 (Initial commit)
