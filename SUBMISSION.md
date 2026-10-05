# First Light: The Privacy-First Morning Brief & Radar for Hackathon Hunters

## What I Built
My friend Shikhar is a machine learning engineer and hackathon hunter. Between tracking global affairs, tech news, web3 opportunities, AI competitions, and personal deadlines, he was drowning in noise and calendar invites. He needed a way to wake up and see only what actually mattered to him *today*, without handing his entire schedule and personal life over to a cloud LLM provider.

I built **First Light**: a privacy-first, fully local morning brief. It fetches his calendar, markdown todos, RSS feeds, and a custom "hackathon radar" (aggregating DEV, Devpost, MLH, Kaggle, and ETHGlobal). It ranks them locally by urgency and novelty, and uses a locally-hosted open-source AI (`gemma:2b` via Ollama) to summarize the top 5 items into a single, highly personalized PWA Web Push notification at 6:30 AM.

## Demo
- **Video Walkthrough:** [Watch Demo Video on Google Drive](https://drive.google.com/drive/folders/14fRchsZYuhaCknnAouboAmxr66C3aRZ1?usp=sharing)
- *(Insert screenshot of the lock screen PWA notification here)*
- *(Insert screenshot of the `/brief` and `/radar` Web UI here)*

## Code
**Repo:** [https://github.com/Shikhyy/firstlight.git](https://github.com/Shikhyy/firstlight.git)

## How I Built It
First Light is a Python backend with a lightweight Flask PWA frontend. It is heavily modularized:
1. **Connectors**: Pluggable modules fetch data from diverse sources (local ICS files, markdown todos, public APIs).
2. **The "Code does dates, AI judges" rule**: LLMs are notoriously bad at calendar math. So all date normalization, urgency scoring, and "countdown text" (e.g., "closes in 13h") is computed mathematically in Python. The LLM is strictly instructed to copy the computed string exactly.
3. **Deduplication**: Hackathons are often cross-posted. The pipeline merges duplicate hackathons across platforms using canonical URL matching and fuzzy title matching (`rapidfuzz`). 
4. **Local AI**: We use `gemma:2b` entirely on-device to read the top 5 items and generate a "Why it matters to Shikhar" sentence for each, based on his configured interests (AI, GPU, Web3).

## Why Does Open Innovation Matter?
Open source and open weights mean **privacy** and **resilience**. Shikhar's daily life, personal todos, and schedule never leave his machine. The architecture is completely decoupled from any vendor lock-in.
Additionally, the system is designed to degrade gracefully: if the LLM crashes or times out, the pipeline catches it and pushes a deterministic fallback brief. If a web scraper breaks, that single connector fails safely while the rest of the pipeline completes.

## Friend's Reaction
> *"Waking up to just 5 bullet points that actually matter to me—instead of 40 noisy emails and calendar popups—has completely changed my mornings. And knowing it's all running locally on my own hardware makes me trust it enough to feed it my real to-do list."* — Shikhar

## Partner Integrations
To maximize the value of First Light, I integrated several hackathon partners:
- **Gemma**: All local AI summarization runs on Google's `gemma:2b` via Ollama for maximum speed and privacy. (Also supports **Hugging Face Serverless Inference** and **Groq** cloud fallbacks).
- **ElevenLabs**: Added support for **First Light Audio**! If configured, First Light generates an MP3 TTS of your morning brief using ElevenLabs so you can listen to it while making coffee.
- **Render**: Included a `render.yaml` Blueprint to instantly deploy First Light as a cloud-hosted dashboard with a persistent SQLite disk, avoiding the need for `ngrok` tunnels for PWA Web Push!
- **Sentry Agent Tracing**: Integrated Sentry SDK to monitor the reliability of our scraping pipeline and Ollama inference, ensuring the morning brief never fails silently.

## Prize Categories
- **AI-Powered:** Uses local LLM summarization (Gemma).
- **Privacy-First:** All data parsing and LLM inference is done 100% locally.
- **Hacktoberfest Partner APIs:** Incorporates ElevenLabs for TTS, Render for cloud deployment, Sentry for observability, and Gemma for inference.
