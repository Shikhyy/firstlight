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

        # Get actual URL from event_sources
        source_row = db.execute(
            "SELECT url FROM event_sources WHERE event_id = ? LIMIT 1", (e["id"],)
        ).fetchone()
        d["url"] = source_row["url"] if source_row else d["canonical_key"]

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


@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    import os

    import yaml
    from flask import redirect, request, url_for

    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "config.yaml"
    )

    if request.method == "POST":
        name = request.form.get("name")
        interests = [
            i.strip() for i in request.form.get("interests", "").split(",") if i.strip()
        ]
        model = request.form.get("model", "gemma:2b")
        hf_token = request.form.get("hf_token", "")
        elevenlabs_key = request.form.get("elevenlabs_key", "")

        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        cfg["profile"]["name"] = name
        cfg["profile"]["interests"] = interests
        cfg["ai"]["model"] = model

        if "integrations" not in cfg:
            cfg["integrations"] = {}
        cfg["integrations"]["hf_token"] = hf_token
        cfg["integrations"]["elevenlabs_api_key"] = elevenlabs_key

        with open(config_path, "w") as f:
            yaml.dump(cfg, f, sort_keys=False)

        from firstlight import config

        config.PROFILE.name = name
        config.PROFILE.interests = interests
        config.AI_MODEL = model

        return redirect(url_for("brief"))

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    return render_template("onboarding.html", cfg=cfg)


@app.route("/api/vapidPublicKey")
def get_vapid_key():
    import json
    import os

    vapid_file = os.path.join("data", "vapid.json")
    if os.path.exists(vapid_file):
        with open(vapid_file) as f:
            v = json.load(f)
            return {"publicKey": v["public_key"]}
    return {"publicKey": ""}


@app.route("/api/todos/<int:todo_id>/done", methods=["POST"])
def mark_todo_done(todo_id):
    db = get_db()
    db.execute("UPDATE todos SET status='done' WHERE id=?", (todo_id,))
    db.commit()
    return {"status": "ok"}


@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    import json
    from datetime import datetime, timezone

    from flask import request

    subscription = request.json
    db = get_db()
    db.execute(
        "INSERT INTO webpush_subscriptions (subscription_json, created_at) VALUES (?, ?)",
        (json.dumps(subscription), datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return {"status": "ok"}


def create_app():
    return app
