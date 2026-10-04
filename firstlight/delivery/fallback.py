from firstlight.ai.schemas import BriefItem, BriefSummary


def build_fallback_brief(items: list[dict]) -> BriefSummary:
    if not items:
        return BriefSummary(title="Quiet day", quiet_day=True, items=[])

    title = f"{len(items)} deadline(s) today"
    brief_items = []

    # Take top 3 for fallback notification
    for item in items[:3]:
        headline = item["title"]
        # In fallback, just copy the countdown as 'why' or include it in headline.
        countdown = item.get("countdown_text", "")
        if countdown:
            headline = f"{headline}: {countdown}"

        brief_items.append(
            BriefItem(
                ref=item["ref"],
                headline=headline[:50],
                why=countdown[:120] if countdown else "Requires your attention",
            )
        )

    return BriefSummary(title=title, quiet_day=False, items=brief_items)
