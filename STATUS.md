# news-image-20261121 v3 — STATUS (build only, not submitted)

## Repo

- https://github.com/wahyunp26-source/news-image-20261121-v3
- Commit: `0ea6d15` (first) — rebuilt files committed + pushed after final visual pass (see git log for the final sha)
- Branch: main, public. Homepage: https://make.fun/bounty/news-image-20261121. Topics: make-fun, news-image.
- Entry dir: `~/workspace/makefun/news-image-20261121-v3-entry/`
- `.makefun/owner.json` contains exactly `{"wallet":"wQUy3YoX5DoUSaAsXycrZT21NTih6BRwE6N4ossmy9S"}` (verified by cat).
- LICENSE first line: `SPDX-License-Identifier: MIT`. README uses the 3-badge format (competition / rank / reward, v3 repo path).

## Kit

- Kit was level 32, site level 34 at start. Refreshed from `https://make.fun/c/news-image-20261121/kit` (old kit backed up to `news-image-20261121-kit-bak32`, diff verified: RULES.txt, cli/makefun.mjs, harness files, kit.json changed). Fresh kit lives at `~/workspace/makefun/news-image-20261121/news-image-20261121-kit/` (outer dir); `makefun status` after refresh shows no level warning.
- `makefun check --worktree` (fresh kit): 4 passed (competition_open, snapshot, license_osi, entrypoint), 1 failed (transcripts_present — no transcripts uploaded locally; recording is handled at submit time), 14 skipped, 5 at-submission checks listed. Entry checks otherwise pass.

## Entry

- `entry.png`: 1024×1024 RGB PNG, 342,098 bytes (≤1 MiB), magic `89504e470d0a1a0a`.
- `main.py`: Python stdlib only, written fresh in this session, revised once after the first visual review (stats-divider span, region-bar last segment to the exact right margin, white ring on map pins). No v2 code was read or copied.
- Determinism: 3 consecutive runs of `main.py` produced identical sha256 `f06fcabe10652b68f5bce7644713f18be63b8d6731f918d5c487061f1c690469`.
- 300px check: headline, stats strip and the 3 feature headlines remain readable at 300px wide.
- Previews: `preview-top.png`, `preview-medium.png`, `preview-bottom.png` in the entry dir.

## Stories (35, 7 regions — counts verified against the list)

- Regions: Europe 4, Asia 10, Middle East 5, Africa 1, Americas 11, Oceania 3, Global 1 (= 35). Antalya COP31 stories count under Middle East, matching the rank-1 bar.
- Big 3: (1) COP31 overtime, Antalya — verified live (AP/Reuters: overtime Saturday, draft 144→80 paragraphs, no fossil-fuel mention, third text promised Saturday, Kurum quote). (2) Five Houthi missiles over Saudi Arabia — verified live (3 over Riyadh early Saturday, 01:53 warning, announced ~02:00 by Maj. Gen. Turki Al-Maliki; 2 toward Jizan Friday evening, debris Al-Shuqaiq). (3) Peru M6.7 quake — verified live (00:09 UTC Sat 21 Nov, USGS 108 km / IGP 129 km, 9 km NE Carhuamayo / 30 km NW Junín, felt in Lima; Indeci Saturday update: 8 injured, 128 homes affected, 4 destroyed, no deaths, no tsunami risk).
- Medium 10: Kyiv/Zelensky Crimea bridge, Hormuz drone claim, Tehran uranium, Trump AI tax, China–Japan Taiwan, Davao 146 safe, Canberra AI talks, Bitcoin $58,983 (−3.9%, ether $1,625, CoinGecko 02:08 UTC), Russell P1 1:34.041, Rahul 136.
- Rahul score: verified live as FINAL 136 (India 486-4 at stumps, lead 118; Cricinfo/ICC/AFP). The rank-1 entry's "124*" was the tea-time snapshot; v3 uses the final 136 everywhere (stats strip, card, sub-headline wording "Strong quake shakes Peru" kept, stats show 136).
- Briefs 14–35: as listed in the task brief; two were shortened to fit the column width (#20 "Trump's call", #35 dropped "after contact"). All 22 fit, verified by build-time width asserts.
- DATE CHECK: Friday 20 Nov news left out (Wall Street correction, Russian barrage on Kyiv's bridges, missile in Poland, UK–EU deal, Cyclone Akvan landfall); older (Voyager 1 light-day, 18 Nov); unconfirmed (BepiColombo Mercury orbit, final COP31 text).

## Illustrations

- 13 flat-cartoon illustrations generated in-session via the media pipeline (1920×1280 PNG sources in /tmp/news21-v3-raw/, prepared to placement size by build.py with edge-column stretch so no motif is cropped or doubled). Visually checked: all 13 motifs complete (COP31 globe/thermometer/clock, Saudi night sky/trails/starbursts, Peru seismograph/mountains/house, Kyiv mic, Hormuz ship/drone, Tehran podium, Trump chip/flag, China–Japan flags/handshake, Davao plane, Canberra parliament/chip, Bitcoin coin/falling chart, F1 track/car, cricket batsman/stumps).
- Dotted world map with 13 numbered pins drawn by main.py from a hand-written continent grid in layout.json.

## Fixes vs v2

- Feature stories are all Saturday 21 Nov (v2 featured Friday news: Poland missile, ICJ Myanmar ruling).
- Peru quake is a big feature (v2 wrongly left it out in DATE CHECK).
- Rahul uses the verified final 136, not the tea-time 124*.
- DATE CHECK corrected to the rank-1 wording.

## Known weaknesses

- The Riyadh/Hormuz/Tehran map pins cluster within ~11px in the Middle East and partly overlap (same crowding as rank 1's map).
- The F1 illustration's car is small inside its frame.
- The judge is pairwise and subjective; no local score exists for this competition type.
