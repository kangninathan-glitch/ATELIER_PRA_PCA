import os
import sqlite3
import time
from datetime import datetime
from flask import Flask, jsonify, request

DB_PATH = os.getenv("DB_PATH", "/data/app.db")

app = Flask(__name__)

# ---------- DB helpers ----------
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------- Routes ----------

@app.get("/")
def hello():
    init_db()
    return jsonify(status="Bonjour tout le monde !")

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/count")
def count():
    conn = get_conn()
    cur = conn.execute("SELECT COUNT(*) FROM events")
    n = cur.fetchone()[0]
    conn.close()
    return jsonify(count=n)

@app.get("/status")
def status():
    # COUNT messages
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()

    # BACKUP info
    backup_path = "/backup"

    last_backup_file = None
    backup_age_seconds = None

    if os.path.exists(backup_path):
        files = sorted(os.listdir(backup_path), reverse=True)
        if files:
            last_backup_file = files[0]
            full_path = os.path.join(backup_path, last_backup_file)
            backup_time = os.path.getmtime(full_path)
            backup_age_seconds = int(time.time() - backup_time)

    return jsonify({
        "count": count,
        "last_backup_file": last_backup_file,
        "backup_age_seconds": backup_age_seconds
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)