# Optimisation, November 2026

What was slow or heavy, what changed, and how it was checked. All numbers are from `python3 build.py` on the
same content before and after (commit `0a19727` vs this change), measured in a cloud sandbox.

## Results

| | Before | After | Change |
|---|---:|---:|---:|
| Elements across all 44 pages | 154,811 | 31,420 | −80% |
| HTML across all pages (raw) | 8.46 MB | 4.31 MB | −49% |
| HTML across all pages (gzip -9) | 1.40 MB | 0.98 MB | −30% |
| Build, without the CV PDFs | 0.83 s | 0.28 s | −66% |
| Build, CV PDF step (wall clock) | 3 lenses one after another | 3 lenses side by side | ~3× faster |
| Cover meter repaints while idle | 60 a second | 0 | — |

The heaviest pages:

| Page | Elements before → after | Raw before → after | Gzip before → after |
|---|---:|---:|---:|
| `vol-ai-platform.html` | 20,894 → 2,190 | 833 KB → 210 KB | 90 KB → 33 KB |
| `vol-re-news.html` | 12,662 → 1,352 | 520 KB → 145 KB | 61 KB → 26 KB |
| `vol-icl-hyperbolic.html` | 9,368 → 1,828 | 455 KB → 204 KB | 58 KB → 33 KB |
| `vol-kkp-wallet.html` | 8,768 → 1,086 | 382 KB → 123 KB | 49 KB → 24 KB |
| `contents.html` | 8,003 → 6,626 | 487 KB → 441 KB | 53 KB → 48 KB |
| `index.html` (cover) | 162 → 162 | 183 KB → 141 KB | 60 KB → 45 KB |

Fewer elements is the change that matters most to a visitor: every SVG element is parsed, styled, laid out and
painted, and held in memory while the page is open, so a 21,000-element page is slow to open and to scroll on a
phone however well it compresses.

## What changed

### 1. Screentone is drawn as patterns, not one circle per dot (`art.py`, `tone()`)

The panel pictures sit on screentone: a grid of dots that grow down (or up) the panel. `tone()` wrote one
`<circle>` per dot, about 1,500 for a wide panel, and a long volume has a dozen panels. Those dots were 99% of
the elements on the volume pages.

Now each row of dots is one `<rect>` filled with a one-dot `<pattern>` (dots in a row share a size, so a row is
exactly a repeating tile). A panel goes from ~1,500 elements to ~60. The tile is centred on the dot and the
rect runs half a step either side of the row's first and last dot, so the same dots are drawn in the same places
and none is clipped (the largest radius, 3.2, is well inside the half-row of 5.2). `tone_bands()`, which the
sleeves already used, works the same way; this brings the panels in line with it.

Pattern ids come from one counter for the whole build, so they are unique on every page. Each pattern is used
only by the rect next to it, in the same `<svg>`, so a hidden SVG never hides another one's pattern.

The one difference: the old code rounded each dot's position to a whole unit, the new rows sit at their exact
height (at most half a unit away). See "How it was checked".

### 2. The cover carries only the data it reads (`build.py`, `cover_page()`)

The cover inlines the site's data as `const D = {...}` for its script. It carried every node's bullets, stack,
repo, kind and story, and the site's log, years and counts, none of which `src/cover.html` reads (the volumes
and the brief show those). They are now left out (`COVER_SKIPS`): the cover's HTML is 42 KB smaller, 15 KB
gzipped, and the script has less to parse before the record appears. If the cover ever needs one of those
fields, take it off `COVER_SKIPS`.

### 3. The font subset is collected per distinct character (`build.py`, `subset_fonts()`)

To ask Google Fonts for only the characters the site uses, the build tested every character of every page
(8.4 million of them, twice each) for being printable. It now takes each page's set of characters first and
tests the few hundred distinct ones. Same subset; this is most of the build time saved (0.83 s → 0.28 s).

### 4. The three CV PDFs print in parallel (`build.py`, `cv_pdfs()`)

Each CV lens (ML, Cloud, Backend) is printed by its own headless Chrome, with its own profile and output file,
and they ran one after another. They now run side by side in a thread pool of three, so the step takes as long as
the slowest lens instead of the sum. The behaviour is unchanged: smaller type until it fits one page, one retry
on a hang, and on the deploy a failure still stops the build (the error is raised in the main thread).

In the sandbox, which cannot reach Google Fonts, every Chrome ran into its 45 s timeout twice, so the whole build
took 4 m 32 s before and 1 m 31 s after. On GitHub Actions, where Chrome prints in seconds, the saving is
smaller in absolute terms but the same ratio.

### 5. The cover's level meter stops repainting when it is flat (`src/cover.html`, `drawMeter()`)

The meter under the record redrew its canvas every frame, including when nothing is playing and the bars lie
flat, so an idle cover kept repainting a still picture 60 times a second (battery, on a laptop or phone). It now
keeps the last frame once the bars have settled flat and nothing is live, and draws again the moment anything
changes: music starts, the canvas is resized, the pixel ratio or the bar colour changes. The animation itself is
untouched.

## How it was checked

- **Pictures.** Four pages (`vol-ai-platform`, `vol-kkp-wallet`, `vol-chess-ai`, `contents`) were rendered
  full-page in Chromium from the old and new builds and compared pixel by pixel. The pages are the same size and
  0.005–0.13% of pixels differ by more than 40/255 (mean difference under 0.2/255): the dots' sub-unit position
  change, invisible side by side.
- **Cover.** Loaded from both builds with no page errors; opening a project from the directory shows its blurb
  as before (so the pruned data held everything the cover needs). With the meter forced on screen and nothing
  playing, the old cover cleared its canvas 120 times in two seconds and the new one not at all.
- **Every page.** All 44 pages loaded over a local server (`python3 -m http.server -d dist`) with no page errors.

## Looked at, left alone

- **The cover's record animation** runs every frame on purpose (the ball turns, the record spins); the browser
  already pauses it in a background tab.
- **`contents.html`** is still the largest page (441 KB raw, 48 KB gzipped). Its weight is forty sleeves and
  forty records drawn inline, and most of it is real drawing (titles, panel pictures, grooves) rather than
  repetition. Loading the sleeves lazily would save more, but changes how the shelf and the volume transition
  work, so it is a design decision rather than an optimisation.
- **Fonts** were already subset to the site's characters, with `preconnect` and `display=swap`.
