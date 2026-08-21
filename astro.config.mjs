// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// No adapter: every page is prerendered, so the site deploys as an
// assets-only Worker (see wrangler.jsonc) with no server bundle. If a
// dynamic route ever appears, re-add @astrojs/cloudflare here and restore
// main/binding in wrangler.jsonc.
export default defineConfig({
  output: 'static',
  site: 'https://chrisdlg.com',
  integrations: [
    sitemap({
      // /arcade is live but unlisted until the deck-lore post ships.
      filter: (page) => !page.includes('/arcade'),
    }),
  ],
  vite: {
    build: {
      // Never inline component <script>s into HTML — external files let
      // the _headers CSP stay at script-src 'self' (no unsafe-inline).
      assetsInlineLimit: 0,
    },
  },
});