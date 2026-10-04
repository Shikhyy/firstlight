# First Light: App Flow

How the product behaves from the friend's point of view, and what the system does behind the scenes.

---

## 1. A day in the friend's life

| Time (IST) | What happens |
|---|---|
| 22:00 | *(P2, optional)* Night check-in: "Tomorrow: busy / okay / free?" |
| 05:30 | System runs silently: collect, clean, rank, summarize |
| 06:30 | Lock-screen notification arrives |
| Any time | Friend taps the notification to open the full brief |
| Daytime | Optional nudge when something changes (P2) |
| 18:00 | *(P2, optional)* "Closing soon" nudge for items ending within 48h |

## 2. Friend-facing flows

### 2.1 Read the morning notification
1. Notification shows title (the day in one line) and 3 priorities.
2. Friend either ignores it (they got what they needed) or taps it.
3. Tap opens `/brief` (the full brief page).

### 2.2 Mark a todo done from the lock screen
1. Friend taps **Done** on the notification.
2. ntfy sends an HTTP request to `POST /api/todos/<id>/done` with a secret token.
3. Backend marks the todo done. The item disappears from tomorrow's brief.

### 2.3 Snooze
1. Friend taps **Snooze 1h**.
2. `POST /api/todos/<id>/snooze` sets `snoozed_until = now + 1h`.
3. The item is hidden until that time.

### 2.4 Browse hackathons
1. From the brief, tap "Hackathon radar" to open `/radar`.
2. Filter chips: All, AI, ML, Web3, Online (more optional).
3. Each card shows domain, platforms, countdown, urgency bar and a "Should I enter?" verdict.
4. Tap a card to open the original event link.

### 2.5 Give feedback *(P2)*
1. Friend taps **Useful** or **Less of this** on the brief.
2. `POST /api/feedback` stores the vote.
3. Domain weights adjust slightly; tomorrow's ranking shifts.

## 3. Screens and navigation

```
Notification (ntfy, rendered by the OS)
      │ tap
      ▼
 /brief  ──────────────►  /radar
   │  (hackathon card)       │ (event card)
   │                         ▼
   │                   External event page
   ▼
 /health  (source health, for the builder)
```

| Screen | Purpose | Key content |
|---|---|---|
| Notification | Glanceable summary | Title, 3 priorities, Done / Snooze / Open |
| `/brief` | Full morning brief | Plan, todos, AI updates, top hackathon, feedback |
| `/radar` | All hackathons | Filters, cards, verdicts, source-health line |
| `/health` | Builder diagnostics | Last run and status per connector |

## 4. System pipeline (the 5:30 AM run)

```
 Scheduler
    │
    ▼
 1 COLLECT  ── calendar · todos · RSS · hackathon connectors · weather
    │          (parallel, each isolated)
    ▼
 2 NORMALIZE ─ parse dates (code), convert to UTC, validate
    │
    ▼
 3 DEDUPE ──── merge same event across platforms; drop already-seen items
    │
    ▼
 4 CLASSIFY ── keyword rules first; local model only for ambiguous items
    │
    ▼
 5 RANK ────── urgency + relevance + eligibility + effort/reward + novelty
    │
    ▼
 6 SUMMARIZE ─ local model: title, headlines, "why this matters to you"
    │
    ▼
 7 DELIVER ─── ntfy push + save brief for /brief
    │
    ▼
 8 LOG ─────── briefs, brief_items, source_runs, timings, errors
```

### Stage rules
- **Collect:** each connector has its own timeout and refresh interval. A failure is logged and skipped.
- **Normalize:** the model never decides a date. Anything that fails validation is flagged with low confidence and excluded from the notification.
- **Dedupe:** match on canonical URL, then fuzzy title plus overlapping dates, then (optional) embedding similarity.
- **Classify:** fixed taxonomy: `ai`, `ml`, `web3`, `security`, `web`, `hardware`, `opensource`, `gamedev`, `social_good`.
- **Rank:** formula in `BACKEND_AND_SCHEMA.md`.
- **Summarize:** only the top N (about 5) items reach the model; output must be strict JSON.
- **Deliver:** one POST to the ntfy topic with title, body, click URL and action buttons.

## 5. Failure flows

| Failure | Behaviour |
|---|---|
| One source down | Skip it, log in `source_runs`, continue |
| Ollama unreachable or invalid JSON (after 1 retry) | **Fallback mode:** build the brief from ranked items with templated text, no AI |
| ntfy POST fails | Retry up to 3 times with backoff; brief page is still saved |
| No items score above threshold | Send a "Quiet day" notification |
| Date cannot be parsed | Item excluded from notification, kept in DB with low confidence |

## 6. Scheduling modes

| Mode | How | Trade-off |
|---|---|---|
| **A. Always-on machine** (Pi, spare laptop, small server) | Cron at 05:30 runs the pipeline and sends the push | Truly self-hosted; needs a machine that stays on |
| **B. Precompute and schedule** | Run the pipeline the night before on the laptop, schedule delivery for 06:30 using ntfy's delayed-delivery feature | Simple; brief may be slightly stale |

Verify the ntfy delayed-delivery header syntax in the ntfy docs before relying on mode B.

## 7. Notification payload (target)

```
Title:    2 deadlines today · meeting at 11
Body:     1. DEV challenge closes in 6h
          2. Submit assignment by 5 PM
          3. New Gemma release worth a look
Click:    https://<your-host>/brief
Actions:  Done (POST /api/todos/<id>/done), Snooze 1h, Open
```

Action endpoints require a secret token. The phone must be able to reach the server (public URL or tunnel) for buttons to work.
