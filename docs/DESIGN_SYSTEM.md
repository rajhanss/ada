# ADA — Design System

**Version:** 0.1.0 | Inspiration: Intentional simplicity. Premium without excess.

---

## 1. Brand Identity

**Primary identity:** Indian gerua / bhagwa — saffron orange.  
Used selectively for identity, active states, and important actions.  
**The interface is not orange. Saffron is an accent.**

---

## 2. Design Tokens

```css
:root {
  /* Brand */
  --ada-saffron:   #E87518;   /* Primary brand, CTAs, active states */
  --ada-orange:    #FF9933;   /* Accent, hover states */
  --ada-saffron-10: rgba(232, 117, 24, 0.10);  /* Subtle backgrounds */
  --ada-saffron-20: rgba(232, 117, 24, 0.20);  /* Selection, focus rings */

  /* Neutrals — Light Mode */
  --ada-ivory:     #F7F4EE;   /* Background canvas */
  --ada-white:     #FFFFFF;   /* Card surfaces */
  --ada-stone:     #D9D5CE;   /* Borders, dividers */
  --ada-muted:     #77736D;   /* Secondary text */
  --ada-charcoal:  #171717;   /* Primary text */

  /* Neutrals — Dark Mode */
  --ada-dark-bg:   #111110;
  --ada-dark-surface: #1C1C1A;
  --ada-dark-border:  #2E2E2B;
  --ada-dark-muted:   #77736D;
  --ada-dark-text:    #F0EDE8;

  /* Semantic */
  --ada-success:   #22C55E;
  --ada-warning:   #F59E0B;
  --ada-error:     #EF4444;
  --ada-info:      #3B82F6;

  /* Typography */
  --font-sans: 'Inter Variable', 'SF Pro Display', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Spacing (8px base grid) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;

  /* Radii */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm:  0 1px 3px rgba(0,0,0,0.08);
  --shadow-md:  0 4px 16px rgba(0,0,0,0.10);
  --shadow-lg:  0 8px 32px rgba(0,0,0,0.14);
  --shadow-orb: 0 8px 40px rgba(232, 117, 24, 0.25);

  /* Motion */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 120ms;
  --duration-normal: 200ms;
  --duration-slow: 350ms;
}
```

---

## 3. Typography Scale

| Token | Size | Weight | Use |
|---|---|---|---|
| `--text-xs` | 11px | 400 | Timestamps, labels |
| `--text-sm` | 13px | 400 | Secondary text, captions |
| `--text-base` | 15px | 400 | Body text, messages |
| `--text-md` | 17px | 500 | Interface labels |
| `--text-lg` | 20px | 600 | Section headings |
| `--text-xl` | 24px | 700 | Page headings |
| `--text-2xl` | 32px | 700 | Display headings |

Line height: 1.5× for body, 1.25× for headings. Letter spacing: -0.01em for large headings.

---

## 4. The ADA Orb (Desktop)

The floating orb is ADA's primary desktop presence. It is the brand made visible.

### Orb States

| State | Visual |
|---|---|
| **Idle** | Soft saffron gradient sphere, subtle breathing pulse (3s cycle, 2% scale) |
| **Listening** | Orb expands 10%, animated ring emanates outward, brighter saffron |
| **Processing** | Rotating gradient arc around orb, opacity pulse |
| **Speaking** | Orb gently oscillates vertically in sync with audio amplitude |
| **Task Running** | Thin progress ring around orb, task color (blue) |
| **Attention Required** | Orange glow pulse — approval needed |
| **Error** | Brief red flash → returns to idle |

Orb diameter: 56px collapsed, 72px expanded, 48px minimal.

---

## 5. Component Vocabulary

### Message Bubbles
- User messages: right-aligned, `--ada-saffron-10` background.
- ADA messages: left-aligned, `--ada-white` or `--ada-dark-surface` background.
- System messages: centered, `--ada-muted` text, no background.
- Tool results: collapsible, monospace font, light border.

### Status Indicators
- 🟢 Green dot: device connected, task succeeded.
- 🟡 Yellow dot: device reconnecting, task running.
- 🔴 Red dot: device offline, task failed.
- 🟠 Saffron dot: approval pending.

### Permission States
- Allowed: subtle green indicator on tool.
- Requires approval: saffron badge.
- Denied: muted, non-interactive.
- Not configured: grey, with setup prompt.

### Empty States
Every empty state has:
- An illustrative icon (not generic).
- A concise explanation.
- A single clear action.

Example: Empty conversations → "Start a conversation with ADA" → [Open] button.

---

## 6. Motion Principles

- **Purposeful:** Every animation communicates state change, not decoration.
- **Fast:** UI response animations ≤ 200ms. Page transitions ≤ 350ms.
- **Consistent:** Same easing curve (`--ease-out`) throughout.
- **Respectful:** Respect `prefers-reduced-motion`. All animations can be disabled.

No spinning loaders — use skeleton screens for content loading.  
No bouncing — subtle slide and fade only.

---

## 7. Web Dashboard Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ┌────────────┐  ┌──────────────────────────────────────┐   │
│  │ Sidebar    │  │  Main Content                        │   │
│  │            │  │                                      │   │
│  │ ADA logo   │  │  Breadcrumb navigation               │   │
│  │            │  │                                      │   │
│  │ Navigation │  │  Page content                        │   │
│  │  - Chat    │  │  (conversations / tasks / settings)  │   │
│  │  - Tasks   │  │                                      │   │
│  │  - Devices │  │                                      │   │
│  │  - Memory  │  │                                      │   │
│  │  - Settings│  │                                      │   │
│  │            │  │                                      │   │
│  │ [User]     │  │                                      │   │
│  └────────────┘  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

Sidebar: 240px fixed on desktop, collapsible to icon-only (60px), hidden on mobile (bottom nav).

---

## 8. Accessibility Standards

- WCAG 2.1 AA contrast minimum.
- Full keyboard navigation.
- ARIA labels on all interactive elements.
- Focus indicators clearly visible.
- Screen reader support (VoiceOver / NVDA).
- Touch targets minimum 44×44px on mobile.
- No information conveyed by colour alone.

---

## 9. PySide6 Implementation Notes

- Use `QSS` stylesheets driven by design tokens (auto-reload in dev).
- Custom widgets extend `QWidget` — no unmodified default components in the visible UI.
- Use `QGraphicsDropShadowEffect` sparingly (GPU cost on Windows).
- Orb rendered via `QPainter` with `QConicalGradient` + `QTimer` animation loop.
- System tray icon follows Windows accent colour when possible.

---

## 10. Design Consistency Checklist

Before shipping any UI:
- [ ] Uses design tokens — no hardcoded colors or sizes.
- [ ] Dark mode tested.
- [ ] Loading state defined (skeleton, not spinner).
- [ ] Empty state defined.
- [ ] Error state defined.
- [ ] Permission state displayed correctly.
- [ ] Keyboard accessible.
- [ ] Contrast ratio passes AA.
- [ ] Animation respects `prefers-reduced-motion`.
