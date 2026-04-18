from flask import Flask, render_template, request, session, redirect, url_for
from app.services.auth_service import register_user, login_user
from app.services.email_service import send_otp_email
from app.services.mfa_service import verify_totp
import sqlite3
import qrcode
import io
import base64
import time
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------- DB --------------------

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password BLOB,
        email TEXT,
        totp_secret TEXT,
        attempts INTEGER DEFAULT 0,
        is_blocked INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        status TEXT,
        ip_address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# -------------------- LOGGING --------------------

def log_activity(username, action, status):
    try:
        conn = get_db()
        cursor = conn.cursor()
        ip = request.remote_addr or "UNKNOWN"

        cursor.execute("""
            INSERT INTO logs (username, action, status, ip_address)
            VALUES (?, ?, ?, ?)
        """, (username, action, status, ip))

        conn.commit()
        conn.close()
    except:
        pass

# -------------------- HOME --------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

# -------------------- REGISTER --------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        secret = register_user(username, password, email)

        if secret == "USERNAME_EXISTS":
            return render_template('register.html',
                                   error="Username already exists ❌")

        log_activity(username, "REGISTER", "SUCCESS")

        uri = f"otpauth://totp/SecureAuthApp:{username}?secret={secret}&issuer=SecureAuthApp"

        qr = qrcode.make(uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        img_str = base64.b64encode(buffer.getvalue()).decode()

        return render_template("qr.html", qr=img_str)

    return render_template('register.html', error=None)

# -------------------- LOGIN --------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        log_activity(username, "LOGIN_ATTEMPT", "START")

        result, _, user = login_user(username, password)

        if result == "TOTP_REQUIRED":
            log_activity(user, "PASSWORD", "SUCCESS")

            session.clear()
            session['temp_user'] = user
            session['totp_attempts'] = 0
            session['totp_start_time'] = time.time()

            return render_template('totp.html', error=None, show_fallback=False)

        elif result == "BLOCKED":
            log_activity(username, "LOGIN", "BLOCKED")
            return render_template('login.html',
                                   error="Account is blocked ❌")

        elif result.startswith("INVALID"):
            attempts = result.split("_")[1]
            log_activity(username, "PASSWORD", "FAILED")
            return render_template('login.html',
                                   error=f"Invalid credentials ({attempts}/3)")

        elif result == "USER_NOT_FOUND":
            log_activity(username, "LOGIN", "USER_NOT_FOUND")
            return render_template('login.html',
                                   error="User not found ❌")

    return render_template('login.html', error=None)

# -------------------- TOTP VERIFY --------------------

@app.route('/verify-totp', methods=['POST'])
def verify_totp_route():
    user = session.get('temp_user')

    if not user:
        return redirect(url_for('login'))

    code = request.form['code']
    attempts = session.get('totp_attempts', 0)
    start_time = session.get('totp_start_time', time.time())

    # ⏱ TIME EXPIRED
    if time.time() - start_time > 90:
        log_activity(user, "TOTP", "EXPIRED")
        return render_template('totp.html',
                               error="Session expired ⏱️. Use Email OTP.",
                               show_fallback=True)

    # ✅ SUCCESS → GO TO DASHBOARD (FIXED MAIN BUG)
    if verify_totp(user, code):
        log_activity(user, "TOTP", "SUCCESS")

        session.clear()
        session['user'] = user

        log_activity(user, "LOGIN", "SUCCESS")

        return redirect(url_for('dashboard'))

    # ❌ FAILED
    attempts += 1
    session['totp_attempts'] = attempts

    if attempts >= 3:
        log_activity(user, "TOTP", "BLOCKED")
        return render_template('totp.html',
                               error="Too many attempts ❌",
                               show_fallback=True)

    log_activity(user, "TOTP", "FAILED")
    return render_template('totp.html',
                           error=f"Invalid TOTP ({attempts}/3)",
                           show_fallback=False)

# -------------------- EMAIL OTP SEND --------------------

@app.route('/send-email-otp', methods=['GET', 'POST'])
def send_email_otp():
    user = session.get('temp_user')

    if not user:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('confirm_otp.html')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE username=?", (user,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return render_template('login.html',
                               error="User not found ❌")

    email = result[0]
    otp = str(random.randint(1000, 9999))

    session['otp'] = otp
    session['otp_expiry'] = time.time() + 120
    session['user'] = user
    session['otp_attempts'] = 0

    send_otp_email(email, otp)
    log_activity(user, "EMAIL_OTP", "SENT")

    return render_template('otp.html', error=None)

# -------------------- EMAIL OTP VERIFY --------------------

@app.route('/verify-otp', methods=['POST'])
def verify_email_otp():
    user = session.get('user')

    if not user:
        return redirect(url_for('login'))

    user_otp = request.form['otp']
    session_otp = session.get('otp')
    expiry = session.get('otp_expiry')

    if not session_otp or not expiry:
        return redirect(url_for('login'))

    if time.time() > expiry:
        log_activity(user, "EMAIL_OTP", "EXPIRED")
        return render_template('otp.html', error="OTP Expired ❌")

    if user_otp == session_otp:
        log_activity(user, "EMAIL_OTP", "SUCCESS")

        session.clear()
        session['user'] = user

        return redirect(url_for('dashboard'))

    log_activity(user, "EMAIL_OTP", "FAILED")
    return render_template('otp.html', error="Invalid OTP ❌")

# -------------------- DASHBOARD --------------------

@app.route('/dashboard')
def dashboard():
    user = session.get('user')

    if not user:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=user)

# -------------------- LOGS --------------------

@app.route('/logs/<username>')
def view_logs(username):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT action, status, ip_address, timestamp
        FROM logs
        WHERE username = ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (username,))

    logs = cursor.fetchall()
    conn.close()

    return render_template('logs.html', logs=logs, username=username)

# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# -------------------- RUN --------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)