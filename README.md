# First Light 🌅

A privacy-first, locally-run morning brief and hackathon radar. First Light cuts through the noise by summarizing your calendar, markdown to-do lists, RSS feeds, and upcoming hackathons into a single, personalized push notification every morning at 6:30 AM.

All data fetching, deduplication, and AI summarization (using `gemma:2b` via Ollama) runs 100% locally on your machine. Your schedule never leaves your device.

![First Light PWA Preview](https://via.placeholder.com/800x400.png?text=First+Light+PWA+Preview)

## Features
- **Hackathon Radar**: Aggregates and deduplicates hackathons from DEV, Devpost, MLH, Kaggle, and Web3 sources.
- **Local AI Summarization**: Uses Ollama to read your top events and tell you *why* they matter based on your configured interests.
- **Privacy-First**: No cloud APIs for your personal data. 
- **PWA Web Push**: Sends a native lock-screen notification to your phone without relying on third-party apps.
- **Deterministic Math**: LLMs are bad at math, so all deadline urgency and countdowns ("closes in 13h") are calculated entirely in Python before the AI sees them.

## Setup & Installation

**Prerequisites:**
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally.
- (Optional) `ngrok` if you want to push notifications to your phone remotely.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shikhyy/firstlight.git
   cd firstlight
   ```

2. **Set up the virtual environment & install:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Initialize the SQLite database & generate VAPID keys:**
   ```bash
   firstlight init-db
   python generate_vapid.py
   ```

4. **Configure your profile:**
   Edit `config.yaml` to include your name, interests, and preferred LLM model (e.g., `gemma:2b`).

5. **Pull the AI Model:**
   ```bash
   ollama run gemma:2b
   ```

## How to Use

To use First Light, you run the web UI to subscribe your phone, and then schedule the pipeline to run every morning.

### 1. Subscribe your phone to Web Push
Start the web UI:
```bash
firstlight web
```
Expose port 8080 to the internet (e.g., using `ngrok http 8080`). Open the URL on your phone's browser, tap "Add to Home Screen", open the installed PWA, and click **🔔 Enable Push**.

### 2. Run the morning pipeline
You can manually trigger the pipeline (and send the push notification) by running:
```bash
firstlight run
```
*(Use `firstlight run --no-ai` if you want to skip the AI generation and just test the delivery).*

### 3. Schedule it (Cron)
To get the notification automatically every morning, add a cron job on your always-on Mac or server:
```bash
# Open crontab
crontab -e

# Add this line to run every day at 06:30 AM
30 06 * * * cd /path/to/firstlight && /path/to/firstlight/.venv/bin/firstlight run
```

## Credits & Technologies
- **Backend:** Python, SQLite, Flask, `pywebpush`
- **AI:** [Ollama](https://ollama.com/) running Google's [Gemma 2B](https://ai.google.dev/gemma).
- **Frontend:** HTML/CSS (Vanilla), Next.js-inspired PWA architecture.
- **Built for:** The DEV & Google Open Source AI Hackathon 2026.

> **Note:** Any commits pushed after Monday Oct 5, 2026, 12:29 PM IST were made after the hackathon deadline for minor bug fixes or documentation formatting.
