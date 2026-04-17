import sqlite3
import bcrypt
import pyotp

# -------------------- REGISTER --------------------

def register_user(username, password, email):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    totp_secret = pyotp.random_base32()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, totp_secret) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, totp_secret)
        )
        conn.commit()
        return totp_secret

    except sqlite3.IntegrityError:   # ✅ specific error
        return "Username already exists"

    finally:
        conn.close()


# -------------------- LOGIN --------------------

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, password, email, totp_secret, attempts, is_blocked FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "USER_NOT_FOUND", None, None

    stored_password = user[2]
    attempts = user[5]
    is_blocked = user[6]

    # 🔒 Check if blocked
    if is_blocked:
        conn.close()
        return "Account is BLOCKED", None, None

    # 🔑 Password correct
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        cursor.execute("UPDATE users SET attempts=0 WHERE username=?", (username,))
        conn.commit()
        conn.close()

        return "TOTP_REQUIRED", None, username

    # ❌ Wrong password
    attempts += 1

    if attempts >= 3:
        cursor.execute(
            "UPDATE users SET attempts=?, is_blocked=1 WHERE username=?",
            (attempts, username)
        )
        conn.commit()
        conn.close()

        return "BLOCKED", None, None

    else:
        cursor.execute(
            "UPDATE users SET attempts=? WHERE username=?",
            (attempts, username)
        )
        conn.commit()
        conn.close()

        return f"INVALID_{attempts}", None, None