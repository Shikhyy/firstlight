TAXONOMY = {
    "ai",
    "ml",
    "web3",
    "security",
    "web",
    "hardware",
    "opensource",
    "gamedev",
    "social_good",
}


def classify_keywords(title: str, description: str) -> list[str]:
    text = (title + " " + description).lower()
    domains = set()

    if "ai " in text or "artificial intelligence" in text or "llm" in text:
        domains.add("ai")
    if "machine learning" in text or " ml " in text or "dataset" in text:
        domains.add("ml")
    if "web3" in text or "crypto" in text or "blockchain" in text or "eth" in text:
        domains.add("web3")
    if "security" in text or "hack" in text or "ctf" in text:
        domains.add("security")
    if "web " in text or "react" in text or "frontend" in text or "backend" in text:
        domains.add("web")
    if "hardware" in text or "iot" in text or "arduino" in text:
        domains.add("hardware")
    if "open source" in text or "opensource" in text or "hacktoberfest" in text:
        domains.add("opensource")
    if "game" in text or "unity" in text or "godot" in text:
        domains.add("gamedev")
    if "social" in text or "good" in text or "climate" in text or "health" in text:
        domains.add("social_good")

    return list(domains)
