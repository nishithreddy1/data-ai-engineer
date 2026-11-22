# Content Checklist — Do These Before Publishing

The code is fixed. These are the **content truths only you can confirm**. Nothing here blocks local preview;
items 1–2 block a public launch.

## 1. Contact details (required)

In `index.html` (or `src/js/data.js`), set:

- [ ] `CONFIG.email` — your real professional email. Until set, the form shows a "not configured" message.
- [ ] `CONFIG.linkedin` — full profile URL, or leave `""` to hide the button.
- [ ] `CONFIG.github` — full profile URL, or leave `""` to hide the button.
- [ ] `CONFIG.resumeUrl` — drop `resume.pdf` next to `index.html` and set `"resume.pdf"`, or leave `""`.

## 2. Experience claims (required)

- [ ] **"5 yrs" stat** — confirm the exact duration. If it's "5+ years" or a different number, edit the hero stat.
- [ ] **Journey section** — currently capability-led with no employer names/dates (by design in the original).
      For job applications, add: employer names, job titles, date ranges, and 1–2 measurable outcomes per role
      (e.g. "cut load failures X%", "migrated N jobs"). Keep client details generic if under NDA.
- [ ] **Hero title** — "Data Engineer · Data + AI Practitioner" — confirm this matches your current title.

## 3. Skill levels (review each dot)

Defaults set in v2.0.0 — change `level` in `SKILLS` if wrong:

| Group | Default | Your call |
|---|---|---|
| Data Engineering (DataStage…) | Hands-on | ☐ |
| Databases & SQL (Teradata…) | Hands-on | ☐ |
| Big Data (PySpark…) | Working knowledge | ☐ |
| Cloud & Platforms (GCP…) | Working knowledge | ☐ |
| Programming (Python…) | Hands-on | ☐ |
| DevOps & Scheduling | Working knowledge | ☐ |
| Machine Learning | Currently learning | ☐ |
| Generative AI | Currently learning | ☐ |

Rule: if you couldn't defend it in an interview, downgrade it. The dot is a promise.

## 4. Project statuses (update as things ship)

All 11 projects are currently Concept / Direction / Planning / Specification — honest today.
When one ships, change its `status` (e.g. `"Built · Live"`) and add a link in the brief.
Priority candidates to actually build first (they're your strongest portfolio pieces):
DataPilot ML Studio, Data Cleansing Assistant, MockData Generator.

## 5. Sharing / SEO (after you pick a domain)

- [ ] Set `og:url` to your live URL.
- [ ] Set `og:image` to a 1200×630 preview image URL (screenshot of the hero works).
- [ ] Add `<link rel="canonical" href="https://yourdomain/">` in `<head>`.
- [ ] Test the share preview (LinkedIn Post Inspector / Twitter Card Validator).

## 6. Final pass

- [ ] Open on your phone: menu, theme toggle, project filter, modal, form.
- [ ] Send yourself a test message through the form.
- [ ] Proofread names/dates once, out loud.
- [ ] Keep `docs/original-index.html` as backup — don't deploy it.
