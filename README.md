# personal_website

Teoh Kai Shun's personal site: every project, big or small, laid out as a manga series, with a record on the cover.

| Page | What it is |
|---|---|
| `index.html` (表紙, cover) | The record, half out of its sleeve. Projects sit on the record (a Poincaré ball, placed by their mix of four skills), and what's playing is printed round its rim. The sleeve carries the intro, or a project's liner notes once you click one. |
| `contents.html` (目次) | Every project as a volume spine on a shelf |
| `vol-<id>.html` | A project's volume: cover, spine, and its story as panels |
| `author.html` (作者紹介) | About, the years, contact, the CV per lens |
| `colophon.html` (奥付) | How this printing was made |

## How it's built

```
portfolio/bank/*.md  (private)
   └─ portfolio/tools/export_site.py   public entries only, leak-scanned
        └─ content/                    committed here; never edited by hand
             └─ build.py → dist/       plain HTML, no framework
                  └─ GitHub Actions → GitHub Pages
```

Design drafts: push a `design/<name>` branch and it deploys as a preview at `/preview/<name>/`; `LAYOUT` in `build.py` picks the cover's layout.

```sh
pip install pyyaml
python3 build.py                     # writes dist/
python3 -m http.server -d dist       # look at it locally
```

Change a fact in the bank, run the export from `portfolio`, then commit and push here. The push deploys.

## Now playing

`worker/` is a Cloudflare Worker at `https://kaishun-now-playing.beanbois.workers.dev`:

- `/now` is what's playing on Spotify, or the last track played. The tempo comes from ReccoBeats, cached per track; there's no beat ring when a track has none.
- `/art` re-serves the album cover with CORS, so the page can print it as screentone.

```sh
cd worker
npx wrangler deploy             # after changing src/index.js
npm run connect-spotify         # if Spotify's login expires: re-authorise (stores secrets in Cloudflare only)
```

**Tempo bank.** A track's BPM comes from the most trusted source that knows it, and the first hit wins:

| Trust | Source | Matched by |
|---|---|---|
| 1 | `site.yaml` → `music.bpm`: your own count | Spotify track id. Always wins |
| 2 | ReccoBeats audio features | Spotify track id |
| 3 | Deezer | ISRC (the same recording) |
| 4 | Deezer search | title, artist and length (±3 s) must all agree |

Hits are cached for 90 days, misses for 1 day. `/now` says which source answered (`bpm_source`). To fix a wrong or missing tempo, add the track to `music.bpm` in `site.yaml`, build, and deploy the worker.

To keep artists off the site, list them in `music.hide_artists` in `site.yaml`, build, and deploy the worker. Both settings reach the worker through `worker/src/config.json`, which the build writes.

## Editing

**[GUIDE.md](GUIDE.md)** is the how-to: `site.yaml` holds the words, colours and music settings (including a playlist per project), and `python3 build.py --watch` shows changes on http://127.0.0.1:8765 as you save.
