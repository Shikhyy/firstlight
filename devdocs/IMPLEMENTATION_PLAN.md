# First Light: Implementation Plan

**Deadline:** Monday, 5 Oct 2026, 12:29 PM IST. Plan starts Saturday night, 3 Oct.
**Rule:** get a thin end-to-end version working first, then add to it. Never leave the project in a state that doesn't run.

Read before starting: `PRD.md`, `APP_FLOW.md`, `TECH_STACK.md`, `BACKEND_AND_SCHEMA.md`, `FRONTEND_UI_GUIDELINES.md`, `GIT_AND_TESTING_WORKFLOW.md`, `AGENTS.md`.

---

## Timeline at a glance

| Block | When (IST) | Phases | Outcome |
|---|---|---|---|
| Sat night | ~3 hrs | 0, 1 | Real notification on the phone |
| Sun morning | ~4 hrs | 2 | Real data, ranking, deadline math |
| Sun afternoon | ~4 hrs | 3 | Hackathon radar with dedup |
| Sun evening | ~3 hrs | 4, 5 | Web UI, buttons, fallback |
| Sun night | ~2 hrs | 6 | Deployed, scheduled, tested |
| Mon early morning | ~3 hrs | 6, 7 | Friend's reaction, write-up, **submit by 11:00 AM** (buffer before 12:29 PM) |

If you fall behind, use the **cut list** at the bottom. Do not cut Phase 7.

---

## Phase 0: Setup (~45 min)

- [ ] Create the GitHub repo **now** (it must be started inside the challenge window). Add README stub.
- [ ] Add `.gitignore` (`.env`, `data/`, `logs/`, `.venv/`, `__pycache__/`).
- [ ] Create venv, `requirements.txt`, install dependencies.
- [ ] Install Ollama; pull the Gemma model; test one prompt.
- [ ] Create an ntfy topic (long random name); install the ntfy app on the friend's phone (or yours for testing).
- [ ] Create `.env` from `.env.example`; create `config.yaml` with the friend's profile.
- [ ] Create the folder structure from `BACKEND_AND_SCHEMA.md`.

**Done when:** `ollama run` answers, and a `curl` POST to ntfy shows a notification on the phone.

## Phase 1: Walking skeleton (~2 hrs)

Goal: one source, one summary, one notification, end to end.

- [ ] `connectors/rss_news.py`: fetch one RSS feed.
- [ ] `ai/client.py`: call Ollama, return parsed JSON.
- [ ] `ai/prompts.py` + `ai/schemas.py`: the brief-summary contract.
- [ ] `delivery/ntfy.py`: send title + body.
- [ ] `__main__.py run --dry-run` and `run`.

**Done when:** `python -m firstlight run` puts a real summarized notification on the phone.

## Phase 2: Core data and ranking (~4 hrs)

- [ ] `db.py` with the schema; `init-db` command.
- [ ] `connectors/calendar_ics.py`, `todos_md.py`, `weather.py`.
- [ ] `pipeline/normalize.py`: dates to UTC, validation, `confidence`.
- [ ] `pipeline/rank.py`: scoring formula; countdown text computed in code.
- [ ] `seen_items` handling (novelty).
- [ ] `delivery/fallback.py` and `--no-ai`.
- [ ] Tests: date normalization, countdown text, scoring.

**Done when:** the brief includes calendar, todos, news and weather; every countdown matches a manual check.

## Phase 3: Hackathon radar (~4 hrs)

- [ ] `connectors/base.py` and `source_runs` logging with per-connector isolation.
- [ ] Build **5 to 6 connectors**, one at a time. For each: verify the source manually, prefer API/RSS, save a fixture, write a test.
  - [ ] DEV challenges
  - [ ] Devpost
  - [ ] MLH
  - [ ] Kaggle (official API)
  - [ ] One web3 source
  - [ ] (optional) one India-focused source
- [ ] `pipeline/dedupe.py`: URL, then fuzzy title + dates.
- [ ] `pipeline/classify.py`: keyword rules; model for leftovers.
- [ ] "Should I enter?" verdict, cached in `events.verdict_json`.
- [ ] Find and record at least one real duplicate merged across platforms (for the post).

**Done when:** the radar returns correct, deduplicated events across at least 5 sources; one broken connector does not stop a run.

## Phase 4: Web UI (~3 hrs)

- [ ] Flask app, base template, CSS with design tokens, glow orbs, glass cards (`FRONTEND_UI_GUIDELINES.md`).
- [ ] `/brief` page.
- [ ] `/radar` page with filter chips.
- [ ] `/health` page.
- [ ] Animations and `prefers-reduced-motion` handling.
- [ ] Check at 390px width; check contrast and 44px touch targets.

**Done when:** the pages visually match the mockup and work on the friend's phone.

## Phase 5: Interactivity and reliability (~2 hrs)

- [ ] Action endpoints (`done`, `snooze`) with token check.
- [ ] ntfy action buttons wired to those endpoints.
- [ ] Quiet-day logic.
- [ ] Retry/backoff for ntfy; Ollama timeout, one retry, then fallback.
- [ ] End-to-end test with fixtures.
- [ ] *(P2)* feedback buttons and weight updates.

**Done when:** tapping Done on the phone marks the todo done; killing Ollama still produces a notification.

## Phase 6: Deploy and real use (~2 hrs, overlapping Sun night / Mon)

- [ ] Pick the scheduling mode (always-on machine, or night precompute with scheduled delivery).
- [ ] Set up cron for the run time; make the web app reachable from the phone (public URL or tunnel) if using buttons.
- [ ] Do one full overnight run and check the 06:30 notification.
- [ ] Hand it to the friend; ask what they think; record their words.
- [ ] Take screenshots: real lock-screen notification, brief, radar, health page.

**Done when:** a notification arrives unattended at the set time.

## Phase 7: Write-up and submission (~2 hrs; submit by 11:00 AM IST)

- [ ] README: what it is, setup, config, credits, and a note on any commits after the deadline.
- [ ] Demo: deployed link and/or a short video.
- [ ] Write the post using the DEV template.
- [ ] Optional: save and embed the agent session (DevRelay).
- [ ] Submit and verify the post is public with the correct tags.

### Post outline (writing quality is weighted most)

1. **What I Built:** the friend, their problem, in their words.
2. **Demo:** lock-screen screenshot first.
3. **Code:** repo link.
4. **How I Built It:** pipeline, the "AI judges, code does dates" rule, connector design, dedup example.
5. **Why Does Open Innovation Matter?:** privacy, zero cost, swappable models; include a before/after model comparison and honest limits (hallucinations, scraper breakage).
6. **Friend's reaction:** direct quote.
7. **What's next:** chat assistant, mood check-in, more connectors.
8. **Prize Categories:** only those genuinely used (e.g. Gemma).

### Submission checklist

- [ ] Published on DEV before **12:29 PM IST, Mon 5 Oct** (target 11:00 AM)
- [ ] Tags: `devchallenge`, `weekendchallenge`, `hf26challenge`
- [ ] All template sections filled
- [ ] Written in English
- [ ] Repo public; project started within the window
- [ ] Prior work and open-source code credited
- [ ] Teammates' DEV handles listed (if any); one submission only
- [ ] Prize categories listed only if truly used

---

## Cut list (in order, if time runs short)

1. Feedback loop and audio brief (P2)
2. Verdict ("Should I enter?")
3. Extra connectors beyond 4
4. Embedding-based dedup
5. `/health` page polish (keep the data)
6. Animations (keep glass and layout)

**Never cut:** Phase 1 working notification, correct deadline math, fallback mode, real-friend feedback, the write-up.

## Risks to watch

| Risk | Response |
|---|---|
| A connector's source changes or blocks | Replace with another source; keep the fixture test |
| Model too slow on the machine | Use a smaller model tag; reduce `top_n_for_model` |
| Notification buttons don't work (phone can't reach server) | Keep Open button and brief link; mention limitation honestly |
| Friend unavailable for feedback | Use your own use as the test and say so plainly |


---

## Commit checkpoints by phase

Every phase follows the dev loop and Conventional Commits from `GIT_AND_TESTING_WORKFLOW.md`. Expected commits are a guide, not a script: commit after every green iteration, and push after every commit. Tag each finished phase.

| Phase | Expected commits (examples) | Tag |
|---|---|---|
| 0 Setup | `chore(repo): add gitignore and env example` · `build(deps): add runtime and dev dependencies` · `chore(config): add config.yaml template` · `ci: add github actions workflow for lint and tests` · `ci: add commit-msg and pre-commit hooks` · `docs: add progress log` | `phase-0` |
| 1 Skeleton | `feat(connectors): add rss news connector with fixture test` · `feat(ai): add ollama client with schema validation` · `test(ai): cover invalid json and timeout paths` · `feat(delivery): send ntfy push with title and body` · `feat(delivery): add fallback brief builder` · `feat(pipeline): add run command with dry-run` | `phase-1` |
| 2 Core | `feat(db): add sqlite schema and init command` · `feat(connectors): add calendar, todos and weather connectors` · `feat(pipeline): normalize dates to utc with confidence` · `feat(pipeline): add ranking with countdown text` · `test(pipeline): cover scoring and countdown edge cases` | `phase-2` |
| 3 Radar | one `feat(connectors): add <name> connector with fixture test` per source · `feat(pipeline): add connector isolation and source run logging` · `feat(pipeline): add dedupe by url and fuzzy title` · `feat(ai): add should-i-enter verdict` · `test(pipeline): prove one failing connector does not stop run` | `phase-3` |
| 4 Web UI | `feat(web): add base layout with glass tokens` · `feat(web): add brief page` · `feat(web): add radar page with filter chips` · `feat(web): add health page` · `style(web): add motion and reduced-motion support` | `phase-4` |
| 5 Interactivity | `feat(web): add token-protected done and snooze endpoints` · `feat(delivery): wire ntfy action buttons` · `fix(ai): add date-safety output guard` · `test(web): cover token and db change` | `phase-5` |
| 6 Deploy | `chore(repo): add cron and run scripts` · `docs(readme): add setup and scheduling modes` · `fix(...)` for anything found in the overnight run | `phase-6` |
| 7 Submit | `docs(readme): add screenshots, credits and post-deadline note` · `chore(repo): final cleanup` | `phase-7` |

### Rules recap
- Never push red to `main`; branch per task; merge when green.
- Max 3 fix attempts per failure, then stop and report.
- At every phase: run both gates (automated and manual) before tagging.
- Update `PROGRESS.md` after every push.
