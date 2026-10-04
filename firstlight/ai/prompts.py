BRIEF_SYSTEM_PROMPT = """
You are a concise morning assistant for {name}. 
Their interests: {interests}.

Your task:
Summarize the top items provided into a short, glanceable brief.
- Use only the facts provided. Never invent dates or times; copy the provided countdown_text exactly.
- `title`: max 60 characters, summarizes the day.
- For each item:
  - `headline`: max 50 characters.
  - `why`: one sentence, max 120 characters, explaining why it matters to {name} based on their interests.
- If no items are provided or nothing is urgent, set `quiet_day` to true.
- Output ONLY valid JSON matching the schema.
"""


def build_brief_prompt(
    name: str, interests: list[str], items: list[dict]
) -> tuple[str, str]:
    system_prompt = BRIEF_SYSTEM_PROMPT.format(
        name=name, interests=", ".join(interests)
    )

    user_prompt = "Items to summarize:\n"
    for idx, item in enumerate(items):
        user_prompt += f"ref: {item['ref']}\n"
        user_prompt += f"title: {item['title']}\n"
        if item.get("countdown_text"):
            user_prompt += f"countdown: {item['countdown_text']}\n"
        if item.get("description"):
            user_prompt += f"description: {item['description']}\n"
        user_prompt += "\n"

    return system_prompt, user_prompt
