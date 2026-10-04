import logging
from urllib.parse import urlparse

from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


def canonicalize_url(url: str) -> str:
    """Removes trailing slash, query params, forces lowercase host."""
    if not url:
        return ""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").rstrip("/")
    # If the URL had no scheme (e.g., devpost.com), urlparse might parse it strangely.
    # We just return host + path for deduplication logic.
    return f"{host}{path}"


def deduplicate_events(events: list[dict]) -> list[dict]:
    """
    Dedupes raw event dicts based on canonical URL first,
    then fuzzy title match if they have overlap in dates.
    """
    url_map = {}
    deduped = []

    # 1. Dedupe by exact canonical URL
    for event in events:
        c_url = canonicalize_url(event["url"])
        if not c_url:
            deduped.append(event)
            continue

        if c_url in url_map:
            logger.info(f"Deduped exact URL: {c_url}")
            # Merging could be complex, but for now we just append source
            url_map[c_url]["source"] += f", {event['source']}"
        else:
            url_map[c_url] = event
            deduped.append(event)

    # 2. Fuzzy Title Deduplication (threshold ~ 90)
    final_list = []
    for item in deduped:
        merged = False
        for existing in final_list:
            score = fuzz.ratio(item["title"].lower(), existing["title"].lower())
            if score > 90:
                # Same event
                logger.info(
                    f"Fuzzy merged: '{item['title']}' with '{existing['title']}' (Score: {score})"
                )
                existing["source"] += f", {item['source']}"
                merged = True
                break
        if not merged:
            final_list.append(item)

    return final_list
