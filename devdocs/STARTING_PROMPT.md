# First Light: Starting Prompt for Google Antigravity

Open the repo (with all the `.md` dev docs in the root) in Antigravity. If a plan-first or planning mode is available, use it. Paste **Prompt 1** into the agent. Use the follow-up prompts after each phase.

**Before you paste:**
- The GitHub repo exists and `git push` works from your terminal (`gh auth login` or SSH).
- Put secrets in `.env` yourself. Never paste secrets into the chat.
- If the IDE asks to approve terminal commands, allow `git`, `python`, `pip`, `pytest`, `ruff`.

---

## Prompt 1: Kickoff (Phase 0 and 1)

```
You are the lead engineer on "First Light", a hackathon project with a HARD deadline of Monday 5 Oct 2026, 12:29 PM IST. This repo contains the dev docs. Follow them exactly.

STEP 0: READ FIRST (write no code yet)
Read in full: AGENTS.md, PRD.md, APP_FLOW.md, TECH_STACK.md, BACKEND_AND_SCHEMA.md, FRONTEND_UI_GUIDELINES.md, IMPLEMENTATION_PLAN.md, GIT_AND_TESTING_WORKFLOW.md.
Then reply with:
 (a) a summary of the product and plan in about 10 lines, in your own words;
 (b) everything you need from me (friend profile details, git remote URL, ntfy topic, ICS URL, which Gemma tag fits my machine). I will place secrets in .env myself. Never ask me to paste secrets in chat;
 (c) any conflicts, gaps or risks you found in the docs.
Wait for my "go" before Step 1.

STEP 1: PHASE 0, SETUP
Follow IMPLEMENTATION_PLAN.md Phase 0 and GIT_AND_TESTING_WORKFLOW.md section 6:
 - folder structure from BACKEND_AND_SCHEMA.md, .gitignore, .env.example, config.yaml, requirements.txt (runtime and dev deps);
 - .githooks/commit-msg and .githooks/pre-commit, and set core.hooksPath;
 - .github/workflows/ci.yml;
 - PROGRESS.md from the template;
 - one placeholder test so pytest runs green.
Commit in small atomic Conventional Commits and push. Tag phase-0 when both gates pass.

STEP 2: PHASE 1, WALKING SKELETON
One RSS source -> Ollama (Gemma) summary with schema validation -> ntfy push, plus --dry-run, per the plan.
Include tests: RSS parsing against a saved fixture, the Ollama client with a mocked HTTP layer (valid JSON, invalid JSON, timeout), and the ntfy payload with requests-mock. Include the fallback path.

NON-NEGOTIABLE RULES
1. THE DEV LOOP, for every unit of work: write or adjust a test first, implement, run `ruff format .`, `ruff check .`, `pytest -q`. If red, read the error, fix and rerun. Max 3 attempts per distinct failure, then STOP and report the failing test, the error, what you tried, your hypothesis and options. Run `python -m firstlight run --dry-run` when pipeline, AI, delivery or web code changed. Only then commit.
2. NEVER delete, skip or weaken a test to get green. NEVER use --no-verify.
3. COMMITS: Conventional Commits (`<type>(<scope>): <subject>`, imperative, lowercase, 72 chars max). Small, atomic, one concern per commit. Every commit must pass lint and tests. Commit after every green iteration (at least every 30 to 45 minutes of work) and `git push` after every commit.
4. GIT: work on a short-lived branch per task (`feat/...`, `fix/...`), merge to main only when green, never force-push, never rewrite published history, never commit secrets, data/, logs/ or .env.
5. After every push, update PROGRESS.md (current phase, last green commit, done, in progress, blockers).
6. AGENTS.md section 3 rules apply: code owns dates and the model never produces them; local open-source AI only; fallback must always work; connectors isolated; prefer APIs/RSS/ICS over scraping and check robots.txt and terms; validate all boundaries with pydantic; invent no facts.
7. Stay in scope: P0 first, then P1. Do not start Phase 2 or anything beyond Phase 1.
8. If you must deviate from the docs, or hit something they do not cover, STOP and ask with options and a recommendation.

CHECKPOINTS
Stop after Phase 0 and again after Phase 1. At each stop, report: what was built; test results (counts and coverage); the list of commits (hash and message); manual checks I should do (e.g. confirm the notification arrived on my phone); anything uncertain. Then wait for my "continue".

Begin with STEP 0 now.
```

---

## Prompt 2: Continue a phase (reuse for Phases 2, 4, 5, 6)

```
Continue with Phase <N> from IMPLEMENTATION_PLAN.md. Re-read AGENTS.md and GIT_AND_TESTING_WORKFLOW.md first.
Follow the dev loop (test first, implement, ruff format, ruff check, pytest, smoke test, commit, push, update PROGRESS.md), Conventional Commits, one branch per task, merge to main only when green.
Meet both phase gates from GIT_AND_TESTING_WORKFLOW.md section 3. Tag phase-<N> when they pass.
Stop at the end of the phase and report: what was built, test results, commits, manual checks for me, risks. Do not start the next phase.
```

## Prompt 3: Phase 3, parallel agents (hackathon radar)

```
Start Phase 3 (hackathon radar). Use parallel agents, one branch per agent, per the roles in AGENTS.md:
 - Connector agent(s): one connector per branch (DEV challenges, Devpost, MLH, Kaggle via official API, one web3 source). For each: verify the source manually first, prefer API/RSS, check robots.txt and terms, save a fixture, add a fixture test and a failure test. Stop and ask if a site's terms forbid scraping.
 - Pipeline agent: connector base interface, source_runs logging with per-connector isolation, dedupe (URL, then fuzzy title plus dates), classify (rules first, model for leftovers), with tests.
 - AI agent: the "Should I enter?" verdict and classification prompts with schema validation and the date-safety output guard, with tests.
 - QA agent: reviews every branch before merge; runs the full loop; tries failure cases.
Each agent follows the dev loop and Conventional Commits. Rebase on main before merging; rerun the loop after rebasing. Merge only when green.
Gate: at least 5 working connectors, one real merged duplicate, and a test proving one failing connector does not stop the run. Tag phase-3. Report, then wait.
```

## Prompt 4: Final QA, README and release (Phase 7)

```
Run a full QA and release pass.
1. QA agent: run the full test suite with coverage, try every failure path in APP_FLOW.md section 5 (Ollama down, invalid JSON, connector error, unparseable date, ntfy failure, no urgent items), confirm no secrets or data/ are tracked (`git ls-files`), confirm CI is green on main.
2. Docs agent: write README.md (what it is, screenshots I provide, setup, config, credits for all open-source pieces, and a note on any commits made after the deadline). Draft the DEV post using the outline in IMPLEMENTATION_PLAN.md Phase 7. Use only real measurements and the real quote from my friend that I will provide. Invent nothing.
3. Commit with Conventional Commits, push, tag phase-7, update PROGRESS.md.
Report any issue that blocks submission. Do not publish anything; I will publish the post myself.
```

## Prompt 5: If the agent gets stuck

```
Stop. Do not make further changes. Write a short report: the failing test or command, the exact error, everything you tried, your best hypothesis, and 2 or 3 options with a recommendation. Update PROGRESS.md under "Blocked / needs human". Then wait for me.
```

---

## Tips

- Keep Phase 0 and 1 on a single agent. Parallel agents start paying off in Phase 3.
- Read the commit log (`git log --oneline`) after each phase. It should read like the build story, which also helps the DEV post.
- If you fall behind, tell the agent to apply the cut list in `IMPLEMENTATION_PLAN.md`. Do not cut the fallback, the date-safety tests or the write-up.
