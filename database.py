import sqlite3
from pathlib import Path

class AlertDatabase:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS alerts (
                message_key TEXT PRIMARY KEY, subject TEXT NOT NULL, sender TEXT NOT NULL,
                email_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sent_at TEXT)""")
    def _connect(self):
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        return c
    def was_sent(self, key):
        with self._connect() as c:
            r = c.execute("SELECT status FROM alerts WHERE message_key=?", (key,)).fetchone()
            return bool(r and r["status"] == "sent")
    def record_pending(self, item):
        with self._connect() as c:
            c.execute("""INSERT INTO alerts(message_key,subject,sender,email_date,status)
                VALUES(?,?,?,?, 'pending') ON CONFLICT(message_key) DO UPDATE SET
                subject=excluded.subject,sender=excluded.sender,email_date=excluded.email_date""",
                (item["message_key"], item["subject"], item["sender"], item["date"]))
    def mark_sent(self, key):
        with self._connect() as c:
            c.execute("UPDATE alerts SET status='sent',sent_at=CURRENT_TIMESTAMP WHERE message_key=?", (key,))
