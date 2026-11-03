# Editing the website

The site is https://beanbois.github.io. This guide is everything you need to change it, see the change on your Mac, and publish it.

## The four parts

Each part is for a different reader, and the corners of every page lead between them.

| Part | Page | For | What's on it |
|---|---|---|---|
| The hook | the cover (`index.html`) | anyone arriving | the record, and a blurb written like the back of a book (`cover.blurb_head`, `cover.blurb`), with two doors: the brief and the projects. Clicking a project shows only its blurb and a link to its volume. |
| The brief | 作者紹介 (`author.html`) | someone with thirty seconds, e.g. a recruiter | your summary, the highlights (`pages.highlights` picks which volumes, in order), the years, contact, the CV PDFs, and the CV in full below |
| The projects | 目次 (`contents.html`) and a volume each | someone who wants depth | every volume as a record in its sleeve. Click one: the record comes out and the volume opens with it (Chrome, Edge and Safari animate this; other browsers just open the page). On the volume the record spins, then turns as you scroll, and the tonearm shows how far you've read. Every volume links to the ones either side. |
| The footnote | 奥付 (`colophon.html`) | the curious | when the site last changed (the date of the last commit), what changed lately, and how it's made. Every page's foot also says "last updated" and links here. |

## What lives where

| To change | Edit | Then |
|---|---|---|
| Words on the site, colours, music settings | **`site.yaml`** (this repo) | look locally, then publish |
| A project's facts (what it is, dates, bullets, stack, status) | `~/Desktop/works/portfolio/bank/…/<project>.md` | export (below), then look and publish |
| A volume's story panels (Wallet) | `~/Desktop/works/portfolio/docs/2-research-design/prototypes/site/chapters/<project>.yaml` | export, look, publish |
| Your CVs | `~/Desktop/works/portfolio/cv/general-*.md` | export, look, publish. Each CV is also printed to a one-page A4 PDF by Chrome during the build (`teoh-kai-shun-cv-<lens>.pdf`, linked on the author page). If a CV grows past one page at the smallest type size, the build says so. |
| Hidden artists, your own tempos | `site.yaml` → `music:` | publish the worker too (see Music) |
| Layout and design | `src/cover.html`, `src/page.html`, `build.py` | ask Claude, or carefully |

Facts go in the bank, because the CVs are written from it too. Everything about how the site looks and sounds goes in `site.yaml`.

## One-time setup

Already done on this Mac. On a new machine:

```sh
pip3 install pyyaml                      # the build's only dependency
cd ~/Desktop/works/personal_website/worker && npm install   # only for publishing music settings
npx wrangler login                       # same; logs in to Cloudflare
```

## See it on your Mac

```sh
cd ~/Desktop/works/personal_website
python3 build.py --watch
```

Open **http://127.0.0.1:8765**. Leave the command running: every time you save `site.yaml` (or anything in `src/` or `content/`), it rebuilds within a second. Refresh the browser to see the change. The record plays your real Spotify here too.

- **A mistake in `site.yaml`** (a missing quote, a wrong project id) prints `not rebuilt: …` with what's wrong, and the last good version keeps serving. Fix it and save again.
- **Stop:** Ctrl+C.
- **"Address already in use":** an old `--watch` is still running somewhere. Close that terminal, or run `pkill -f "build.py --watch"`.

**Trying the page turns (for now, until one of each is chosen).** Add a switch to any page's address; it sticks until you close the tab. Chrome, Edge or Safari only.
- `?nav=` picks how the four parts turn into each other: `geo` (the page slides along a curve of the ball's space, shrinking into a disc), `wave` (the default, Kai Shun's pick: the new page opens in a soft circle from where you clicked, slowing as it nears the edges, with a few light raised ripples behind it), `ball` (leaving the cover, the ball flies and the page opens out of it; everywhere else as `geo`), `tile` (heptagon tiles fill the screen and empty again), `sleeves` (the same, tiled with your record sleeves), `albums` (the same, tiled with the album covers of what you played lately; needs the worker deployed: `npm run deploy` in `worker/`, see "Music"; until then it shows the sleeves). Try `index.html?nav=wave`.
- `?bg=` picks what happens behind the record when a volume opens: `ripple` (the default), `tone` (screentone dots) or `dim` (the lights go down). Try `contents.html?bg=tone`.

## Editing `site.yaml`

Open it in any editor. Every setting has a comment saying where it shows up. A few rules keep YAML happy:

- Keep the indentation: two spaces, no tabs.
- Put text that contains `:`, `#`, or starts with a quote in `"double quotes"`. When in doubt, quote it.
- `#` starts a comment. Lines starting with `#` are switched off (that's how the examples are written).

**Words.** Change the text after the colon, for example:

```yaml
you:
  one_liner: "Builds the platforms that keep GPUs busy. Also builds too many side projects."
```

**Colours.** A light and a dark palette, each its own colours (the site follows the visitor's system setting). Any CSS colour works; `#rrggbb` is easiest. `spot` is the one red: keep it for things that are live or selected. The other names are roles, not hues, so each mode can colour them differently: `music` is what moves with the music (rim text, level bars, tonearm); `archive` is the shelf bands, corner squares, panels and the CV sheet; `mark` fills the caption boxes and hovers, with `on_mark` for text on it. `spot_edge` is the border round red things (set it the same as `spot` for no border). **By part:** to recolour one part of the site only (record, rim player, tonearm, sleeve, shadows, corners, live, shelf, panels, CV sheet), add it under `light:` or `dark:` with just the colours you want; the comment in `site.yaml` lists every part, its colours and their defaults. A misspelt part or colour stops the build with a message saying so.

## Changing a project's facts

1. Edit the entry in `~/Desktop/works/portfolio/bank/`. The schema is in that folder's `README.md`. When you've checked an entry, remove its `# DRAFT` notes and add `verified: <today's date>` to its front matter (e.g. `verified: 2026-10-25`): that takes the "draft" stamp off it on the site. The check refuses a verified entry that still has a DRAFT note.
2. Export the public part to the site:

   ```sh
   cd ~/Desktop/works/portfolio
   python3 tools/export_site.py
   ```

   It refuses if anything private or an internal name would leak, and tells you what.
3. If `--watch` is running, the site has already rebuilt. Look, then publish.

## Music

**A playlist per project.** Under `music.playlists`, add the project's id (from the table at the end) and a Spotify playlist link:

```yaml
music:
  playlists:
    kkp-wallet: https://open.spotify.com/playlist/…      # "Share → Copy link to playlist" in Spotify
    tradingjoe: https://open.spotify.com/playlist/…
```

Clicking that project then plays a random song from the playlist, and the playlist's cover goes on the record. **The playlist must be one you own or collaborate on**: Spotify only shows this kind of app the tracks of your own playlists. Any other playlist quietly falls back to what you're playing now. Playlists are cached for 6 hours, so a change to a playlist's songs can take that long to show. This setting needs nothing more than publishing the site.

**Hidden artists and your own tempos** are read by the worker (the small program on Cloudflare that talks to Spotify), so after changing them, publish it as well:

```yaml
music:
  hide_artists:
    - Some Artist
  bpm:
    https://open.spotify.com/track/4iaPbB3jH6NGKhSVjETPwG: 96     # "Share → Copy song link" in Spotify
```

```sh
python3 build.py                                   # writes worker/src/config.json from site.yaml
cd worker && npm run deploy                        # takes about 10 seconds
```

The build reminds you when these have changed. Your own tempo beats every other source (the order is in `README.md`).

**If the record stops showing music,** Spotify's login has probably expired (roughly every six months). Reconnect:

```sh
cd ~/Desktop/works/personal_website/worker
npm run connect-spotify
```

## Publishing

A push to `main` publishes the site. It's live in about a minute.

```sh
cd ~/Desktop/works/personal_website
git add -A
git commit -m "Say what changed for a visitor"
git push
```

`gh run list --limit 1` shows whether the deploy succeeded. If it failed, `gh run view --log-failed` says why.

**To try something without touching the live site,** put it on a design branch. It publishes as a preview at `https://beanbois.github.io/preview/<name>/`:

```sh
git checkout -b design/new-colours
# …edit, look locally…
git commit -am "Try warmer colours" && git push -u origin design/new-colours
```

When you like it: `git checkout main && git merge design/new-colours && git push`, then delete the branch with `git push origin --delete design/new-colours` (its preview disappears).

## Project ids

For `music.playlists`. For `pages.highlights`, use the volume's id: most are the same as the project's, except the volumes that hold several projects: `ai-platform` (the Tencent platform work) and `neuromorphic` (with iRecognise).

| id | project |
|---|---|
| `9loop` | 9Loop |
| `aki-predictor` | Acute kidney injury predictor |
| `blockhub` | BlockHub |
| `car-designer` | CarDesigner |
| `chess-ai` | chessAI |
| `data-terminal` | Data terminal |
| `expense-tracker` | expense-tracker |
| `fps-rl-agent` | RL agent for an FPS game |
| `icl-hyperbolic` | In-context imitation learning with non-Euclidean methods |
| `irecognise` | iRecognise |
| `kkp-wallet` | Wallet |
| `kurf` | KURF research programme (King's) |
| `mybudixc` | myBudiXc |
| `neuromorphic` | Neuromorphic computing (independent study) |
| `ollama-home-lab` | Ollama home lab |
| `plate-recognition` | Malaysian licence plate recognition |
| `polyarb` | polyarb |
| `re-news` | RE-News |
| `robocup` | RoboCup@Home (King's) |
| `sales-signatures` | Sales signatures |
| `srgan` | SRGAN from scratch |
| `tencent-autoscaler` | Time-of-day GPU autoscaler |
| `tencent-cloning` | Cross-environment service cloning |
| `tencent-conversation-service` | Gameplay conversation query service |
| `tencent-multitenancy` | Multi-tenant model deployment |
| `tencent-reliability` | Platform reliability |
| `tradingjoe` | TradingJoe |
| `transformer-from-scratch` | Attention Is All You Need, from scratch |

A new project in the bank gets its id from its file name.
