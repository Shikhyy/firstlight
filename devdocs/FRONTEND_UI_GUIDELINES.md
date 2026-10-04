# First Light: Frontend UI Guidelines

Visual reference: the three-screen mockup canvas (lock screen, full brief, hackathon radar): https://claude.ai/artifact/RXJvkf7dPhNTbnkDVkvm8m

Mood: **dawn**. Deep midnight background, slow drifting colored glows, frosted glass cards, one warm accent.

> The lock screen is rendered by the phone OS via ntfy. The mockup is illustrative. Our real UI is `/brief`, `/radar` and `/health`.

---

## 1. Principles

1. **Glanceable first.** The most important thing is readable in 2 seconds.
2. **Calm, not noisy.** Motion is slow and purposeful.
3. **Mobile first.** Design at 390px wide, then scale up with `max-width`.
4. **Accessible.** Contrast, touch targets, reduced motion.
5. **No framework.** Jinja templates, one CSS file, a little vanilla JS.

## 2. Design tokens

```css
:root {
  /* Surfaces */
  --bg: #0b1020;
  --glass: rgba(255, 255, 255, 0.10);
  --glass-border: rgba(255, 255, 255, 0.22);
  --glass-highlight: rgba(255, 255, 255, 0.28);

  /* Glow orbs (background only) */
  --orb-violet: #7b5cff;
  --orb-teal: #2ee6c5;
  --orb-coral: #ff8a5c;

  /* Accent */
  --accent: #ffb27a;        /* buttons, section labels, countdowns */
  --accent-strong: #ff8a5c; /* urgency bar, pulse dot */
  --on-accent: #1a1028;     /* text on accent buttons */

  /* Text */
  --text: #ffffff;
  --text-body: rgba(255, 255, 255, 0.88);
  --text-muted: rgba(255, 255, 255, 0.74);

  /* Shape and space */
  --radius-card: 22px;
  --radius-btn: 14px;
  --radius-chip: 22px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-5: 20px; --space-6: 28px;
}
```

## 3. Typography

| Use | Font | Weight | Size |
|---|---|---|---|
| Big clock / page titles | Fraunces (serif) | 600 | 32 to 34px titles, 104 to 112px clock |
| Body, labels, buttons | DM Sans | 400 / 500 / 700 | 14 to 17px |
| Section labels | DM Sans, uppercase, `letter-spacing: 0.1em` | 700 | 12px, accent color |

Load via Google Fonts with fallbacks: `'Fraunces', Georgia, serif` and `'DM Sans', system-ui, sans-serif`.

## 4. Glass card (the core component)

```css
.glass {
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-card);
  padding: var(--space-4);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  box-shadow: 0 8px 32px rgba(5, 5, 20, 0.35),
              inset 0 1px 0 var(--glass-highlight);
}
@supports not (backdrop-filter: blur(1px)) {
  .glass { background: rgba(30, 34, 51, 0.92); }
}
```

Glass only looks good over color. Always render the glow orbs behind content.

## 5. Background glows

Three blurred circles, `position: absolute`, `filter: blur(70px)`, opacity 0.35 to 0.6, inside a `position: relative; overflow: hidden` page wrapper. Content sits above with `position: relative; z-index: 1`.

| Orb | Color | Position | Drift |
|---|---|---|---|
| 1 | violet | top right | `drift1` 12s |
| 2 | teal | middle left | `drift2` 14s |
| 3 | coral | bottom right | `drift1` 16s reverse |

## 6. Animation

```css
@keyframes drift1 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(34px,46px) scale(1.18)} }
@keyframes drift2 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(-44px,30px) scale(1.12)} }
@keyframes rise   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none} }
@keyframes pulse  { 0%{box-shadow:0 0 0 0 rgba(255,138,92,.75)} 100%{box-shadow:0 0 0 10px rgba(255,138,92,0)} }
@keyframes grow   { from{transform:scaleX(0)} to{transform:scaleX(1)} }
@keyframes shimmer{ to{background-position:200% center} }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

| Element | Animation |
|---|---|
| Cards | `rise .7s ease-out both`, staggered `animation-delay` (0.15s steps) |
| Countdown badge | pulsing dot, `pulse 1.8s infinite` |
| Urgency bar | `grow 1.3s ease-out`, `transform-origin: left` |
| Buttons | lift on hover: `translateY(-2px)`, `transition .2s` |
| Orbs | slow `drift` loops |

Keep motion subtle; never animate text content that the friend must read quickly.

## 7. Components

| Component | Spec |
|---|---|
| **GlassCard** | Section 4; flex column, gap 8px |
| **SectionLabel** | 12px uppercase, accent color |
| **Button (primary)** | bg `--accent`, text `--on-accent`, min-height 44px, radius 14px, weight 700 |
| **Button (secondary)** | translucent white bg, 1px light border, white text, min-height 44px |
| **Chip (filter)** | min-height 44px, radius 22px; active = accent bg + dark text |
| **CountdownBadge** | accent text, bold; pulse dot if under 24h |
| **UrgencyBar** | 6px high track `rgba(255,255,255,.15)`, fill `--accent-strong` |
| **TodoRow** | real `<input type="checkbox">` with `accent-color: var(--accent)` and a `<label>` |
| **SourceHealthLine** | 13px muted text: "all connectors OK · last run 5:30 AM" |

## 8. Screens

### `/brief` (390px wide, scrolls)
1. Header: date, weather line, "Good morning, {name}" (Fraunces).
2. **Today's plan** card: events plus free-slot hint.
3. **Todos** card: checkbox rows.
4. **AI updates** card: headline plus "why it matters to you".
5. **Hackathon radar** card: top event with countdown.
6. Footer: Useful / Less of this (P2).

### `/radar`
1. Title "Hackathon radar".
2. Filter chips (horizontal scroll).
3. Event cards: domain and platforms, countdown, name, verdict, urgency bar.
4. Source-health line.

### `/health` (builder only, plain style is fine)
Table: connector, last run, status, items found, error.

## 9. Accessibility checklist

- Text contrast at least 4.5:1 (3:1 for 24px and larger). Check text on glass over every orb color.
- Touch targets at least 44px.
- Use real `<button>`, `<a>`, `<input>` + `<label>`; never click handlers on divs.
- Icon-only controls need `aria-label`.
- Do not rely on color alone for urgency; include the text countdown.
- Respect `prefers-reduced-motion` (Section 6).
- No emoji as icons; use inline SVG if icons are needed.

## 10. Responsive rules

- Base layout 390px; wrapper `max-width: 480px; margin: 0 auto`.
- Wide content (tables) scrolls inside its own `overflow-x: auto` container.
- Use `rem` and `%`, not fixed pixel widths, for containers.

## 11. Copy tone

Friendly and short. Use the friend's name once in the header. "Quiet day. Nothing urgent." beats padding. Always label AI judgments as suggestions ("Should I enter?"). Deadlines always appear as countdowns, backed by code-computed times.
