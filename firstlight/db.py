import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data") / "firstlight.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT, timezone TEXT DEFAULT 'Asia/Kolkata',
  wake_time TEXT DEFAULT '06:30', country TEXT,
  is_student INTEGER DEFAULT 0, interests_json TEXT
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  canonical_key TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL, organizer TEXT, description TEXT,
  domains_json TEXT, tags_json TEXT,
  start_at TEXT, deadline_at TEXT,
  mode TEXT CHECK (mode IN ('online','in_person','hybrid','unknown')) DEFAULT 'unknown',
  location TEXT, prize_text TEXT, prize_usd REAL,
  team_size_max INTEGER, eligibility_text TEXT,
  status TEXT CHECK (status IN ('upcoming','open','closing','ended')) DEFAULT 'upcoming',
  confidence REAL DEFAULT 1.0,
  verdict_json TEXT,
  first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_sources (
  id INTEGER PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  platform TEXT NOT NULL, url TEXT NOT NULL,
  raw_json TEXT, fetched_at TEXT NOT NULL,
  UNIQUE (platform, url)
);

CREATE TABLE IF NOT EXISTS todos (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL, due_at TEXT, priority INTEGER DEFAULT 2,
  status TEXT CHECK (status IN ('open','done')) DEFAULT 'open',
  snoozed_until TEXT, source TEXT DEFAULT 'markdown',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS calendar_items (
  id INTEGER PRIMARY KEY,
  uid TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
  start_at TEXT NOT NULL, end_at TEXT, location TEXT
);

CREATE TABLE IF NOT EXISTS news_items (
  id INTEGER PRIMARY KEY,
  url TEXT UNIQUE NOT NULL, title TEXT NOT NULL, source TEXT,
  published_at TEXT, summary TEXT, cluster_id INTEGER,
  fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS briefs (
  id INTEGER PRIMARY KEY,
  brief_date TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL, body TEXT NOT NULL,
  mode TEXT CHECK (mode IN ('ai','fallback')) NOT NULL,
  model TEXT, latency_ms INTEGER, tokens_in INTEGER, tokens_out INTEGER,
  created_at TEXT NOT NULL, sent_at TEXT
);

CREATE TABLE IF NOT EXISTS brief_items (
  id INTEGER PRIMARY KEY,
  brief_id INTEGER NOT NULL REFERENCES briefs(id) ON DELETE CASCADE,
  item_type TEXT CHECK (item_type IN ('event','todo','news','calendar')) NOT NULL,
  item_ref INTEGER NOT NULL, rank INTEGER NOT NULL, score REAL,
  headline TEXT, why_line TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY,
  brief_item_id INTEGER NOT NULL REFERENCES brief_items(id) ON DELETE CASCADE,
  value INTEGER CHECK (value IN (-1, 1)) NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interest_weights (
  domain TEXT PRIMARY KEY, weight REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS seen_items (
  item_type TEXT NOT NULL, item_ref INTEGER NOT NULL, shown_at TEXT NOT NULL,
  PRIMARY KEY (item_type, item_ref)
);

CREATE TABLE IF NOT EXISTS webpush_subscriptions (
  id INTEGER PRIMARY KEY,
  subscription_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_runs (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
  ok INTEGER NOT NULL, items_found INTEGER DEFAULT 0, error TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_deadline ON events(deadline_at);
CREATE INDEX IF NOT EXISTS idx_todos_due ON todos(due_at);
CREATE INDEX IF NOT EXISTS idx_source_runs_source ON source_runs(source, started_at);
"""


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    logger.info("Initializing database...")
    with get_connection() as conn:
        conn.executescript(SCHEMA)
    logger.info("Database initialized.")
