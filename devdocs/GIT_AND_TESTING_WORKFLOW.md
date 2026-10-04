# First Light: Git and Testing Workflow

How every piece of work is **built, looped until green, tested, committed (Conventional Commits) and pushed**. Agents must follow this for every task. Humans too.

---

## 1. The dev loop (every unit of work)

```
 ┌──────────────────────────────────────────────────────────────┐
 │ 1. TEST FIRST   write/adjust a test from the acceptance      │
 │                 criteria (it should fail for the right reason)│
 │ 2. IMPLEMENT    smallest change that can pass                │
 │ 3. FORMAT+LINT  ruff format . && ruff check .                │
 │ 4. TEST         pytest -q                                    │
 │      ├─ red  → read the error, fix, go to 3 (see limits)     │
 │      └─ green ↓                                              │
 │ 5. SMOKE        python -m firstlight run --dry-run           │
 │                 (when pipeline, AI, delivery or web changed) │
 │ 6. COMMIT       Conventional Commit, atomic                  │
 │ 7. PUSH         git push                                     │
 │ 8. LOG          update PROGRESS.md                           │
 └──────────────────────────────────────────────────────────────┘
```

### Loop limits (prevents endless loops)
- Max **3 fix attempts per distinct failure**. If still red, stop, and report: the failing test, the error, what was tried, a hypothesis, and options.
- Never delete, skip, or weaken a test just to get green. If a test is wrong, fix it in its own `test:` commit with an explanation.
- Never mark a task done while anything is red.
- A flaky test is a bug: fix it or quarantine it with a written reason in `PROGRESS.md`.

## 2. Test strategy

| Layer | What to test | How |
|---|---|---|
| **Unit** | date normalization, UTC conversion, countdown text, dedupe, classify rules, scoring | pure functions, `freezegun` to fix "now" |
| **Connector** | each connector parses its saved fixture into valid `RawItem`s; failure raises cleanly | fixtures in `tests/fixtures/`, no network |
| **AI** | valid output accepted; invalid JSON, unknown `ref`, timeout, Ollama down all trigger fallback | mocked Ollama client |
| **AI output guard** | headline/why text contains no date or time that was not in the input countdown strings | regex check on model output; reject and retry or fall back |
| **Delivery** | ntfy request has correct URL, Title, Click, Actions headers; retries on failure | `requests-mock` |
| **Web** | `/brief`, `/radar`, `/health` return 200; `done` and `snooze` reject a bad token and change the DB with a good one | Flask test client, temp DB |
| **End to end** | fixtures in, brief out, nothing sent (`--dry-run`), fallback path with `--no-ai` | temp SQLite DB |

Rules:
- **No network in tests.** Everything external is mocked or read from fixtures.
- **Time is injected.** No test depends on the real clock.
- **Each bug fix gets a regression test** in the same PR/commit series.
- **Coverage goal:** at least 80% on `pipeline/`, `ai/`, `delivery/` (`pytest --cov=firstlight`). Coverage is a floor, not the goal; test behavior.

### Test tooling (dev dependencies)
`pytest`, `pytest-cov`, `requests-mock`, `freezegun`, `ruff`.

## 3. Phase gates

A phase is complete only when **both** gates pass.

| Phase | Automated gate | Manual gate |
|---|---|---|
| 0 Setup | `ruff` clean; `pytest` runs (one placeholder test) | Ollama answers a prompt; `curl` to ntfy shows a notification on the phone |
| 1 Skeleton | tests for RSS parse, Ollama client (mocked), ntfy payload | `run` puts a real summarized notification on the phone |
| 2 Core | tests for normalize, countdown, rank, fallback | every countdown in the brief matches a manual check |
| 3 Radar | fixture test per connector; dedupe tests; isolation test (one connector raises, run continues) | spot-check 5 events against their source pages; one real duplicate merged |
| 4 Web UI | route tests (200s) | pages checked on a phone at 390px; contrast and touch targets |
| 5 Interactivity | token tests; action endpoints change DB; AI-down test | tap **Done** on the phone; kill Ollama and still get a notification |
| 6 Deploy | full test suite + CI green | unattended notification at the set time |
| 7 Submit | CI green on `main`; README accurate | post public with tags, before 11:00 AM IST target |

At each gate: tag the commit (`git tag phase-N && git push --tags`) and update `PROGRESS.md`.

## 4. Git workflow

- **`main` is always green and runnable.** Never push failing code to `main`.
- **One short-lived branch per task:** `<type>/<short-desc>`, e.g. `feat/devpost-connector`, `fix/deadline-timezone`.
- Work on the branch, commit often, push the branch regularly.
- **Merge to `main` only when:** lint + tests + (if relevant) dry-run are green. Use fast-forward or `--no-ff` merges; keep history readable.
- Parallel agents: **one branch per agent**; rebase on `main` before merging; resolve conflicts, rerun the loop.
- **Never:** force-push `main`, rewrite published history, commit secrets, commit `data/`, `logs/`, `.env`, `.venv/`.
- Tag each finished phase: `phase-0` ... `phase-7`.

### Commit cadence
- Commit after **every green loop iteration** (every logical unit), and at least every ~30 to 45 minutes of work.
- Push after **every commit** (or at minimum after each finished task).
- **Every commit must pass lint and tests.** No "wip" commits on `main`; on a feature branch a half-done step is allowed only if tests still pass.
- Keep commits **atomic**: one concern per commit (feature, test, docs, refactor, chore separate).

## 5. Conventional Commits

Format:

```
<type>(<scope>): <subject>

[optional body: what and why, wrapped at ~72 chars]

[optional footer: BREAKING CHANGE: ..., Refs: ...]
```

| Type | Use for |
|---|---|
| `feat` | new user-visible capability |
| `fix` | bug fix |
| `docs` | documentation only |
| `style` | formatting only, no logic change |
| `refactor` | code change that neither fixes a bug nor adds a feature |
| `perf` | performance improvement |
| `test` | adding or fixing tests |
| `build` | dependencies, packaging |
| `ci` | GitHub Actions, hooks |
| `chore` | repo upkeep (gitignore, config templates) |
| `revert` | reverting a previous commit |

**Scopes:** `connectors`, `pipeline`, `ai`, `delivery`, `web`, `db`, `config`, `tests`, `docs`, `deps`, `repo`, or a specific name such as `devpost`.

**Subject rules:** imperative mood ("add", not "added"), lowercase, no trailing period, 72 characters max. Breaking changes use `!` and a `BREAKING CHANGE:` footer.

### Examples for this project
```
chore(repo): add gitignore and env example
build(deps): add flask, feedparser and pydantic
feat(connectors): add rss news connector with fixture test
feat(ai): add ollama client with json schema validation
fix(pipeline): mark unparseable deadlines as low confidence
test(ai): cover invalid json fallback path
feat(delivery): send ntfy push with click url and action buttons
refactor(pipeline): extract countdown text helper
feat(web): add radar page with domain filter chips
ci: add github actions workflow for lint and tests
docs(readme): add setup steps and credits
feat(delivery)!: require action token in header

BREAKING CHANGE: action endpoints no longer accept the token as a query param
```

## 6. Enforcement (set up in Phase 0)

### 6.1 Git hooks (stored in the repo)

```bash
mkdir -p .githooks
git config core.hooksPath .githooks
```

`.githooks/commit-msg`:
```bash
#!/usr/bin/env bash
first_line=$(head -n1 "$1")
case "$first_line" in Merge*|Revert*) exit 0 ;; esac
regex='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9_-]+\))?(!)?: .{1,72}$'
if ! echo "$first_line" | grep -Eq "$regex"; then
  echo "Commit message must follow Conventional Commits:"
  echo "  <type>(<scope>): <subject>   e.g. feat(web): add radar page"
  exit 1
fi
```

`.githooks/pre-commit`:
```bash
#!/usr/bin/env bash
set -e
ruff format --check .
ruff check .
pytest -q -x
```

```bash
chmod +x .githooks/commit-msg .githooks/pre-commit
```

Agents must **not** bypass hooks (`--no-verify` is forbidden).

### 6.2 CI: `.github/workflows/ci.yml`

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: ruff format --check .
      - run: ruff check .
      - run: pytest -q --cov=firstlight
```

Use current major versions of the actions. CI needs no Ollama or ntfy because tests mock them.

### 6.3 Git access for agents
Before the agent starts: the remote exists, you are authenticated on the machine (`gh auth login` or SSH key), and `git push` works from the terminal. If the IDE asks to approve terminal commands, allow `git`, `pytest`, `ruff`, `python`, `pip`.

## 7. `PROGRESS.md` (running log, kept at repo root)

Agents update it after every push. Template:

```markdown
# Progress

## Current
- Phase: N
- Branch: <name>
- Last green commit: <hash> <message>

## Done
- [x] Phase 0: ... (tag: phase-0)

## In progress
- [ ] <task> (branch, status)

## Blocked / needs human
- <question, with options and a recommendation>

## Quarantined tests
- <test name>: <reason>

## Notes and assumptions
- ...
```

## 8. Checklist before saying "done"

- [ ] Tests written for the change and all green
- [ ] `ruff format` and `ruff check` clean
- [ ] Smoke test (`run --dry-run`) passes if relevant
- [ ] Failure paths tested (not just the happy path)
- [ ] Conventional commit(s), atomic, pushed
- [ ] CI green on the branch
- [ ] `PROGRESS.md` updated
- [ ] Docs updated if behavior or structure changed
