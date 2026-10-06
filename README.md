# chrisdlg.com

Personal site for Chris De La Garza — Staff Solutions Engineer. Built with Astro 6 and deployed to Cloudflare Workers.

**Live:** [chrisdlg.com](https://chrisdlg.com)

## Stack

- [Astro 6](https://astro.build) — static output
- [Cloudflare Workers](https://workers.cloudflare.com) — hosting as an assets-only Worker (static assets, no server bundle)
- Vanilla CSS — retro amber/parchment palette (SNES RPG meets Fallout terminal)
- Canvas 2D — animated sprite strip in the footer (user + dog walking across screen)

## Structure

```
src/
  layouts/BaseLayout.astro   # shared HTML shell, OG tags, game strip animation
  components/
    Nav.astro
    Footer.astro
  pages/
    index.astro              # home / about
    blog/                    # markdown blog posts
    projects.astro
    resume.astro             # resume, rendered from src/data/resume.json
  data/
    resume.json              # SINGLE SOURCE for /resume and the three PDFs
    doodles.astro
    rss.xml.ts               # RSS feed
    404.astro                # custom 404 page
public/
  sprites/                   # me.png, dog.png sprite sheets
  doodles/                   # art
  *.pdf                      # resume downloads, generated (see below)
scripts/
  build_resume_pdfs.py       # resume.json -> public/*.pdf
  avatar.png                 # default OG image
```

## Commands

| Command | Action |
| :--- | :--- |
| `npm install` | Install dependencies |
| `npm run dev` | Dev server at `localhost:4321` |
| `npm run build` | Build to `./dist/` |
| `npm run preview` | Preview production build locally |

## Updating the resume

Edit `src/data/resume.json`, then rebuild the PDFs so they match the page:

```sh
python3 -m venv .venv-resume && .venv-resume/bin/pip install reportlab
.venv-resume/bin/python scripts/build_resume_pdfs.py
```

It writes the dark, light and 1-page PDFs to `public/`. Bullets marked
`"onepage": true` are the ones kept on the 1-page cut, and the script exits
non-zero if that cut spills onto a second page.

## Deployment

Pushes to `main` trigger an automatic build and deploy via Cloudflare Workers Git integration.
