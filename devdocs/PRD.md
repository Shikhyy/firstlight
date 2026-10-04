# First Light: Product Requirements Document (PRD)

> A self-hosted morning assistant. Before you wake up, it gathers your plans, todos, AI news and hackathon deadlines, lets a local open-source AI pick the few things that matter, and puts them on your lock screen.

**Challenge:** Hacktoberfest Weekend Challenge: Build for a Friend (DEV)
**Hard deadline:** Monday, 5 Oct 2026, 12:29 PM IST (06:59 UTC)
**Window rule:** the project and its repo must be started and finished inside the challenge window (from 2 Oct 2026, 02:00 UTC).

---

## 1. Problem

People start the day by opening five apps (calendar, todos, news, email, hackathon sites) and still miss things: a deadline closing tonight, a meeting, a hackathon they would have loved. Existing tools scatter this information or run as closed services that see all of a person's private data.

## 2. Target user

**One real person: the friend we build this for.** Fill in before building:

| Field | Value |
|---|---|
| Name | [FRIEND NAME] |
| Role | [student / developer / other] |
| Phone | [Android / iPhone] |
| Interests (domains) | [AI, ML, Web3, Security, Web, ...] |
| Country / eligibility | [India; student: yes/no] |
| Wake-up time | [06:30] |
| Their biggest morning pain | [one sentence, in their words] |

Everything is tuned to this person. Do not build a generic product.

## 3. Goals

1. Deliver one lock-screen notification each morning with the top 3 things that matter today.
2. Offer a fuller brief page one tap away (plan, todos, AI updates, hackathons).
3. Track hackathons across many platforms and domains with correct deadlines.
4. Keep all personal data local; use only open-source AI.
5. Be reliable: the friend always gets something, even when AI or a source fails.

## 4. Non-goals (this weekend)

- Native mobile app
- Multi-user accounts or login system
- Auto-registering for hackathons
- Email or chat assistant
- Perfect coverage of every hackathon platform

## 5. Features and priority

### P0: must ship

| ID | Feature | Acceptance criteria |
|---|---|---|
| F1 | Source collection | Fetches calendar (ICS), todos (markdown file), AI news (RSS), weather (Open-Meteo) |
| F2 | Deadline math | All date and time logic is plain code in UTC, displayed in Asia/Kolkata |
| F3 | Ranking | Each item gets a score from urgency, relevance, eligibility and novelty |
| F4 | Local AI summary | Gemma via Ollama writes a title, headlines and a "why this matters to you" line for the top items |
| F5 | Lock-screen push | One ntfy notification: a one-line title and the top 3 priorities, with a link to the full brief |
| F6 | Brief page | Web page with plan, todos, AI updates and top hackathons |

### P1: should ship

| ID | Feature | Acceptance criteria |
|---|---|---|
| F7 | Hackathon radar | At least 5 connectors (e.g. DEV, Devpost, MLH, Kaggle, one web3 source) feeding one normalized table |
| F8 | Deduplication | The same event from 2+ platforms is merged into one record with all links |
| F9 | "Should I enter?" verdict | Model reads rules text and returns effort, fit and a short verdict, labelled as a suggestion |
| F10 | Action buttons | Done and Snooze on todos work from the notification |
| F11 | Fallback mode | If AI or a source fails, a plain non-AI brief is still sent |
| F12 | Source health | A page or line showing the last successful run per connector |

### P2: if time allows

- Thumbs up/down feedback that adjusts domain weights
- Audio brief (local TTS or ElevenLabs)
- Suggested day plan from free calendar gaps
- Quick capture ("remind me to ...") parsed by the model

### Future work (mention in the post only)

Chat assistant, mood check-ins, multi-language summaries, weekly recap, multi-user mode, more connectors.

## 6. User stories

- As [FRIEND], I want one glance at my lock screen to tell me what is urgent today.
- As [FRIEND], I want deadlines shown as "closes in 6h", not as dates I must calculate.
- As [FRIEND], I want hackathons filtered to my skills, country and effort level.
- As [FRIEND], I want to mark a todo done without opening an app.
- As [FRIEND], I want my calendar and habits to stay on my own machine.

## 7. Notification design constraints

Lock screens show about 2 to 3 lines.

- **Title:** the day in one line (max 60 chars), e.g. `2 deadlines today · meeting at 11`
- **Body:** top 3 priorities, most urgent first, each max 50 chars
- **Tap:** opens the full brief
- **Buttons:** Done, Snooze 1h, Open
- **Quiet day:** if nothing is urgent, say so instead of padding

## 8. Why open-source AI (required for the challenge post)

- **Privacy:** calendar, todos and routines never leave the machine.
- **Cost:** nothing per brief, forever.
- **Control:** swap models, change ranking and tone, no vendor changing the rules.
- **Extensibility:** anyone can add a new source in about 30 lines.

The post must explain where the open approach worked better than a closed one, with honest limits.

## 9. Success metrics

- Notification arrives at the set time on the friend's phone for at least 2 consecutive mornings.
- Zero incorrect deadlines in the final brief (verified manually against sources).
- At least 5 radar connectors working; at least 1 real duplicate merged.
- Friend's reaction captured in their own words for the post.
- Post published before the deadline with all required sections and tags.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Local model can't run at 6:30 AM (laptop asleep) | Precompute the night before and schedule delivery, or use an always-on machine |
| Scrapers break | Prefer APIs, RSS, ICS; isolate each connector; snapshot tests |
| Small model hallucinates dates | Model never outputs dates; code owns all date math |
| Scope too large for the time | Strict P0, then P1; everything else goes to "future work" |
| Site terms forbid scraping | Check `robots.txt` and terms; use official APIs or feeds where possible |

## 11. Submission requirements (DEV)

- New project built within the window; note any commits after the deadline in the README.
- One submission per person or team (teams up to 4; list DEV handles in the post).
- Post in English to be prize-eligible.
- Tags: `devchallenge`, `weekendchallenge`, `hf26challenge`.
- Sections: What I Built, Demo, Code, How I Built It, Why Does Open Innovation Matter?, optional My Agent Session, Prize Categories.
- Credit any non-trivial prior work or open-source code used.
- Optional partner categories (only if genuinely used): Gemma, Render, DigitalOcean, ElevenLabs, and others.
