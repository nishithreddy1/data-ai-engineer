# Deploy Guide — Nishith Portfolio

This is a static site: no server, no database, no build step. Any static host works.
Deploy **`index.html`** (single-file build) unless you prefer the split `src/` build.

## Option A — Netlify (fastest, free)

1. Go to app.netlify.com → "Add new site" → "Deploy manually".
2. Drag the folder containing `index.html` onto the page.
3. Done — you get a `*.netlify.app` URL. Add a custom domain under Site settings → Domain management.

## Option B — Vercel (free)

1. vercel.com → "Add New → Project" → import a Git repo containing `index.html`, **or** use the CLI:
   ```bash
   npm i -g vercel && cd nishith-portfolio && vercel --prod
   ```
2. Framework preset: "Other". No build command, output directory = current folder.

## Option C — GitHub Pages (free)

1. Create a repo, push `index.html` (and `resume.pdf` if used) to `main`.
2. Repo → Settings → Pages → Source: `main` / root.
3. Live at `https://<username>.github.io/<repo>/` in ~1 minute.

## Option D — Cloudflare Pages (free)

1. dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets.
2. Upload the folder with `index.html`. Add custom domain in the project settings.

## Custom domain checklist (any host)

- [ ] Point DNS per host instructions (CNAME / A records), wait for HTTPS cert.
- [ ] Set `og:url` + canonical to the real domain (see CONTENT-CHECKLIST §5).
- [ ] Re-test the contact form on the live URL (mailto works everywhere).

## If you later want real form submissions (no mailto)

Swap the submit handler for a form service — no backend needed:

- **Formspree** (formspree.io): create a form, POST to `https://formspree.io/f/<id>`.
- **Netlify Forms**: add `data-netlify="true"` to the `<form>` when hosted on Netlify.
- **Web3Forms** (web3forms.com): free access-key based endpoint.

Ask me to wire one in when you're ready — it's a ~15-line change in `app.js`.

## Updating the site later

Edit `src/js/data.js` (content) or `src/css/styles.css` (look), then re-deploy the `src/` folder —
or keep using the single-file build and edit its matching blocks. Don't edit both builds in parallel;
pick one as your source of truth.
