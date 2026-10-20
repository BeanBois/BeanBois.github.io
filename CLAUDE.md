# Working in this repo

This repo is **public**. It holds the website's source and a public export of the bank, nothing else.

- `content/` is written by `portfolio/tools/export_site.py`. Never edit it here; change the bank in `portfolio` and re-export. The export leak-scans what it writes.
- Never commit anything from `portfolio` by hand: no bank entries, no `.forbidden`, no private or `ask` projects, no internal employer names.
- `site.yaml` is Kai Shun's file: every word, colour and music setting that isn't a project fact. Put new user-facing text or colours there, never hard-coded in `src/` or `build.py`. [GUIDE.md](GUIDE.md) is his how-to; keep it in step.
- `src/cover.html` is the cover (the record), `src/page.html` is the shell for every other page, and `build.py` puts them together into `dist/`.
- Design work, decisions and the session log live in `portfolio/docs/`. Record changes there, not here.
- Check a change with `python3 build.py` and a local server before pushing: a push to `main` deploys.
