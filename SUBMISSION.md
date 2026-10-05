# First Light: The Privacy-First Morning Brief & Radar for Hackathon Hunters

## What I Built
My friend Shikhar is a machine learning engineer, backend enthusiast, and avid hackathon hunter. Between tracking global tech affairs, web3 releases, ML benchmarks, hackathon registration windows, and daily personal tasks, his mornings were overwhelmed by a storm of notification badges, spam newsletters, and calendar alerts. He needed a way to wake up, glance at his phone, and see **only the top 5 things that actually matter to him today**—without shipping his entire personal calendar, private to-do list, and unreleased project ideas to a third-party cloud LLM.

To solve this, I built **First Light**: a privacy-first, 100% locally-run morning intelligence brief and hackathon radar. Every morning at 6:30 AM, First Light:
1. Gathers events from local ICS calendars, markdown to-do files, RSS news feeds, and a curated hackathon radar (DEV, Devpost, MLH, Kaggle, and Web3/ETHGlobal).
2. Mathematically calculates urgency windows and deduplicates cross-posted hackathons across platforms.
3. Uses a local open-weight model (**Google Gemma 2B**) to synthesize the noise into a concise, prioritized 5-bullet morning brief tailored to Shikhar's profile.
4. Delivers a native, lock-screen Web Push notification to his phone via a self-hosted PWA, complete with an interactive dashboard and an ElevenLabs audio briefing.

> *"Waking up to just 5 bullet points that actually matter to me—instead of 40 noisy emails and calendar popups—has completely changed my mornings. And knowing it's all running locally on my own machine makes me trust it enough to feed it my real daily to-do list."* — Shikhar

## Demo
- **Video Walkthrough:** [Watch the Full Demo on Google Drive](https://drive.google.com/drive/folders/14fRchsZYuhaCknnAouboAmxr66C3aRZ1?usp=sharing)
- **Live Interface & Features Shown:**
  - 🔔 **Native PWA Web Push:** Lock-screen notification delivered directly to mobile without third-party messaging apps.
  - 🌅 **Dawn-Themed Dashboard:** Frosted glass UI displaying the AI briefing, deadline countdowns, and urgency meters.
  - 🎧 **First Light Audio:** On-demand text-to-speech briefing player powered by ElevenLabs.
  - 🎯 **Hackathon Radar:** Filterable list of competitions with direct registration links and AI "Should I enter?" verdicts.
  - ✅ **Interactive To-Dos:** Real-time task completion synced directly to the local SQLite database.

## Code
{% github https://github.com/Shikhyy/firstlight %}

**Repository URL:** [https://github.com/Shikhyy/firstlight](https://github.com/Shikhyy/firstlight)

## How I Built It
First Light is engineered in Python with an installable CLI (`pip install -e .`), backed by SQLite and a lightweight Flask PWA with a custom Service Worker.

### 1. Open-Source AI Architecture
- **Local-First Core:** We run Google's **Gemma 2B** (`gemma:2b`) locally via [Ollama](https://ollama.com/). It runs on consumer hardware (such as an Apple Silicon Mac) with near-zero latency and zero operational cost.
- **Pydantic Structured Outputs:** The pipeline enforces structured JSON schema validation (`BriefSummary`) directly on the model's output to guarantee schema compliance.
- **Graceful Cloud Fallbacks:** For cloud deployments where local Ollama is inaccessible, First Light seamlessly falls back to **Hugging Face Serverless Inference** (`google/gemma-2-2b-it`) or Groq, keeping the architecture strictly on open Gemma models.

### 2. The "Code Does Dates, AI Judges" Architecture
LLMs frequently hallucinate calendar math and relative dates. First Light enforces a strict architectural separation:
- **Deterministic Engine (Python):** Date parsing, deadline countdowns (e.g., `"closes in 13h"`), urgency scores ($[0.0, 1.0]$), and deduplication (canonical URL normalization + RapidFuzz token matching) are calculated purely in Python.
- **Judgment Engine (Gemma):** The LLM receives pre-calculated facts and strictly evaluates relevance: *"Why does this matter to Shikhar based on his interests in ML, Web3, and Backend?"*

### 3. Resilient Pipeline & Fail-Safe Delivery
- Each data connector (DEV, Devpost, MLH, Kaggle, RSS, Calendar) is isolated in a try/except sandbox; if one scraper fails, the pipeline logs the error in a `source_runs` health table and continues uninterrupted.
- If Ollama is offline or times out, the pipeline triggers a deterministic fallback generator, ensuring a morning brief is *always* delivered on time.

## Why Does Open Innovation Matter?
Open innovation and open-weights models are essential for personal software like First Light:

1. **Absolute Data Privacy:** Your personal calendar, daily tasks, health appointments, and unreleased project ideas are deeply intimate data. Routing this stream through proprietary closed APIs means sharing your life with centralized corporate servers. With Gemma running locally, your personal data literally never leaves your device.
2. **Zero Marginal Cost & No Rate Limits:** Closed APIs charge per token, rate-limit automated jobs, and risk breaking changes. Open models allow automated morning pipelines and background cron jobs to run indefinitely for free.
3. **Resilience & Vendor Independence:** Open innovation ensures First Light will function offline, on an airplane, or years in the future without risk of API deprecation, subscription price hikes, or account suspensions.

## My Agent Session
First Light was designed, implemented, and tested through an intensive pair-programming session using **Google Antigravity**:
- Orchestrated the full project lifecycle: data connectors, SQLite schema design, fuzzy deduplication algorithms, Pydantic schema validation, and PWA Web Push implementation with VAPID crypto keys.
- Iterated rapidly on prompt engineering and deterministic fallback logic to guarantee sub-minute pipeline execution on lightweight hardware.

## Prize Categories
We are entering the following partner categories:
- **Gemma:** Core intelligence is built entirely around Google's `gemma:2b` via Ollama for fast, local, privacy-first summarization, with Hugging Face Serverless integration for `google/gemma-2-2b-it`.
- **ElevenLabs:** Integrated ElevenLabs Text-to-Speech into `firstlight/delivery/audio.py` to synthesize a natural, spoken morning briefing playable directly from the PWA dashboard.
- **Render:** Provided a turnkey `render.yaml` Infrastructure-as-Code Blueprint with persistent disk mounts to deploy First Light as a cloud web service and automated cron worker with a single click.
- **Sentry Agent Tracing:** Integrated `sentry-sdk` to trace pipeline transactions, monitor scraper reliability, and observe local LLM inference performance.
