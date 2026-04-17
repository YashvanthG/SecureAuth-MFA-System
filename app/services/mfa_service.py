import pyotp
import sqlite3

def verify_totp(username, user_code):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT totp_secret FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    conn.close()

    if not result or not result[0]:
        return False

    secret = result[0]

    totp = pyotp.TOTP(secret)

    # 🔥 IMPORTANT FIX → allow slight time delay
    return totp.verify(user_code, valid_window=1)