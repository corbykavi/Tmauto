# db.py
import aiosqlite
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger("db")

async def init_db(db_path="tmauto.db"):
    db = await aiosqlite.connect(db_path)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        msg_id TEXT UNIQUE,           -- chat_id:message_id
        chat_id INTEGER,
        message_id INTEGER,
        file_name TEXT,
        file_size INTEGER,
        date_utc TEXT,                -- iso
        title TEXT,
        year INTEGER,
        season INTEGER,
        episode TEXT,
        language TEXT,
        quality TEXT,
        parsed_at TEXT,
        group_tag TEXT                -- computed grouping key
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS checkpoints (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        value TEXT
    )
    """)
    await db.commit()
    return db

async def set_checkpoint(db, name, value):
    await db.execute("INSERT OR REPLACE INTO checkpoints (name, value) VALUES (?, ?)", (name, value))
    await db.commit()

async def get_checkpoint(db, name):
    cur = await db.execute("SELECT value FROM checkpoints WHERE name = ?", (name,))
    row = await cur.fetchone()
    return row[0] if row else None

def msg_key(chat_id, message_id):
    return f"{chat_id}:{message_id}"