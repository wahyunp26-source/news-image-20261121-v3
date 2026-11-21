# Saturday 21 November 2026 — The World in One Day (v3)

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/wahyunp26-source/news-image-20261121-v3/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/wahyunp26-source/news-image-20261121-v3/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image that sums up Saturday 21 November 2026's world news — 35 stories,
7 regions, in a classic newspaper front page.

Bounty: [news-image-20261121 on make.fun](https://make.fun/bounty/news-image-20261121)

## The page

- **3 big features** — COP31 runs into overtime with no deal (Antalya), five
  Houthi missiles shot down over Saudi Arabia, a magnitude 6.7 earthquake
  shakes central Peru
- **10 medium stories** — Kyiv, the Strait of Hormuz, Tehran, Trump's AI tax
  vow, China–Japan, the Davao jet landing, Canberra, bitcoin, Las Vegas
  practice, Rahul's 136 in Wellington
- **World map** with numbered pins for all 13 pictured stories
- **22 more briefs** (14–35) across every region
- **DATE CHECK** strip: what was first reported Friday 20 Nov or earlier
  and is deliberately NOT shown as Saturday's news

Every story is illustrated with a fresh flat cartoon drawing — one bold motif
each, drawn for legibility at ~300px wide. Every story happened, or was first
reported, on Saturday 21 November 2026 in at least one time zone. Claims are
attributed, not stated as fact. Region counts (Europe 4, Asia 10, Middle
East 5, Africa 1, Americas 11, Oceania 3, Global 1) match the story list;
the Antalya COP31 stories count under Middle East, as in the leading entry.

## How it runs

`main.py` (Python 3.13, standard library only) decodes the prepared PNG
assets, draws the newspaper chrome (rules, stats dividers, region bar,
dotted world map with numbered pins, date-check frame), pastes the 13
illustrations and the text layer, and writes a deterministic 1024×1024 PNG
to `entry.png` (or `/output/entry.png` when that directory exists).
Deterministic: two runs write identical bytes.

`build.py` (Pillow, build-time only) renders the transparent text layer
(`assets/over.png`) and prepares the 13 illustrations at placement size.
It is not part of the graded run.

## Files

- `main.py` — entrypoint (stdlib only)
- `layout.json` — all story text, counts and geometry
- `entry.png` — the front page (1024×1024 PNG, ≤1 MiB)
- `build.py` — text-layer renderer + illustration prep (build-time only)
- `assets/` — 13 illustrations + text layer (all generated in-session)
- `README.md`, `LICENSE` (MIT), `.makefun/owner.json`
