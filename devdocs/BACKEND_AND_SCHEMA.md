# First Light: Backend and Schema

---

## 1. Repository layout

```
first-light/
├── AGENTS.md
├── README.md
├── config.yaml                # friend profile, interests, sources, schedule
├── .env.example               # NTFY_TOPIC, NTFY_BASE_URL, ACTION_TOKEN, ICS_URL, OLLAMA_URL, OLLAMA_MODEL
├── requirements.txt
├── firstlight/
│   ├── __main__.py            # CLI: run, serve, init-db
│   ├── config.py              # loads config.yaml + .env
│   ├── db.py                  # SQLite connection, migrations
│   ├── models.py              # pydantic models
│   ├── connectors/
│   │   ├── base.py            # Connector interface
│   │   ├── calendar_ics.py
│   │   ├── todos_md.py
│   │   ├── rss_news.py
│   │   ├── weather.py
│   │   └── hackathons/        # one file per platform
│   ├── pipeline/
│   │   ├── normalize.py       # date parsing, UTC, validation
│   │   ├── dedupe.py
│   │   ├── classify.py
│   │   ├── rank.py
│   │   └── run.py             # orchestrates the 8 stages
│   ├── ai/
│   │   ├── client.py          # Ollama HTTP client
│   │   ├── prompts.py
│   │   └── schemas.py         # pydantic output schemas
│   ├── delivery/
│   │   ├── ntfy.py
│   │   └── fallback.py        # non-AI brief builder
│   └── web/
│       ├── app.py             # Flask routes
│       ├── templates/
│       └── static/
├── data/                      # git-ignored: firstlight.db, todos.md
├── tests/
│   ├── fixtures/              # saved source responses
│   └── test_*.py
└── logs/
```

## 2. Config (`config.yaml`)

```yaml
profile:
  name: "[FRIEND NAME]"
  timezone: "Asia/Kolkata"
  wake_time: "06:30"
  country: "IN"
  is_student: true
  interests: [ai, ml, web3]        # taxonomy values
  min_prize_usd: 0
  online_only: false

schedule:
  run_at: "05:30"
  quiet_days: []                   # e.g. ["Sun"]

sources:
  calendar_ics: true
  todos_file: "data/todos.md"
  rss:
    - https://example.com/feed.xml # replace with chosen feeds
  hackathons: [dev, devpost, mlh, kaggle, web3_source]

ai:
  model: "gemma3:4b"
  top_n_for_model: 5
  timeout_s: 60
```

## 3. Connector interface

```python
# firstlight/connectors/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel


class RawItem(BaseModel):
    source: str
    title: str
    url: str
    raw: dict
    # optional, filled when the source provides them
    deadline_text: str | None = None
    start_text: str | None = None
    description: str | None = None


class Connector(ABC):
    name: str  # "devpost"
    refresh_hours: int = 24  # skip if fetched more recently
    timeout_s: int = 20

    @abstractmethod
    def fetch(self) -> list[RawItem]: ...
```

Rules:
- A connector only fetches and returns `RawItem`s. Parsing dates and scoring happen elsewhere.
- Raise on failure; the pipeline catches it, writes a `source_runs` row, and continues.
- Use official API, RSS or ICS where possible. Respect `robots.txt`, rate-limit, set a User-Agent.
- Every connector has a test using a saved fixture in `tests/fixtures/<name>.*`.

## 4. SQLite schema

```sql
CREATE TABLE profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT, timezone TEXT DEFAULT 'Asia/Kolkata',
  wake_time TEXT DEFAULT '06:30', country TEXT,
  is_student INTEGER DEFAULT 0, interests_json TEXT
);

CREATE TABLE events (                       -- hackathons / challenges
  id INTEGER PRIMARY KEY,
  canonical_key TEXT UNIQUE NOT NULL,       -- normalized URL or title+date hash
  title TEXT NOT NULL, organizer TEXT, description TEXT,
  domains_json TEXT, tags_json TEXT,
  start_at TEXT, deadline_at TEXT,          -- ISO 8601 UTC
  mode TEXT CHECK (mode IN ('online','in_person','hybrid','unknown')) DEFAULT 'unknown',
  location TEXT, prize_text TEXT, prize_usd REAL,
  team_size_max INTEGER, eligibility_text TEXT,
  status TEXT CHECK (status IN ('upcoming','open','closing','ended')) DEFAULT 'upcoming',
  confidence REAL DEFAULT 1.0,              -- low when dates uncertain
  verdict_json TEXT,                        -- {effort, fit, verdict, red_flags}
  first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
);

CREATE TABLE event_sources (                -- one event, many platforms
  id INTEGER PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  platform TEXT NOT NULL, url TEXT NOT NULL,
  raw_json TEXT, fetched_at TEXT NOT NULL,
  UNIQUE (platform, url)
);

CREATE TABLE todos (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL, due_at TEXT, priority INTEGER DEFAULT 2,
  status TEXT CHECK (status IN ('open','done')) DEFAULT 'open',
  snoozed_until TEXT, source TEXT DEFAULT 'markdown',
  created_at TEXT NOT NULL
);

CREATE TABLE calendar_items (
  id INTEGER PRIMARY KEY,
  uid TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
  start_at TEXT NOT NULL, end_at TEXT, location TEXT
);

CREATE TABLE news_items (
  id INTEGER PRIMARY KEY,
  url TEXT UNIQUE NOT NULL, title TEXT NOT NULL, source TEXT,
  published_at TEXT, summary TEXT, cluster_id INTEGER,
  fetched_at TEXT NOT NULL
);

CREATE TABLE briefs (
  id INTEGER PRIMARY KEY,
  brief_date TEXT UNIQUE NOT NULL,          -- local date, YYYY-MM-DD
  title TEXT NOT NULL, body TEXT NOT NULL,
  mode TEXT CHECK (mode IN ('ai','fallback')) NOT NULL,
  model TEXT, latency_ms INTEGER, tokens_in INTEGER, tokens_out INTEGER,
  created_at TEXT NOT NULL, sent_at TEXT
);

CREATE TABLE brief_items (
  id INTEGER PRIMARY KEY,
  brief_id INTEGER NOT NULL REFERENCES briefs(id) ON DELETE CASCADE,
  item_type TEXT CHECK (item_type IN ('event','todo','news','calendar')) NOT NULL,
  item_ref INTEGER NOT NULL, rank INTEGER NOT NULL, score REAL,
  headline TEXT, why_line TEXT
);

CREATE TABLE feedback (                     -- P2
  id INTEGER PRIMARY KEY,
  brief_item_id INTEGER NOT NULL REFERENCES brief_items(id) ON DELETE CASCADE,
  value INTEGER CHECK (value IN (-1, 1)) NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE interest_weights (             -- P2
  domain TEXT PRIMARY KEY, weight REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE seen_items (
  item_type TEXT NOT NULL, item_ref INTEGER NOT NULL, shown_at TEXT NOT NULL,
  PRIMARY KEY (item_type, item_ref)
);

CREATE TABLE source_runs (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
  ok INTEGER NOT NULL, items_found INTEGER DEFAULT 0, error TEXT
);

CREATE INDEX idx_events_deadline ON events(deadline_at);
CREATE INDEX idx_todos_due ON todos(due_at);
CREATE INDEX idx_source_runs_source ON source_runs(source, started_at);
```

Store all timestamps as ISO 8601 UTC. Convert to `Asia/Kolkata` only at display time.

## 5. Normalization and dedup

**Normalize:** parse with `dateutil`, convert to UTC. If parsing fails or the result is implausible (in the past by years, or far future), set `confidence < 0.5` and exclude from the notification.

**Dedup order:**
1. Same canonical URL (strip tracking params, trailing slashes, lowercase host).
2. Fuzzy title match (`rapidfuzz`, threshold about 90) **and** overlapping date range.
3. *(optional)* embedding similarity above a high threshold.

On match: merge into one `events` row; add each source URL to `event_sources`; keep the most complete fields.

## 6. Ranking

```
score = 0.40*urgency + 0.30*relevance + 0.15*eligibility
      + 0.10*effort_reward + 0.05*novelty
final = score * feedback_multiplier           # P2, default 1.0
```

| Factor | Definition |
|---|---|
| urgency | deadline within 6h = 1.0; 24h = 0.85; 3d = 0.6; 7d = 0.35; later = 0.1; ended = excluded |
| relevance | overlap of event domains with profile interests, weighted by `interest_weights` |
| eligibility | 1.0 if country/student/team rules fit, 0.3 if unknown, 0 if clearly ineligible |
| effort_reward | heuristic from prize and time to deadline (keep simple, 0 to 1) |
| novelty | 1.0 if not in `seen_items`, 0.4 if seen before |

Todos: urgency from `due_at` and `priority`. Calendar items: urgency from start time. News: relevance and recency. All item types are ranked on the same 0 to 1 scale; take the top N.

## 7. AI contract

### 7.1 Brief summary

**Input (JSON, built by code):** profile name and interests, the top N items each with `ref` (e.g. `event:12`), `type`, `title`, and **pre-computed** `countdown_text` (e.g. "closes in 6h").

**System prompt (core rules):**
- Use only the facts provided. Never invent or calculate dates or times; copy `countdown_text` exactly.
- `title`: max 60 characters, summarizes the day.
- Each `headline`: max 50 characters. Each `why`: one sentence, max 120 characters, tied to the person's interests.
- If nothing is urgent, set `quiet_day` to true.
- Output only valid JSON.

**Output schema:**
```json
{
  "title": "string",
  "quiet_day": false,
  "items": [
    { "ref": "event:12", "headline": "string", "why": "string" }
  ]
}
```

Validate with pydantic. Reject if a `ref` was not in the input. One retry on failure, then fallback mode.

### 7.2 "Should I enter?" verdict (events only, cached in `events.verdict_json`)

**Input:** event title, rules/description text (truncated), profile interests and skills.

**Output:**
```json
{
  "effort": "low|medium|high",
  "fit": "low|medium|high",
  "verdict": "max 25 words",
  "red_flags": ["string"]
}
```

Always present as a suggestion in the UI.

### 7.3 Classification (only for events keyword rules couldn't classify)

Output: `{"domains": ["ai", "web3"]}` using only the fixed taxonomy: `ai, ml, web3, security, web, hardware, opensource, gamedev, social_good`.

## 8. Fallback brief

Used when Ollama is down, times out, or returns invalid JSON twice.

- Title: `"{n} deadline(s) today"` or `"Quiet day"`.
- Body: top 3 ranked items as `"{title}: {countdown_text}"`.
- Saved with `mode = 'fallback'`.

## 9. ntfy delivery

```python
requests.post(
    f"{NTFY_BASE_URL}/{NTFY_TOPIC}",
    data=body.encode("utf-8"),
    headers={
        "Title": title,
        "Click": f"{PUBLIC_URL}/brief",
        "Actions": (
            f"http, Done, {PUBLIC_URL}/api/todos/{todo_id}/done?token={ACTION_TOKEN}, method=POST; "
            f"http, Snooze 1h, {PUBLIC_URL}/api/todos/{todo_id}/snooze?token={ACTION_TOKEN}, method=POST; "
            f"view, Open, {PUBLIC_URL}/brief"
        ),
    },
    timeout=10,
)
```

Check the ntfy docs for exact header and action syntax and non-ASCII header handling. Retry up to 3 times with backoff.

## 10. HTTP API (Flask)

| Method | Path | Purpose |
|---|---|---|
| GET | `/brief` | Today's brief page |
| GET | `/radar` | Hackathon radar page; query: `domain`, `online`, `max_days` |
| GET | `/health` | Source health table |
| GET | `/api/events` | JSON list of events with filters |
| POST | `/api/todos/<id>/done?token=` | Mark done |
| POST | `/api/todos/<id>/snooze?token=` | Snooze 1h |
| POST | `/api/feedback` | P2: body `{brief_item_id, value}` |

Security: mutating endpoints require `ACTION_TOKEN` (constant-time compare). No user accounts. Keep the server private or behind the token.

## 11. CLI

```
python -m firstlight init-db
python -m firstlight run              # full pipeline + send
python -m firstlight run --dry-run    # full pipeline, print instead of sending
python -m firstlight run --no-ai      # force fallback mode
python -m firstlight serve            # Flask app
```

## 12. Observability

- Every connector run writes a `source_runs` row.
- Every brief records `mode`, `model`, `latency_ms`, token counts.
- Logs go to `logs/`; one line per stage with duration.

## 13. Testing

- Connector tests run against saved fixtures (no network in tests).
- Unit tests for date normalization, dedup, scoring.
- AI tests use a mocked Ollama client plus malformed-JSON cases to prove fallback works.
- One end-to-end test: fixtures in, brief out, `--dry-run`.
