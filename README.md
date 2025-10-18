# Quizly – Backend (Django + DRF)

This repository contains the backend implementation of **Quizly**, an AI-powered quiz generator that creates interactive quizzes from YouTube videos using **Whisper** for transcription and **Gemini (Google AI)** for quiz generation.

---

## 🎯 Features

- **AI-Based Quiz Creation**
  - Automatically extracts audio from YouTube videos  
  - Transcribes the content using OpenAI’s Whisper model  
  - Generates a structured multiple-choice quiz via Gemini API  

- **Quiz Management**
  - Create, view, update, and delete quizzes  
  - Each quiz stores its questions, options, and correct answers in the database  

- **Authentication**
  - JWT-based authentication using access & refresh tokens  
  - Only authenticated users can create and manage their own quizzes  

---

## 🛠️ Tech Stack
- **Python 3.12**  
- **Django 5.x**  
- **Django REST Framework (DRF)**  
- **SimpleJWT** (cookie-based authentication)  
- **Whisper AI** (speech-to-text transcription)  
- **Gemini API** (quiz generation)  

---

## 🌍 Deployment

The backend will soon be deployed using the following stack:

- **Gunicorn** – WSGI server for running Django  
- **Nginx** – reverse proxy handling HTTPS and static files  
- **Supervisor** – keeps Gunicorn running in the background  
- **Certbot (Let’s Encrypt)** – manages free SSL certificates  

Deployed version available soon at  
👉 [https://quizly-api.muzammal-anwar.at](https://quizly-api.muzammal-anwar.at)

---

## 🚀 Getting Started

Follow these steps to set up and run the backend locally.

### 1. Clone the repository
```bash
git clone https://github.com/MuzammalAnwar/Quizly-Backend.git
cd Quizly-Backend
```

### 2. Create and activate a virtual environment
Windows (PowerShell)
```bash
python -m venv env
"env\Scripts\activate"
```
Linux / macOS
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a file named .env in the project root (same directory as manage.py) and configure the variables if required:
```bash
# =========================================
# Django Settings
# =========================================

# Keep this key secret in production!
# To generate one locally, run:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY="your_generated_secret_key_here"

# Debug mode — use True for local development, False for production
DEBUG=True

# Allowed hosts (comma-separated, no spaces)
ALLOWED_HOSTS=127.0.0.1,localhost

# CORS & CSRF settings
CORS_ALLOWED_ORIGINS=http://127.0.0.1:4200,http://localhost:4200
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
CSRF_COOKIE_DOMAIN=your_domain


# =========================================
# External API Keys
# =========================================

# Gemini / Google API key
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Apply database migrations
```bash
python manage.py migrate
python manage.py createsuperuser  # optional
```

### 6. Run the development server
```bash
python manage.py runserver
# http://127.0.0.1:8000/
```
