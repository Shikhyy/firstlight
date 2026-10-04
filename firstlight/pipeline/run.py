import json
import logging
from datetime import datetime, timezone

from firstlight import config
from firstlight.ai.client import call_ollama
from firstlight.ai.prompts import build_brief_prompt
from firstlight.connectors.base import RawItem
from firstlight.connectors.rss_news import RssConnector
from firstlight.db import get_connection
from firstlight.delivery.fallback import build_fallback_brief
from firstlight.delivery.simplepush import send_push
from firstlight.pipeline.fetcher import fetch_safely
from firstlight.pipeline.sync import sync_items

logger = logging.getLogger(__name__)


def fetch_and_sync():
    """Phase 1: Fetch and Sync to DB."""
    rss_urls = config.SOURCES.get("rss", [])
    if not rss_urls:
        rss_urls = ["https://news.ycombinator.com/rss"]

    raw_items = []

    rss = RssConnector(urls=rss_urls)
    raw_items.extend(fetch_safely(rss))

    from firstlight.connectors.calendar_ics import CalendarConnector
    from firstlight.connectors.todos_md import TodosConnector

    if config.SOURCES.get("calendar_ics"):
        raw_items.extend(fetch_safely(CalendarConnector()))

    if config.SOURCES.get("todos_file"):
        raw_items.extend(fetch_safely(TodosConnector()))

    hackathon_sources = config.SOURCES.get("hackathons", [])
    if "dev" in hackathon_sources:
        from firstlight.connectors.hackathons.dev import DevChallengesConnector

        raw_items.extend(fetch_safely(DevChallengesConnector()))
    if "devpost" in hackathon_sources:
        from firstlight.connectors.hackathons.devpost import DevpostConnector

        raw_items.extend(fetch_safely(DevpostConnector()))
    if "mlh" in hackathon_sources:
        from firstlight.connectors.hackathons.mlh import MlhConnector

        raw_items.extend(fetch_safely(MlhConnector()))
    if "kaggle" in hackathon_sources:
        from firstlight.connectors.hackathons.kaggle import KaggleConnector

        raw_items.extend(fetch_safely(KaggleConnector()))
    if "web3_source" in hackathon_sources:
        from firstlight.connectors.hackathons.web3 import Web3Connector

        raw_items.extend(fetch_safely(Web3Connector()))

    logger.info(f"Fetched {len(raw_items)} items total across sources")

    # Deduplicate Hackathons
    from firstlight.pipeline.dedupe import deduplicate_events

    hackathons_only = [
        i.model_dump()
        for i in raw_items
        if i.source not in ("rss", "calendar", "todos")
    ]
    deduped_hackathons_dicts = deduplicate_events(hackathons_only)

    deduped_raw_items = [
        i for i in raw_items if i.source in ("rss", "calendar", "todos")
    ]
    for d in deduped_hackathons_dicts:
        deduped_raw_items.append(RawItem(**d))

    logger.info(f"After deduplication: {len(deduped_raw_items)} items")

    # Sync to DB
    sync_items(deduped_raw_items)


def process_events(dry_run: bool, no_ai: bool):
    """Phase 2: Classify and Verdict for open events."""
    from firstlight.pipeline.classify import classify_keywords
    from firstlight.pipeline.verdict import get_verdict

    with get_connection() as conn:
        events = conn.execute(
            "SELECT id, title, description, domains_json, verdict_json FROM events WHERE status = 'open'"
        ).fetchall()
        for row in events:
            # We only classify if not done
            domains = json.loads(row["domains_json"]) if row["domains_json"] else []
            if not domains:
                domains = classify_keywords(row["title"], row["description"] or "")

            verdict_json = row["verdict_json"]
            if not verdict_json and not dry_run and not no_ai:
                verdict_json = get_verdict(row["title"], row["description"] or "")

            conn.execute(
                "UPDATE events SET domains_json = ?, verdict_json = ? WHERE id = ?",
                (json.dumps(domains), verdict_json, row["id"]),
            )
        conn.commit()


def rank_and_generate_brief(dry_run: bool, no_ai: bool):
    """Phase 3: Rank everything in DB, select top, generate brief, and send."""
    from firstlight.pipeline.normalize import normalize_date
    from firstlight.pipeline.rank import compute_score, compute_urgency
    from firstlight.pipeline.seen import is_novel, mark_seen

    processed = []

    with get_connection() as conn:
        # Get Events
        events = conn.execute(
            "SELECT id, title, description, deadline_at FROM events WHERE status = 'open'"
        ).fetchall()
        for row in events:
            iso_date, _ = normalize_date(row["deadline_at"])
            urgency, countdown = compute_urgency(iso_date)
            score = compute_score(
                urgency=urgency,
                novelty=1.0 if is_novel("event", str(row["id"])) else 0.4,
            )
            if score >= 0:
                processed.append(
                    {
                        "ref": f"event:{row['id']}",
                        "title": row["title"],
                        "description": row["description"] or "",
                        "countdown_text": countdown,
                        "score": score,
                        "item_type": "event",
                        "item_ref": row["id"],
                    }
                )

        # Get News (assume last 24h or all for now)
        news = conn.execute(
            "SELECT id, title, url, published_at FROM news_items"
        ).fetchall()
        for row in news:
            iso_date, _ = normalize_date(row["published_at"])
            urgency, countdown = compute_urgency(iso_date)
            score = compute_score(
                urgency=urgency,
                novelty=1.0 if is_novel("news", str(row["id"])) else 0.4,
            )
            if score >= 0:
                processed.append(
                    {
                        "ref": f"news:{row['id']}",
                        "title": row["title"],
                        "description": "",
                        "countdown_text": countdown,
                        "score": score,
                        "item_type": "news",
                        "item_ref": row["id"],
                    }
                )

        # Get Calendar
        cal = conn.execute("SELECT id, title, start_at FROM calendar_items").fetchall()
        for row in cal:
            iso_date, _ = normalize_date(row["start_at"])
            urgency, countdown = compute_urgency(iso_date)
            score = compute_score(
                urgency=urgency,
                novelty=1.0 if is_novel("calendar", str(row["id"])) else 0.4,
            )
            if score >= 0:
                processed.append(
                    {
                        "ref": f"calendar:{row['id']}",
                        "title": row["title"],
                        "description": "",
                        "countdown_text": countdown,
                        "score": score,
                        "item_type": "calendar",
                        "item_ref": row["id"],
                    }
                )

        # Get Todos
        todos = conn.execute(
            "SELECT id, title, due_at FROM todos WHERE status = 'open'"
        ).fetchall()
        for row in todos:
            iso_date, _ = normalize_date(row["due_at"])
            urgency, countdown = compute_urgency(iso_date)
            score = compute_score(
                urgency=urgency,
                novelty=1.0 if is_novel("todo", str(row["id"])) else 0.4,
            )
            if score >= 0:
                processed.append(
                    {
                        "ref": f"todo:{row['id']}",
                        "title": row["title"],
                        "description": "",
                        "countdown_text": countdown,
                        "score": score,
                        "item_type": "todo",
                        "item_ref": row["id"],
                    }
                )

    processed.sort(key=lambda x: x["score"], reverse=True)
    top_items = processed[:5]

    # Clean up fields for AI
    items_for_ai = [
        {
            "ref": i["ref"],
            "title": i["title"],
            "description": i["description"],
            "countdown_text": i["countdown_text"],
        }
        for i in top_items
    ]

    profile = config.PROFILE
    name = profile.get("name", "User")
    interests = profile.get("interests", [])

    sys_prompt, user_prompt = build_brief_prompt(name, interests, items_for_ai)

    if dry_run or no_ai:
        if no_ai:
            logger.info("Skipping AI call (--no-ai). Using fallback.")
        else:
            logger.info("[DRY RUN] Skipping AI call. Would send prompt:")
        summary = build_fallback_brief(items_for_ai)
    else:
        summary = call_ollama(sys_prompt, user_prompt)
        if not summary:
            logger.warning("AI failed. Using fallback.")
            summary = build_fallback_brief(items_for_ai)

    now_iso = datetime.now(timezone.utc).isoformat()
    brief_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if summary.quiet_day:
        title = "Quiet day ahead"
        body = "Nothing urgent."
    else:
        title = summary.title
        body_lines = [f"• {item.headline} ({item.why})" for item in summary.items]
        body = "\n".join(body_lines)

    if dry_run:
        logger.info(f"[DRY RUN] Would send notification. Title: {title}\nBody:\n{body}")
    else:
        # Mark as seen
        for item in top_items:
            mark_seen(item["item_type"], str(item["item_ref"]))

        # Save to DB
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT OR REPLACE INTO briefs (brief_date, title, body, mode, created_at) VALUES (?, ?, ?, ?, ?)",
                (brief_date, title, body, "fallback" if no_ai else "ai", now_iso),
            )
            brief_id = cursor.lastrowid

            # For each item returned by AI, find matching top_item
            if not summary.quiet_day:
                for idx, ai_item in enumerate(summary.items):
                    match = next(
                        (i for i in top_items if i["ref"] == ai_item.ref), None
                    )
                    if match:
                        conn.execute(
                            "INSERT INTO brief_items (brief_id, item_type, item_ref, rank, score, headline, why_line) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                brief_id,
                                match["item_type"],
                                match["item_ref"],
                                idx + 1,
                                match["score"],
                                ai_item.headline,
                                ai_item.why,
                            ),
                        )
            conn.commit()

        send_push(title, body, items_for_ai)
        logger.info("Notification sent and DB updated.")

    return summary


def run_pipeline(dry_run: bool = False, no_ai: bool = False):
    fetch_and_sync()
    process_events(dry_run, no_ai)
    return rank_and_generate_brief(dry_run, no_ai)
