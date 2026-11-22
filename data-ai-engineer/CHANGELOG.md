# Changelog — Nishith Portfolio

## v2.0.0 — Production fix (2026-11-20)

Source: `docs/original-index.html` (your uploaded file, 30,888 bytes, preserved untouched).

### Removed (publish blockers)
- 5 visible `.notice` warning boxes that told visitors the content was unverified:
  experience-duration disclaimer, portfolio-accuracy note, employment-chronology disclaimer,
  "add your email/LinkedIn/GitHub" instruction, and "configure your email" form note.
  → Moved to `docs/CONTENT-CHECKLIST.md` as owner tasks.
- Asterisk on "5 yrs" stat (the footnote it pointed to is gone).
- Placeholder `CONTACT_EMAIL = 'your.email@example.com'` and its blocking `alert()`.

### Added
- `CONFIG` block (`email`, `linkedin`, `github`, `resumeUrl`) — the only block you must edit.
  Social/résumé buttons render only when set.
- Copy-email button (Clipboard API with fallback message).
- Inline form validation (empty fields, email format) with `aria-live` messages — no `alert()`.
- Open Graph + Twitter card meta, `theme-color`, inline SVG favicon, JSON-LD `Person` schema.
- Inter font loading (`preconnect` + `display=swap`) — the original referenced Inter but never loaded it.
- Skill proficiency markers (Hands-on / Working knowledge / Currently learning) + legend —
  this replaces the old accuracy warning box with honest UI.
- Result count ("Showing X of 11 projects", `aria-live`) on the project filter.
- Skip-to-content link, back-to-top link, `noscript` message, print stylesheet.
- Split-source build under `src/` (HTML/CSS/JS/data separated) alongside the single-file build.

### Changed
- Theme: `body.light` class → `html[data-theme]` + CSS variables. Now respects
  `prefers-color-scheme`, persists choice in `localStorage`, set before first paint (no flash).
  Toggle button updates icon + `aria-label`/`aria-pressed`.
- Mobile menu: added `aria-expanded`, `aria-controls`, dynamic label.
- Project filters: `.active` class → `aria-pressed`; filtering uses `hidden` attribute.
- Modal: `hidden` attribute + focus trap + Escape + focus return to the opening button + body scroll lock.
- Scrollspy: scroll listener → `IntersectionObserver`.
- Capabilities / skills / projects: hard-coded HTML → rendered from JS data arrays (single source of truth, HTML-escaped).
- Removed inline `style="color:var(--muted)"` attributes in favour of classes.
- Minimum touch targets (42px icon buttons, 36px filters); `:focus-visible` rings; `prefers-reduced-motion` support.

### Verified
- All JavaScript passes `node --check` (single-file blocks + `src/js/data.js` + `src/js/app.js`).
- No leftover placeholder strings (`your.email@example.com`, warning-box text) in the production build.
- 11 projects render from data; filter counts verified in code.

### Not changed (your call — see CONTENT-CHECKLIST)
- "5 yrs" experience figure, skill groupings/levels, project statuses, journey wording,
  domain/OG image — these are content truths only you can confirm. Defaults are marked in the checklist.
