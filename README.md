# dialectforge.com

Static site for DialectForge LLC, served by GitHub Pages from `main`.

- Plain HTML/CSS with one small JS file (`assets/js/df.js`). No framework, no build step needed to serve.
- Fonts are self-hosted in `assets/fonts/` (Archivo, Source Serif 4, JetBrains Mono, all SIL Open Font License).
- `_src/build.py` regenerates the pages from `_src/pages/*.html` (content fragments) and re-wraps the legal/support pages
  from `_src/orig/` (their wording stays unchanged). Run `python3 _src/build.py` from the repo root, then commit the output.
  `_src/` is ignored by GitHub Pages' Jekyll build (leading underscore).
- `reset-password/` is a standalone page and isn't generated.

Contact: info@dialectforge.com
