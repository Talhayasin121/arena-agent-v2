import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("ARENA_DB_PATH", "arena.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            goal TEXT NOT NULL,
            status TEXT NOT NULL,
            report TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_run(run_id: str, goal: str, status: str, created_at: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO runs (run_id, goal, status, created_at) VALUES (?, ?, ?, ?)",
        (run_id, goal, status, created_at)
    )
    conn.commit()
    conn.close()

def update_run_status(run_id: str, status: str, report: str = None):
    conn = get_db()
    cursor = conn.cursor()
    if report:
        cursor.execute(
            "UPDATE runs SET status = ?, report = ? WHERE run_id = ?",
            (status, report, run_id)
        )
    else:
        cursor.execute(
            "UPDATE runs SET status = ? WHERE run_id = ?",
            (status, run_id)
        )
    conn.commit()
    conn.close()

def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def list_runs(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_run(run_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
    conn.commit()
    conn.close()
