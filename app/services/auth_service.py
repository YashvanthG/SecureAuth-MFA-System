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

    except sqlite3.IntegrityError:
        return "USERNAME_EXISTS"   # ✅ standardized

    finally:
        conn.close()


# -------------------- LOGIN --------------------

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, password, attempts, is_blocked
        FROM users
        WHERE username=?
    """, (username,))

    user = cursor.fetchone()

    # ❌ USER NOT FOUND
    if not user:
        conn.close()
        return "USER_NOT_FOUND", None, None

    stored_password = user[1]
    attempts = user[2]
    is_blocked = user[3]

    # 🔒 ACCOUNT BLOCKED
    if is_blocked == 1:
        conn.close()
        return "BLOCKED", None, None

    # ✅ PASSWORD CORRECT
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        cursor.execute("UPDATE users SET attempts=0 WHERE username=?", (username,))
        conn.commit()
        conn.close()

        return "TOTP_REQUIRED", None, username

    # ❌ WRONG PASSWORD
    attempts += 1

    if attempts >= 3:
        cursor.execute("""
            UPDATE users
            SET attempts=?, is_blocked=1
            WHERE username=?
        """, (attempts, username))

        conn.commit()
        conn.close()

        return "BLOCKED", None, None

    else:
        cursor.execute("""
            UPDATE users
            SET attempts=?
            WHERE username=?
        """, (attempts, username))

        conn.commit()
        conn.close()

        return f"INVALID_{attempts}", None, None