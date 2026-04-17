# 🔐 SecureAuth - Multi-Factor Authentication System

A secure authentication framework built using Flask that implements Multi-Factor Authentication (MFA) using:

- Password Authentication
- TOTP (Google Authenticator)
- Email OTP (Fallback with Resend)
- Activity Logging Dashboard

---

## 🚀 Features

### 🔐 Authentication System
- User Registration with secure password hashing (bcrypt)
- Login with credential validation
- Account blocking after multiple failed attempts

### 📱 TOTP (Time-Based OTP)
- QR Code generation for Google Authenticator
- 6-digit OTP verification
- Time-based expiry
- Limited attempts protection

### 📧 Email OTP (Fallback)
- Triggered when TOTP fails or expires
- 4-digit OTP sent via email (Brevo API)
- OTP expiry handling
- Resend OTP functionality

### 📊 Dashboard & Logs
- User dashboard after successful login
- Activity logs tracking:
  - Login attempts
  - OTP verification
  - Failures & blocks
- Displays IP address & timestamps

---

## 🧠 System Flow

Register → QR Setup → Login → TOTP Verification  
→ (Fail / Expire) → Email OTP (Resend Option)  
→ Dashboard → View Logs

---

## 🛠️ Tech Stack

- Backend: Flask (Python)
- Database: SQLite
- Authentication: bcrypt, pyotp
- Email Service: Brevo (Sendinblue API)
- Frontend: HTML, CSS, Bootstrap
- Version Control: Git & GitHub

---

## 📁 Project Structure

SecureAuthOS/
│
├── app/
│   └── services/
│       ├── auth_service.py
│       ├── mfa_service.py
│       └── email_service.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── qr.html
│   ├── totp.html
│   ├── otp.html
│   ├── dashboard.html
│   └── logs.html
│
├── static/
│   ├── css/style.css
│   └── js/script.js
│
├── app.py
├── requirements.txt
└── .gitignore

---

## ⚙️ Setup Instructions

1. Clone the repository  
git clone https://github.com/YOUR_USERNAME/SecureAuth-MFA-System.git  
cd SecureAuth-MFA-System  

2. Create virtual environment  
python -m venv venv  
venv\Scripts\activate  

3. Install dependencies  
pip install -r requirements.txt  

4. Create .env file  
BREVO_API_KEY=your_api_key  
SENDER_EMAIL=your_verified_email  

5. Run the application  
python app.py  

---

## 🔒 Security Features

- Password hashing using bcrypt  
- TOTP-based MFA  
- Session management  
- Attempt limiting & account blocking  
- OTP expiry handling  
- Secure API key management using .env  

---

## 🎯 Future Enhancements

- OTP expiry countdown timer  
- Mobile UI improvements  
- JWT-based authentication  
- Cloud deployment (Render / AWS)  

---

## 👨‍💻 Author

Yashvanth G  
B.Tech CSE @ LPU  

---

## ⭐ If you like this project

Give it a star on GitHub!
