"""Lưu phiên JSON trong SQLite; khóa theo phiên giữa các luồng server."""
import json
import os
import sqlite3
import threading
from contextlib import closing, contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get("LION_DB_PATH", Path(__file__).resolve().parents[1] / "sessions.sqlite3"))
_locks = {}
_locks_guard = threading.Lock()


def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT NOT NULL)")
    return conn


@contextmanager
def session_lock(session_id):
    with _locks_guard:
        lock = _locks.setdefault(session_id, threading.Lock())
    with lock:
        yield


def save(session):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT INTO sessions VALUES (?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now')) "
                     "ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
                     (session['id'], json.dumps(session, ensure_ascii=False)))


def load(session_id):
    with closing(_connect()) as conn, conn:
        row = conn.execute("SELECT data FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return json.loads(row[0]) if row else None
