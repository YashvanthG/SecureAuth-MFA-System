# 🔐 SecureAuth - Multi-Factor Authentication System

A secure authentication framework built using Flask that implements **Multi-Factor Authentication (MFA)** using:

- 🔑 Password Authentication
- 📱 TOTP (Google Authenticator)
- 📧 Email OTP (Fallback with Resend)
- 📊 Activity Logging Dashboard

---

## 🚀 Features

### 🔐 Authentication System
- User Registration with secure password hashing (bcrypt)
- Login with credential validation
- Account blocking after multiple failed attempts

### 📱 TOTP (Time-Based OTP)
- QR Code generation for Google Authenticator
- 6-digit OTP verification
- Time-based expiry (30 seconds)
- Limited attempts protection

### 📧 Email OTP (Fallback)
- Triggered when TOTP fails or expires
- 4-digit OTP sent via email (Brevo API)
- OTP expiry handling
- 🔁 Resend OTP functionality

### 📊 Dashboard & Logs
- User dashboard after successful login
- Activity logs tracking:
  - Login attempts
  - OTP verification
  - Failures & blocks
- Displays IP address & timestamps

---

## 🧠 System Flow

```plaintext
Register → Scan QR → Login → TOTP Verification
        → (Fail / Expire)
        → Email OTP (Resend Option)
        → Dashboard → View Logs
