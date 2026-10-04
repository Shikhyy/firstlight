import logging

from firstlight import config
from firstlight.ai.client import call_ollama
from firstlight.ai.prompts import build_brief_prompt
from firstlight.connectors.base import RawItem
from firstlight.connectors.rss_news import RssConnector
from firstlight.delivery.fallback import build_fallback_brief
from firstlight.delivery.ntfy import send_ntfy_push

logger = logging.getLogger(__name__)


def run_pipeline(dry_run: bool = False, no_ai: bool = False):
    logger.info("Starting First Light pipeline")

    from firstlight.connectors.calendar_ics import CalendarConnector
    from firstlight.connectors.todos_md import TodosConnector
    from firstlight.pipeline.normalize import normalize_date
    from firstlight.pipeline.rank import compute_score, compute_urgency
    from firstlight.pipeline.seen import is_novel, mark_seen

    # 1. Fetch data
    rss_urls = config.SOURCES.get("rss", [])
    if not rss_urls:
        rss_urls = ["https://news.ycombinator.com/rss"]  # dummy default

    from firstlight.pipeline.fetcher import fetch_safely

    raw_items = []

    rss = RssConnector(urls=rss_urls)
    raw_items.extend(fetch_safely(rss))

    if config.SOURCES.get("calendar_ics"):
        cal = CalendarConnector()
        raw_items.extend(fetch_safely(cal))

    if config.SOURCES.get("todos_file"):
        todos = TodosConnector()
        raw_items.extend(fetch_safely(todos))

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

    # 2. Deduplicate Hackathons
    from firstlight.pipeline.dedupe import deduplicate_events

    hackathons_only = [
        i.model_dump()
        for i in raw_items
        if i.source not in ("rss", "calendar", "todos")
    ]
    deduped_hackathons_dicts = deduplicate_events(hackathons_only)

    # Re-build raw items list, keeping non-hackathons exactly as they were
    deduped_raw_items = [
        i for i in raw_items if i.source in ("rss", "calendar", "todos")
    ]
    for d in deduped_hackathons_dicts:
        deduped_raw_items.append(RawItem(**d))

    logger.info(f"After deduplication: {len(deduped_raw_items)} items")

    # 3. Normalize and rank
    from firstlight.pipeline.classify import classify_keywords
    from firstlight.pipeline.verdict import get_verdict

    processed = []
    for i, item in enumerate(deduped_raw_items):
        ref = f"{item.source}:{i}"

        # Determine raw date to use based on source type
        raw_date = None
        if item.source == "calendar":
            raw_date = item.start_text
        elif item.source == "todos":
            raw_date = item.deadline_text
        elif item.source == "rss":
            raw_date = item.raw.get("published")
        else:
            raw_date = item.deadline_text

        iso_date, _ = normalize_date(raw_date)
        urgency, countdown = compute_urgency(iso_date)

        novelty = 1.0 if is_novel(item.source, str(i)) else 0.4
        score = compute_score(urgency=urgency, novelty=novelty)

        if score >= 0:
            # Classification
            title = item.title
            desc = item.description or ""
            domains = classify_keywords(title, desc)

            # AI verdict for top/interesting items or we just do it for hackathons
            # To save tokens, only do it if score is high and it's a hackathon
            verdict = ""
            if (
                not dry_run
                and not no_ai
                and item.source not in ("rss", "calendar", "todos")
                and score > 0.3
            ):
                verdict = get_verdict(title, desc)

            processed.append(
                {
                    "ref": ref,
                    "title": title,
                    "description": desc,
                    "countdown_text": countdown,
                    "score": score,
                    "source": item.source,
                    "raw_id": str(i),
                    "domains": domains,
                    "verdict": verdict,
                }
            )

    # Sort by score desc
    processed.sort(key=lambda x: x["score"], reverse=True)

    # Take top 5
    top_items = processed[:5]

    # Mark as seen
    if not dry_run and not no_ai:
        for item in top_items:
            mark_seen(item["source"], item["raw_id"])

    # Clean up fields for AI
    items_for_ai = []
    for item in top_items:
        items_for_ai.append(
            {
                "ref": item["ref"],
                "title": item["title"],
                "description": item["description"],
                "countdown_text": item["countdown_text"],
            }
        )

    profile = config.PROFILE
    name = profile.get("name", "User")
    interests = profile.get("interests", [])

    sys_prompt, user_prompt = build_brief_prompt(name, interests, items_for_ai)

    if dry_run or no_ai:
        if no_ai:
            logger.info("Skipping AI call (--no-ai). Using fallback.")
        else:
            logger.info("[DRY RUN] Skipping AI call. Would send:")
            logger.info(sys_prompt)
            logger.info(user_prompt)
        summary = build_fallback_brief(items_for_ai)
    else:
        summary = call_ollama(sys_prompt, user_prompt)
        if not summary:
            logger.warning("AI failed. Using fallback.")
            summary = build_fallback_brief(items_for_ai)

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
        send_ntfy_push(title, body, items_for_ai)
        logger.info("Notification sent.")

    return summary
