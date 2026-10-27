import os
import secrets
import string
import sqlite3
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "getkey.db")
KEY_HOURS = int(os.environ.get("KEY_HOURS", "24"))

def now_utc():
    return datetime.now(timezone.utc)

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_value TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0
            )
        """)

def make_key():
    alphabet = string.ascii_uppercase + string.digits
    chunks = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3)]
    return "REAL-" + "-".join(chunks)

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/getkey")
def get_key():
    expires = now_utc() + timedelta(hours=KEY_HOURS)
    created_at = now_utc().isoformat()
    expires_at = expires.isoformat()

    with connect_db() as conn:
        for _ in range(5):
            key_value = make_key()
            try:
                conn.execute(
                    "INSERT INTO keys (key_value, created_at, expires_at) VALUES (?, ?, ?)",
                    (key_value, created_at, expires_at)
                )
                return jsonify({
                    "ok": True,
                    "key": key_value,
                    "expires_at": expires_at,
                    "message": "สร้างคีย์สำเร็จ"
                }), 201
            except sqlite3.IntegrityError:
                continue

    return jsonify({"ok": False, "message": "สร้างคีย์ไม่สำเร็จ กรุณาลองใหม่"}), 500

@app.post("/api/verify")
def verify_key():
    data = request.get_json(silent=True) or {}
    key_value = str(data.get("key", "")).strip().upper()
    if not key_value:
        return jsonify({"ok": False, "valid": False, "message": "กรุณากรอกคีย์"}), 400

    with connect_db() as conn:
        row = conn.execute(
            "SELECT key_value, expires_at, revoked FROM keys WHERE key_value = ?",
            (key_value,)
        ).fetchone()

    if row is None:
        return jsonify({"ok": True, "valid": False, "message": "ไม่พบคีย์นี้"}), 200
    if row["revoked"]:
        return jsonify({"ok": True, "valid": False, "message": "คีย์ถูกยกเลิกแล้ว"}), 200

    try:
        expiry = datetime.fromisoformat(row["expires_at"])
    except ValueError:
        return jsonify({"ok": False, "valid": False, "message": "ข้อมูลวันหมดอายุไม่ถูกต้อง"}), 500

    if expiry <= now_utc():
        return jsonify({"ok": True, "valid": False, "message": "คีย์หมดอายุแล้ว"}), 200

    return jsonify({
        "ok": True,
        "valid": True,
        "message": "คีย์ใช้งานได้",
        "expires_at": row["expires_at"]
    }), 200

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "REALMAX GetKey"})

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
