# AGENTS.md: First Light

Instructions for AI coding agents working on this repository (Google Antigravity or any agentic IDE).

> Place this file at the repo root. If your tool does not read `AGENTS.md` automatically, paste its contents into the workspace rules / agent instructions.

---

## 1. Mission

Build **First Light**: a self-hosted morning assistant that collects the user's calendar, todos, AI news and hackathon deadlines, uses a **local open-source model (Gemma via Ollama)** to pick and summarize the top items, and delivers them as a lock-screen notification (ntfy) plus a brief web page.

It is a hackathon project with a hard deadline: **Monday 5 Oct 2026, 12:29 PM IST**. Favor a small, reliable, working product over a large, fragile one.

## 2. Doc map (read before coding)

| File | Read it for |
|---|---|
| `PRD.md` | What and why, priorities (P0/P1/P2), non-goals |
| `APP_FLOW.md` | User flows, pipeline stages, failure behavior |
| `TECH_STACK.md` | Approved tools and constraints |
| `BACKEND_AND_SCHEMA.md` | Layout, SQL schema, interfaces, prompts, API |
| `FRONTEND_UI_GUIDELINES.md` | Design tokens, glass UI, animation, accessibility |
| `IMPLEMENTATION_PLAN.md` | Phase order, acceptance criteria, cut list, commit checkpoints |
| `GIT_AND_TESTING_WORKFLOW.md` | Dev loop, test strategy, phase gates, branching, Conventional Commits, hooks, CI |
| `PROGRESS.md` | Running log; update after every push |

If a request conflicts with these docs, stop and ask. If the docs are wrong or incomplete, propose an edit to the doc in the same change.

## 3. Non-negotiable rules

1. **Code owns dates; the model never does.** All date parsing, timezone conversion, deadline math and countdown text are plain Python. The model receives pre-computed countdown strings and must copy them. Never accept a date produced by the model.
2. **Local, open-source AI only.** Use Ollama with an open-weight model. Do not add closed-API calls (OpenAI, Anthropic, etc.) to the runtime.
3. **Fallback must always work.** If Ollama fails, times out or returns invalid JSON twice, send the plain non-AI brief. The user always gets a notification.
4. **Connectors are isolated.** One failing source must never break a run. Catch, log to `source_runs`, continue.
5. **Prefer official APIs, RSS and ICS over scraping.** Before scraping a site, check its `robots.txt` and terms. Rate-limit, set a User-Agent, cache.
6. **No secrets or personal data in git.** `.env`, `data/`, `logs/` are git-ignored. Use `.env.example` for placeholders.
7. **Validate everything crossing a boundary.** Connector output and model output pass through pydantic models.
8. **Do not invent facts.** No fabricated hackathons, deadlines, prizes or sources. If data is missing, store `NULL` and lower `confidence`.
9. **Stay in scope.** Build P0 first, then P1. P2 and "future work" only if the plan says time allows.
10. **Credit prior work.** Note any borrowed code or ideas in the README.
11. **Every change goes through the dev loop** in `GIT_AND_TESTING_WORKFLOW.md`: test first, implement, format, lint, test, smoke test, commit, push, log. Max 3 fix attempts per distinct failure, then stop and report.
12. **Never weaken tests to get green.** Do not delete, skip or loosen a test to pass. Never use `--no-verify`.
13. **Commit often, in Conventional Commits style**, atomically, and push after every commit. Every commit passes lint and tests. Never commit secrets, `.env`, `data/` or `logs/`. Never force-push or rewrite published history.

## 4. Repository layout

See `BACKEND_AND_SCHEMA.md` section 1. Do not add top-level folders without updating that doc.

## 5. Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m firstlight init-db
python -m firstlight run --dry-run     # full pipeline, prints instead of sending
python -m firstlight run               # full pipeline + sends ntfy push
python -m firstlight run --no-ai       # force fallback mode
python -m firstlight serve             # Flask app
pytest -q
ruff check . && ruff format .
```

Run `pytest` and `ruff` before declaring any task done.

## 6. Coding conventions

- Python 3.11+, type hints on all public functions, small functions, clear names.
- Pydantic models for connector items, AI outputs and config.
- Store timestamps as ISO 8601 **UTC**; convert to `Asia/Kolkata` only for display.
- No network calls in tests; use fixtures in `tests/fixtures/`.
- Log one line per pipeline stage with duration; log errors with context.
- Keep functions pure where possible (normalize, dedupe, rank) so they are easy to test.
- Frontend: Jinja + one CSS file + minimal vanilla JS. No JS framework, no build step.
- Follow `FRONTEND_UI_GUIDELINES.md` for every UI change (tokens, glass card, 44px targets, reduced motion, no emoji icons).

## 7. Task protocol (for every task)

1. **Read** the relevant docs and the files you will touch.
2. **Plan**: list the files you will change and the acceptance criteria (from `IMPLEMENTATION_PLAN.md`). Create or switch to a branch `<type>/<short-desc>`.
3. **Loop** (see `GIT_AND_TESTING_WORKFLOW.md` section 1):
   test first, implement, `ruff format .`, `ruff check .`, `pytest -q`.
   If red: read the error, fix, rerun. After 3 failed attempts on the same failure, stop and report.
4. **Smoke test** with `python -m firstlight run --dry-run` when pipeline, AI, delivery or web code changed.
5. **Commit** with a Conventional Commit message (atomic, one concern) and **push**.
6. **Log** in `PROGRESS.md`.
7. **Merge** to `main` only when green. At a phase gate, tag `phase-N` and push tags.
8. **Report**: what changed, what was tested, commits (hash and message), what is left, assumptions and risks.

Do not mark a task done if tests fail or acceptance criteria are unmet.

## 8. Agent roles

Use these roles to split work across parallel agents. Each agent works only in its own area and avoids editing others' files without coordination.

### Planner / Coordinator
- **Owns:** `IMPLEMENTATION_PLAN.md`, `PROGRESS.md`, task breakdown, merge order, phase tags.
- **Does:** reads all docs, assigns phases, tracks progress, applies the cut list when time is short, keeps docs consistent.
- **Must not:** write feature code.

### Backend / Pipeline agent
- **Owns:** `firstlight/pipeline/`, `db.py`, `models.py`, `config.py`, `__main__.py`.
- **Does:** schema, normalization, dedupe, classify, rank, orchestration, CLI.
- **Key checks:** deadline math is correct; ranking matches the formula; fallback works.

### Connector agent
- **Owns:** `firstlight/connectors/`, `tests/fixtures/`.
- **Does:** one connector at a time. For each: verify the source manually, prefer API/RSS/ICS, return `RawItem`s, save a fixture, add a test.
- **Must not:** parse dates into final form or score items.
- **Key checks:** robots/terms respected; failure raises cleanly; no secrets in fixtures.

### AI agent
- **Owns:** `firstlight/ai/`, `firstlight/delivery/fallback.py`.
- **Does:** Ollama client, prompts, output schemas, retry-then-fallback logic, verdict and classification prompts.
- **Key checks:** output validates against schema; unknown `ref`s rejected; model never emits dates; token and latency recorded in `briefs`.

### Delivery agent
- **Owns:** `firstlight/delivery/ntfy.py`, action endpoints in `web/app.py`.
- **Does:** ntfy push with title/body/click/actions, retries, token-protected `done` and `snooze`.
- **Key checks:** verify ntfy header and action syntax against the ntfy docs; constant-time token compare.

### Frontend agent
- **Owns:** `firstlight/web/templates/`, `firstlight/web/static/`.
- **Does:** `/brief`, `/radar`, `/health` pages per the UI guidelines.
- **Key checks:** matches the mockup, works at 390px, contrast and touch targets, `prefers-reduced-motion` respected.

### QA / Reviewer agent
- **Owns:** `tests/`, `.githooks/`, `.github/workflows/`, review of every change.
- **Does:** runs tests and lint, checks acceptance criteria, tries failure cases (Ollama down, bad JSON, connector error, unparseable date), verifies no secrets are committed.
- **Must not:** approve work that fails the rules in section 3.

### Docs / Writer agent
- **Owns:** `README.md`, the DEV post draft.
- **Does:** README (setup, config, credits, post-deadline commit note), post draft following the outline in `IMPLEMENTATION_PLAN.md`, real screenshots, honest limitations.
- **Must not:** invent results, quotes or numbers. Use only real measurements and the friend's real words.

## 9. Definition of done

A task is done when all are true:

- [ ] Acceptance criteria in `IMPLEMENTATION_PLAN.md` are met
- [ ] `pytest` and `ruff` pass
- [ ] Failure paths tested where relevant
- [ ] `run --dry-run` works if the pipeline was touched
- [ ] No secrets, personal data or generated junk committed
- [ ] Docs updated if behavior or structure changed
- [ ] A short report was written per section 7
- [ ] Committed with Conventional Commit message(s), atomic, and pushed
- [ ] CI is green on the branch (and on `main` after merge)
- [ ] `PROGRESS.md` updated

## 10. Out of scope (do not build unless told)

Native mobile apps, user accounts or login, auto-registering for hackathons, email or chat assistants, multi-user mode, paid or closed AI APIs, anything requiring storing other people's personal data.

## 11. When to stop and ask

- A source's terms appear to forbid scraping.
- A change would add a closed AI service, a new top-level folder, or a new dependency outside `TECH_STACK.md`.
- You cannot meet an acceptance criterion within the time budget.
- Requirements in the docs conflict with each other.

State the question, the options, and your recommendation, then wait.
