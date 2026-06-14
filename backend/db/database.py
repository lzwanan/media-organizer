"""数据库 — SQLite 连接与初始化"""

import sqlite3
from datetime import datetime
from pathlib import Path

from backend.config_manager import ConfigManager


def get_db_path() -> Path:
    return ConfigManager.instance().config_dir / "media_organizer.db"


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            root_path TEXT NOT NULL,
            total_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            skipped_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            history_id INTEGER NOT NULL,
            original_path TEXT NOT NULL,
            new_path TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            FOREIGN KEY (history_id) REFERENCES history(id)
        );
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_pattern TEXT NOT NULL UNIQUE,
            normalized_title TEXT NOT NULL,
            title_zh TEXT,
            title_en TEXT,
            year INTEGER,
            media_type TEXT NOT NULL,
            use_count INTEGER DEFAULT 1,
            last_used DATETIME
        );
        CREATE TABLE IF NOT EXISTS tmdb_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            query_hash TEXT UNIQUE NOT NULL,
            result_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def record_history(
    root_path: str,
    total: int, success: int, failed: int, skipped: int,
    change_items: list[dict],
) -> int:
    """记录一次整理操作，返回 history_id"""
    conn = get_connection()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO history (timestamp, root_path, total_count, success_count, failed_count, skipped_count) VALUES (?, ?, ?, ?, ?, ?)",
        (now, root_path, total, success, failed, skipped),
    )
    history_id = cur.lastrowid
    for item in change_items:
        conn.execute(
            "INSERT INTO changes (history_id, original_path, new_path, status, error_message) VALUES (?, ?, ?, ?, ?)",
            (history_id, item.get("path", ""), item.get("target", ""), item.get("status", ""), item.get("error")),
        )
    conn.commit()
    conn.close()
    return history_id


def get_history_list(limit: int = 20) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_detail(history_id: int) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM history WHERE id = ?", (history_id,)).fetchone()
    if not row:
        conn.close()
        return {}
    changes = conn.execute(
        "SELECT * FROM changes WHERE history_id = ?", (history_id,)
    ).fetchall()
    conn.close()
    return {**dict(row), "changes": [dict(c) for c in changes]}
