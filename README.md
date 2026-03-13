# chrisdlg.com

Personal site for Chris De La Garza — Sr. Solutions Engineer. Built with Astro 6 and deployed to Cloudflare Workers.

**Live:** [chrisdlg.com](https://chrisdlg.com)

## Stack

- [Astro 6](https://astro.build) — static output
- [Cloudflare Workers](https://workers.cloudflare.com) — hosting via `@astrojs/cloudflare` adapter
- Vanilla CSS — retro amber/parchment palette (SNES RPG meets Fallout terminal)
- Canvas 2D — animated sprite strip in the footer (hero + dog walking across screen)

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
    resume.astro             # resume with PDF downloads
    doodles.astro
public/
  sprites/                   # me.png, dog.png sprite sheets
  doodles/                   # art
  *.pdf                      # resume downloads (gitignored)
  avatar.png                 # default OG image
```

## Commands

| Command | Action |
| :--- | :--- |
| `npm install` | Install dependencies |
| `npm run dev` | Dev server at `localhost:4321` |
| `npm run build` | Build to `./dist/` |
| `npm run preview` | Preview production build locally |

## Deployment

Pushes to `main` trigger an automatic build and deploy via Cloudflare Workers Git integration.
