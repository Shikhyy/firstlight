# First Light: Tech Stack

Everything is open-source unless noted. Pin exact versions in `requirements.txt` after installing; use the latest stable releases.

---

## 1. Summary

| Layer | Choice | Why |
|---|---|---|
| AI model | **Gemma 3 (small)** via **Ollama** | Open-weight, runs locally; qualifies for Best Use of Gemma |
| Fallback models | Qwen or Llama small variants via Ollama | Swap and compare for the "why open matters" section |
| Language | **Python 3.11+** | Fastest path; every library needed exists |
| Web framework | **Flask** + Jinja templates | Small, no build step |
| Frontend | HTML, CSS, vanilla JS | No framework needed for 2 pages |
| Database | **SQLite** | Zero setup, single file |
| Scheduling | **cron** (or APScheduler) | Triggers the 05:30 run |
| Push delivery | **ntfy** | Open-source push; one HTTP POST gives a lock-screen notification with buttons |
| Feeds | `feedparser` (RSS), `icalendar` (ICS) | Stable, official-style sources |
| HTTP | `requests` or `httpx` | Fetching sources and calling Ollama |
| Dates | `python-dateutil`, `zoneinfo` | All date logic in code |
| Fuzzy match | `rapidfuzz` | Deduplication |
| Validation | `pydantic` | Strict schemas for connectors and model JSON |
| HTML parsing | `beautifulsoup4` | Only where no API or feed exists |
| Tests | `pytest`, `pytest-cov`, `requests-mock`, `freezegun` | Fixture-based connector tests, mocked network, injected time |
| Lint / format | `ruff` | One tool for both |
| Git hygiene | `.githooks/` (commit-msg, pre-commit) + GitHub Actions | Enforces Conventional Commits, lint and tests on every commit and push |

## 2. AI layer

- **Runtime:** Ollama running locally (default `http://localhost:11434`).
- **Primary model:** a small Gemma 3 variant (e.g. `gemma3:4b`; drop to `gemma3:1b` if the machine is limited). Confirm available tags with `ollama list` / the Ollama model library.
- **Optional embeddings:** a small embedding model (e.g. `nomic-embed-text`) for dedup fallback only.
- **Calls:** use Ollama's HTTP API with `stream: false` and JSON output. Validate responses with pydantic. One retry on invalid JSON, then fallback mode.

### What the model does vs. what code does

| Model | Code |
|---|---|
| Chooses what matters for this person | Fetching and parsing sources |
| Writes headlines and "why this matters" lines | All date and deadline math |
| Classifies ambiguous events | Dedup rules and scoring formula |
| Writes the "Should I enter?" verdict | Scheduling, notifications, storage |

**Rule:** the model never outputs a date or deadline.

## 3. Data sources

| Source | Method | Notes |
|---|---|---|
| Calendar | ICS feed URL (e.g. Google Calendar secret ICS) | Parsed with `icalendar` |
| Todos | `todos.md` file in the repo's data folder | Simplest; optional Google Tasks later |
| AI news | RSS from selected blogs, Hugging Face, Hacker News | Via `feedparser` |
| Weather | Open-Meteo API | Free, no key |
| Hackathons | DEV challenges, Devpost, MLH, Kaggle (official API), one web3 source | See connector rules below |

### Connector rules
- Prefer official APIs, RSS and ICS over HTML scraping.
- Check `robots.txt` and each site's terms before scraping.
- Send a clear User-Agent, rate-limit, and cache with ETag / Last-Modified.
- Each connector is isolated: failure never stops the run.
- Endpoints and page structures change; verify each source manually before coding its connector.

## 4. Push delivery: ntfy

- Send with one HTTP POST to `https://<ntfy-host>/<topic>`.
- Headers used: `Title`, `Priority`, `Tags`, `Click`, `Actions`.
- **Action buttons** call back to the Flask server (`Done`, `Snooze`). The server must be reachable from the phone (public URL, tunnel, or hosted).
- Use a long random topic name; treat it as a secret. Self-host ntfy if privacy matters more than convenience.
- Scheduled delivery (for the precompute mode): check ntfy docs for delayed-delivery headers.

## 5. Hosting options

| Option | Fit |
|---|---|
| **Always-on home machine / Raspberry Pi** | Best fit for "self-hosted"; runs Ollama and cron |
| **Laptop with night precompute** | Fastest for a weekend; slightly stale brief |
| **Render** (web service + cron job) | Good for the Flask brief page and cron; Ollama itself needs a machine with enough RAM, so run the model elsewhere or use a bigger instance |
| **DigitalOcean GPU Droplet** | Option for serving the open-weight model remotely |

Only list a partner category (Render, DigitalOcean) in the submission if the project genuinely uses it.

## 6. Optional extras (P2)

| Feature | Tool |
|---|---|
| Voice notes to todos | Whisper (local) |
| Audio brief | Local TTS or ElevenLabs |
| Tracing and cost view | Sentry Agent Tracing (partner category) |

## 7. Configuration and secrets

- `config.yaml`: friend profile, interests, sources, wake time, timezone.
- `.env`: `NTFY_TOPIC`, `NTFY_BASE_URL`, `ACTION_TOKEN`, `ICS_URL`, `OLLAMA_URL`, `OLLAMA_MODEL`, any API keys (e.g. Kaggle).
- `.env` and `data/` are git-ignored. Never commit secrets or personal data.

## 8. Dev environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull gemma3:4b          # or a smaller tag
python -m firstlight run --dry-run
```

## 9. Open-source credits to include in the README

Ollama, Gemma, Flask, SQLite, ntfy, feedparser, icalendar, rapidfuzz, pydantic, BeautifulSoup, Open-Meteo. Credit any code or ideas borrowed from other projects.
