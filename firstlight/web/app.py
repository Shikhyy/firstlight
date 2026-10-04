import sqlite3

from flask import Flask, g, render_template

from firstlight import config
from firstlight.db import DB_PATH

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
@app.route("/brief")
def brief():
    db = get_db()
    # Get latest brief
    brief_row = db.execute(
        "SELECT * FROM briefs ORDER BY created_at DESC LIMIT 1"
    ).fetchone()

    # Get todos
    todos = db.execute(
        "SELECT * FROM todos WHERE status='open' ORDER BY due_at ASC"
    ).fetchall()

    # Get items for the brief
    brief_items = []
    if brief_row:
        brief_items = db.execute(
            "SELECT * FROM brief_items WHERE brief_id=? ORDER BY rank ASC",
            (brief_row["id"],),
        ).fetchall()

    return render_template(
        "brief.html",
        brief=brief_row,
        items=brief_items,
        todos=todos,
        profile=config.PROFILE,
    )


@app.route("/radar")
def radar():
    db = get_db()
    # Get open hackathons
    events = db.execute(
        "SELECT * FROM events WHERE status='open' ORDER BY deadline_at ASC"
    ).fetchall()

    # Get domains for filters
    all_domains = set()
    import json

    parsed_events = []
    for e in events:
        d = dict(e)
        d["domains"] = json.loads(d["domains_json"]) if d["domains_json"] else []
        for dom in d["domains"]:
            all_domains.add(dom)

        # calculate urgency width
        from firstlight.pipeline.normalize import normalize_date
        from firstlight.pipeline.rank import compute_urgency

        iso, _ = normalize_date(d["deadline_at"])
        urgency, countdown = compute_urgency(iso)
        d["countdown_text"] = countdown
        d["urgency_pct"] = min(100, max(0, int(urgency * 100)))

        parsed_events.append(d)

    # Get health status
    sources = db.execute(
        "SELECT source, MAX(started_at) as last_run, ok FROM source_runs GROUP BY source"
    ).fetchall()
    health_ok = all(s["ok"] for s in sources)

    return render_template(
        "radar.html",
        events=parsed_events,
        domains=sorted(all_domains),
        health_ok=health_ok,
    )


@app.route("/health")
def health():
    db = get_db()
    runs = db.execute(
        "SELECT * FROM source_runs ORDER BY started_at DESC LIMIT 50"
    ).fetchall()
    return render_template("health.html", runs=runs)


def create_app():
    return app
