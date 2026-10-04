import logging

from firstlight import config
from firstlight.ai.client import call_ollama
from firstlight.ai.prompts import build_brief_prompt
from firstlight.connectors.rss_news import RssConnector
from firstlight.delivery.fallback import build_fallback_brief
from firstlight.delivery.ntfy import send_ntfy_push

logger = logging.getLogger(__name__)


def run_pipeline(dry_run: bool = False):
    logger.info("Starting First Light pipeline")

    # 1. Fetch data
    # In Phase 1, just one RSS source
    rss_urls = config.SOURCES.get("rss", [])
    if not rss_urls:
        rss_urls = ["https://news.ycombinator.com/rss"]  # dummy default

    connector = RssConnector(urls=rss_urls)
    raw_items = connector.fetch()

    logger.info(f"Fetched {len(raw_items)} items from RSS")

    # Transform to dict for AI prompt (and add ref)
    items_for_ai = []
    for i, item in enumerate(raw_items):
        # We simulate a countdown or basic formatting
        # For RSS, we might not have a deadline, so countdown is empty
        items_for_ai.append(
            {
                "ref": f"rss:{i}",
                "title": item.title,
                "description": item.description,
                "countdown_text": "",
            }
        )

    # Take top 5 for brevity
    items_for_ai = items_for_ai[:5]

    profile = config.PROFILE
    name = profile.get("name", "User")
    interests = profile.get("interests", [])

    sys_prompt, user_prompt = build_brief_prompt(name, interests, items_for_ai)

    if dry_run:
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
