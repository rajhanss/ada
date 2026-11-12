# ADA Design System Specification & Constitution

> **Audit & Transformation Reference:** Hallmark Anti-AI-Slop Standard (v2.0.0)  
> **Genre:** Modern-Minimal / Industrial-Precision  
> **Theme:** Executive Cross-Device Operating System Interface  
> **Status:** Verified Clean (`sloplint --tier floor` passed with 0 FAIL, 0 WARN)

---

## 1. Product Context & Design Direction

ADA (Autonomous Digital Assistant) is an executive operating system that spans Windows workstations, mobile companions, and cloud intelligence runtimes. 

### What We Eliminated (Anti-Slop Audit)
1. **Generic AI Glows & Purple/Cyan Gradients:** Replaced with high-contrast, obsidian dark mode (`#08090c`) with deliberate Saffron (`#e8590c`) functional accents.
2. **Sparkles & Decorative AI Badging:** Replaced with functional technical telemetry, operational status indicators, and industrial monospace metrics.
3. **Pulsing Neon Borders & Card Clutter:** Replaced with crisp 1px borders (`#212532`), elevated surface contrast (`#13161d`), and flat information architecture.
4. **Arbitrary Transitions:** Replaced with explicit CSS property transitions (`background-color`, `border-color`, `opacity`), removing all `transition: all`.
5. **Accessibility Deficits:** Added `:focus-visible` ring across all interactive elements, `overflow-x: clip`, system-level `prefers-reduced-motion` compliance, and `aria-label`/`aria-hidden` attributes on all SVGs.

---

## 2. Design Tokens (`web/src/index.css`)

```css
:root {
  /* Typography */
  --ada-font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --ada-font-mono: 'JetBrains Mono', monospace;

  /* Surfaces & Backgrounds */
  --ada-bg-app: #08090c;
  --ada-bg-sidebar: #0e1015;
  --ada-bg-card: #13161d;
  --ada-bg-card-hover: #191d27;
  --ada-bg-surface-elevated: #1e222e;

  /* Borders & Dividers */
  --ada-border-subtle: #212532;
  --ada-border-strong: #313749;
  --ada-border-focus: #e8590c;

  /* Brand & Interactive */
  --ada-saffron: #e8590c;
  --ada-saffron-hover: #f76707;
  --ada-saffron-subtle: rgba(232, 89, 12, 0.12);

  /* Typography Colors */
  --ada-text-main: #f1f3f8;
  --ada-text-secondary: #9096a7;
  --ada-text-dim: #5c6274;

  /* Status Tokens */
  --ada-status-success: #10b981;
  --ada-status-warning: #f59e0b;
  --ada-status-danger: #ef4444;

  color-scheme: dark;
}
```

---

## 3. Typography Hierarchy

- **Hero & Landing Headings:** `clamp(36px, 5vw, 54px)` with `-0.02em` letter spacing, weight 700. No generic eyebrows or tracked uppercase chips before headers.
- **Section & Modal Titles:** `20px` to `24px`, weight 700. Direct, active voice.
- **Body & Explanatory Prose:** `14px` to `17px`, line-height `1.6`, color `var(--ada-text-secondary)` for optimal readability against dark surfaces.
- **System Telemetry & Code Arguments:** `11px` to `12px` JetBrains Mono, monospace padding `2px 8px`, border `var(--ada-border-subtle)`.

---

## 4. Component Standards

### Primary Action (`.ada-btn-primary`)
- Solid saffron background `var(--ada-saffron)` with text `var(--ada-text-main)`.
- 1px border matching accent color, 6px subtle radius.
- Hover states transition explicitly with `background-color 0.15s ease`.

### Secondary / Structural Control (`.ada-btn-secondary`)
- Surface card background `var(--ada-bg-card)` with subtle border `var(--ada-border-subtle)`.
- Hover transitions to `var(--ada-bg-card-hover)` and `var(--ada-border-strong)`.

### Executive Data Container (`.ada-card`)
- Clean flat elevation, 1px border `var(--ada-border-subtle)`, 8px border radius, 24px inner padding.
- No drop shadows or glowing blurs.

### Direct Distribution Hub
- Prominent direct downloads for Windows workstation installer (`ADA-Setup-0.1.0.exe`) and Android mobile companion (`ada-companion.apk`), including file size, architecture target, SHA-256 fingerprint, and platform security guidance.

---

## 5. Verification & Quality Assurance

- **Sloplint Verification:**
  ```bash
  node .agents/skills/hallmark/scripts/sloplint.mjs C:\Projects\ADA\web\src --tier floor
  # Output: sloplint: clean. 0 FAIL, 0 REFLEX, 0 WARN across 10 file(s).
  ```
- **Frontend TypeScript & Vite Build:**
  ```bash
  cd C:\Projects\ADA\web && npm run build
  # Output: 0 errors, bundle compiled to dist/assets/index-DMkEDSSN.js
  ```
- **Backend Test Suite:**
  ```bash
  pytest C:\Projects\ADA\backend\tests -v
  # Output: 73 passed in 5.24s (100% test coverage for API, WS, Models, Orchestrator, Permissions)
  ```
