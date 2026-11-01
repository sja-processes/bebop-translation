# Be-Bop High School (J) — English translation plan

Work is split into stages sized for one sitting each (roughly an hour of agent
time). Start each session with: "Continue the Be-Bop translation — next stage
in PLAN.md". Update the **Status** and **Findings** sections at the end of
each session so the next one doesn't re-derive anything.

## Status

- [x] **Stage 0 — Tooling check** (2026-10-10)
- [x] Stage 1 — Static ROM survey (2026-10-10)
- [x] Stage 2 — Find the font & table file (2026-10-10)
- [x] Stage 3 — Trace the text engine (2026-10-10)
- [x] Stage 4 — Script dump (2026-10-10)
- [ ] Stage 5 — Translation (several sessions, mostly you + Claude chat) — first pass of all 8 files done 2026-10-10; review/polish pending
- [x] Stage 6a — Font, ROM expansion, inserter; English intro verified (2026-10-11)
- [x] Stage 6b — Verb menu width, screens check, BPS patch, newline decision (2026-10-11)
- [x] Stage 7a — Title menu in English (2026-10-14)
- [x] Stage 7b — Title subtitle (English line under kanji) + romanised author credit (2026-10-14)
- [x] Stage 7c — Status panel (NERVE / LUCK / luck grades); bank 7 "kana grid" identified as ending credits (2026-10-14)
- [x] Stage 7d — Ending staff credits in English (2026-10-14; wording open for Stephen's review)
- [x] Stage 7e — Scene-art text: survey done, CLOSED caption added, 8/9 flavour (2026-10-15); street-area signs #2-#7, #10 deferred to stage 8 (judge in context)
- [x] Stage 8a — Automated checks (2026-10-16): text-box layout, change audit, raw tiles, verbs
- [ ] Stage 8b+ — Stephen's playthrough findings, fixed in batches (one session per batch)
  - [x] Batch 1 (2026-10-16/17): see "Stage 8b batch 1" below. Next: more of Stephen's play; Junko's self-reference lines to review; street-area signs when met
- [x] Optional — In-game help: the caretaker's room south of Aitoku High (NERVE, LUCK, saving, evenings); built 2026-10-17, see "Optional: help pages" below. **To do:** Stephen's handheld test
- [x] Kakui department store picture variants (floors and roofs looked identical); built 2026-10-18, see "Department store variants" below. **To do:** Stephen's play test
- [x] Optional — Caretaker extras, stage 1: menu split (Talk / Ask), Beg → Promise luck cheat (always CHARM), Flatter hint placeholder; built 2026-10-23, see "Caretaker extras" below. **To do:** Stephen's handheld test
- [x] Optional — Caretaker extras, stage 2: real hints, one per story milestone (39 hints, built 2026-11-01; see "Caretaker extras"). **To do:** Stephen's handheld test
- [x] Optional — Day goal: caretaker Coffee tells the day limit for the happiest ending; Select in a scene swaps LUCK/grade for GOAL / DAY / time. Built 2026-10-31 (`tools/daygoal.py`), see "Day goal" below. **To do:** Stephen's handheld test
- [x] Optional — Visible cars in the Nishiyama Building car park (two car scenes had no car on the map); built 2026-10-24, see "Car park cars" below. **To do:** Stephen's handheld test

## Stages

**1. Static ROM survey.** Split PRG into its 8 × 16 KB MMC1 banks, find
which bank is fixed at $C000, and map the vectors/NMI handler. Run a CDL pass
through title → new game → first dialogue to learn which banks hold code and
which hold data. Output: a bank map in this file.

**2. Font & table file.** Find the kana/Latin glyphs in CHR ROM (the title
menu shows a kana font). Read nametable writes while the menu is on screen to
map byte → tile. Output: `tools/bebop.tbl`.

**3. Text engine.** Set a watch on PPU writes ($2007) during a dialogue box,
walk back to the routine that reads script bytes, and document pointer
tables, control codes (newline, wait, name substitution, end), and bank
switching. Output: an engine description in this file.

**4. Script dump.** A Python dumper using the table + pointer tables, writing
`script/*.txt` (Japanese with IDs). Check how many bytes are free for growth.
`script/jp/` is gitignored — per AGENTS.md, don't commit material
extracted from the ROM; `script/en/` (English only) is committed.

**5. Translation.** Fill in English next to each line. How to run it
(cheapest in a normal Claude chat, one dump file per sitting):
1. `python3 tools/script.py dump` (re-creates `script/jp/`, gitignored).
2. Give the chat one `script/jp/msg_XXX.txt` plus the rules below, and ask
   for an English-only file in the same shape: each `@@ ID ...` line
   followed by `EN:` and the English (no JP block).
3. Save the reply as `script/en/msg_XXX.txt` (committable — it contains
   no ROM text) and commit.
Rules for the translator: keep every `[code ...]` exactly and in order;
`[page]` is a page break; aim for ≤24 characters per line and ≤4 lines per
page (the inserter will re-wrap and warn, so natural line breaks are
fine); character/place names consistent across files (keep a glossary in
`script/glossary.md`); verb list entries (IDs $3AA-$3C1) must be short
menu words (target ≤ 8 letters). **Use UK English
throughout:** British spelling (colour, realise, programme), vocabulary
(mate, bloke, mum, trousers, pavement) and idioms, plus British slang
for the delinquent schoolboy banter where an equivalent fits, rather than
American phrasing. This is mostly
language work and can be done in a normal Claude chat (cheaper) in batches.

**6. Insertion.** Inserter that re-encodes English, repoints, and emits a
BPS patch. A likely need: an 8×8 Latin font in CHR and possibly DTE/
word compression or text relocation if space runs out (MMC1 128 KB PRG can
be expanded to 256 KB if necessary).

**7. Graphics.** Title kanji subtitle, any graphic menus/signs.

**7e. Scene-art text.** Policy agreed with Stephen: Japanese painted into
background art is kept for local flavour; where it carries meaning the
player needs (e.g. 閉店 "Closed" on a shop shutter, which is why the only
option there is Leave), add a small English caption beside it rather than
replacing it. Steps: (1) survey every scene CHR bank / layout for
Japanese text and list meaning + where it appears; (2) Stephen marks each
as flavour or gameplay; (3) add captions only for the gameplay ones.

**8. Playtest.** Agreed approach (2026-10-15): split by who is better at
what, which also saves usage (stepping through the game frame by frame in
the emulator costs many tokens; Stephen playing costs none).
- **Claude, systematic checks first (8a):** a tool that renders all 962
  messages page by page as they appear in the text box, scanned for
  overflowing lines, too many lines per page, stray tiles and broken
  control codes (no emulator needed); quick test builds to view all 37
  scene pictures and every verb menu (with the menu/box on screen, see
  7e lesson); the full ending in the real game flow, not just the
  `cmdDB` shortcut; emulator traces only where something looks wrong.
- **Stephen, real play (8b onwards):** play naturally and judge the
  English. Watch for: text running past or cut off at the box edge, odd
  wrapping, lines that read awkwardly or don't fit the scene; menu
  responses that don't match the chosen action; flicker or garbage,
  especially around the picture frame and status panel; leftover Japanese
  that seems to matter (street-area signs #2-#7, #10 from the 7e survey —
  screenshot them when met); branches that misbehave or crash.
- **Reporting:** a screenshot plus a short note; a Mesen save state just
  before the problem for anything that needs tracing.
- **Rhythm:** 8a first so obvious problems are fixed before Stephen
  invests play time; then he plays in his own chunks and sends findings,
  fixed in batches, one session per batch.

## Findings

### ROM
- iNES header: mapper 1 (MMC1), 128 KB PRG (8 × 16 KB), 128 KB CHR,
  battery-backed SRAM. SHA-1 `68373685E2FACEFC23C5622ED3B7957B8D8C6500`.
- Vectors (last bank): NMI `$C0F7`, RESET `$FFD0`, IRQ/BRK `$C15B`.
- Title screen (frame ~300 after reset) shows a kana menu: two character
  choices (Nakama Tooru / Katou Hiroshi) plus "continue".

### Bank map (stage 1)

MMC1 control written as `$1E` at boot: PRG mode 3 (bank 7 fixed at
$C000, $8000 switchable), CHR 4 KB mode, vertical mirroring.

| Bank | Role | Free (largest $FF run) |
|---|---|---|
| 0 | Data, some text-like data; read $AFC9-$B148 at intro | 3757 B @ $B143 |
| 1 | Data (graphics/nametables?); read $8390-$84BF, $AAC0-$AEBF | 357 B @ $BE8B |
| 2 | **Script** — dense dialogue throughout | **none** (11 B) |
| 3 | **Script** $8000-~$AC00, sparser data after | 315 B @ $BEB5 |
| 4 | **Main game code** (title, story) + tables | 4453 B @ $AE8B |
| 5 | Data, not touched in intro | 186 B @ $BF36 |
| 6 | Code+data (small entries at $8000, $95AE, $A5CE, $AD7A…) | 1430 B @ $AF6A |
| 7 | Fixed: kernel, NMI, mapper helpers; text/strings around $F800-$FFC0 | 724 B @ $FCFC |

Banks 0–6 end with a dummy vector stub at $BFF0 (unused in mode 3).
Script space is tight (bank 2 is full), so plan on DTE or a PRG expansion
to 256 KB (MMC1 SUROM-style is awkward; easiest is relocating text into
freed/added banks — decide in stage 6).

### Fixed-bank routines (bank 7)
- `$C003` write MMC1 control; `$C017` CHR bank 0 (from `$7D`);
  `$C02B` CHR bank 1 (from A; `$7E` normal, `$7F` after sprite-0 split);
  `$C049` PRG bank select (A → also saved in `$7C`); `$C07B..$C093` =
  select PRG bank 0..6.
- `$19` = "mapper not busy" flag; NMI skips all work while it is 0.
- NMI `$C0F7`: OAM DMA from `$0700` if `$1A`; `JSR $D1E8` PPU uploads;
  sprite-0 hit wait, then CHR bank switch mid-screen (status/text split).
- `$D1E8` PPU upload queues (likely where text reaches the screen):
  - `$1B` ≠ 0 → palette, 32 bytes from `$0200`.
  - `$1D` ≠ 0 → run of `$1D` bytes from `($62)` to PPU addr `$61:$60`.
  - `$1C` ≠ 0 → list of (hi, lo, value) triples at `$02C4`, `$1C` = bytes.
- `$6E` frame counter. Reset init at `$C098`, then `JMP $DA0A`.

### Text encoding (head start for stages 2–3)
- Script bytes = nametable tile numbers, uncompressed.
  Hiragana `$00`+ in gojūon order (あ=$00, い=$01, こ=$09, つ=$11,
  の=$18), katakana `$60`+ (ア=$60, キ=$66, ン=$8D), space `$FE`.
- `$5A` before a kana = dakuten; on screen it's drawn as tile `$5A` on
  the row *above*, so each text line uses two nametable rows.
  (Handakuten probably `$5B`, unconfirmed.)
- `$F5` = newline, `$F4` = end of page/wait (likely). Other codes seen:
  `$F0 xx`, `$EF xx`, `$ED`, `$58` (。?), `$57`.
- First intro line "ついに この キタコウの…" is at bank 3 `$A3F8`.
- No pointer table — confirmed in stage 3, see "Text engine".

### Font & table (stage 2)
- Font lives in **CHR 4 KB banks 30 and 31** (CHR ROM offsets $1E000 /
  $1F000), tiles $00-$9F; tiles $A0-$FF of those banks are portraits.
  Banks 30/31 are almost identical in the font area — only tiles $42, $4D,
  $7C, $86, $8D differ (glyph variants of 0, O, ホ, ラ, ン). Which screen
  uses which bank: find out in stage 3.
- Layout: $00-$2D hiragana あ…ん; $2E-$36 ぁぃぅぇぉゃゅょっ; $37 unknown
  (rare); $38-$40 ァィゥェォャュョッ; $41 unknown (rare); $42-$4B digits
  0-9; $4C N, $4D O, $4E 「, $4F 」; $50 icon; $51 ？ $52 ！ $53 ー $54 〜
  $55 ‥ $56 ・ $57 、 $58 。 $59 ♥ $5A ゛ $5B ゜ $5C B $5D A; $5E/$5F
  graphics; $60-$8D katakana ア…ン; $8E/$8F and $90-$9F white-on-black
  kana graphics (probably status/menu labels).
- `tools/bebop.tbl` (Thingy format) covers all of this, with `5Axx` /
  `5Bxx` two-byte entries for voiced kana. Verified by decoding bank 3
  $A3F8 and samples from banks 2/3.
- **English font plan:** once Japanese is replaced, kana tiles $00-$8D
  (142 slots) are free for an English font in both banks 30 and 31, which
  is plenty for A-Z, a-z and punctuation, or for DTE pair tiles. With no
  dakuten, the "row above" isn't needed, so lines could be single-spaced
  (more lines per box) if the engine allows. Check first that no other
  screen uses kana tiles as graphics.

### Text engine (stage 3)

**Message lookup** — `$DBCF` runs message ID in X (lo) / Y (hi). IDs
`< $170` → bank 2, index = ID; IDs `>= $170` → bank 3, index = ID − $170
(constant at `$DBF0`/`$DBF5`; banks chosen by `JSR $C083`/`$C087` at
`$DBF9`/`$DC02`). `$DC16` then walks from `$8000` skipping `index`
`$FF`-terminated messages. **No pointer table**: to reinsert, keep
message order and make each bank's messages fit in the bank. The skip
loop doesn't parse arguments, so **`$FF` must never appear in an
argument or text byte**. Verified at runtime: the intro calls ID `$238`
= bank 3 `$A3B6`.
- 368 messages in bank 2 ($8000-$BFE5, full; 26 junk bytes after).
- Bank 3 holds IDs `$170`+, then ~315 bytes `$FF` padding at `$BEB5`.
- To gain space later: patch the `$170` split, or point the bank-selects
  at other/added banks.

**Interpreter** — `$DC3C` loop: `$EA04` fetches `($4D)` → `$51` and
advances `$4D/$4E`; the byte is looked up in a 48-entry code list at
`$DC6E` with an RTS-jump table (hi `$DC9F`, lo `$DC9E`). Anything not in
the list is a printable tile: `$DCFE` queues (hi `$50`, lo `$4F`, tile)
into the `$02C4` NMI list and increments the cursor `$4F`. After each
char, `$DC5B` waits `$52` frames unless fast mode (`$20`) is on.
- Text box origin: PPU `$2084` (reset in `$E9AC`); the box is cleared over
  9 rows by `$E97D`. Newline `F5`: cursor = (row start) + `$44` → two
  rows down, column 4. Diacritic codes `5A`/`5B`/`9D` (`$E1D3`) draw the
  mark one row up (cursor − $20) and then print the next byte.

**Control codes** (args = following bytes; implemented in
`tools/script.py`):

| Code | Args | Meaning |
|---|---|---|
| `FF` | 0 | end of message |
| `F5` | 0 | newline (2 rows down) |
| `F4` | 0 | wait for button (blinking tile $50), clear box |
| `D3` | 2 | `F4` then goto message |
| `F3` | 1 | delay N frames |
| `F7` / `F6` | 1 | set / clear flag `$7100+n` |
| `F2` | 2 | goto message (lo, hi) |
| `F1` | 2 | call message (nested) |
| `FD` / `D9` | 5 | flag, target-if-clear, target-if-set (D9 = call & return) |
| `F9` / `D5` | 10 | two flags → one of four targets |
| `FC` / `D8` | var | `(flag lo hi)*` `FA lo hi`: go to first set flag's target, else default |
| `FB` / `D7` | var | same, first *clear* flag |
| `F8` / `D4` | var | menu: id, then one target per non-empty slot of menu row `$DEB3+id*6` (a trailing "leave" slot may have no target) |
| `5A`/`5B`/`9D` | 1 | dakuten/handakuten/inverse-dakuten + char |
| `E4` / `E3` | 0 | fast text on / off |
| `EB` | 0 | screen flash (greyscale for a frame) |
| `D2` | 0 | flash + shake |
| `EF` | 1 | scene/music change? (special-cases $32/$14 by chosen hero `$71B5`) |
| `F0` | 1 | portrait/face? (writes `$02C2`) |
| `EE` | 1 | sets `$7007` (often right after `EF`) |
| `EC` | 3 | object/sprite placement? (bank 6 `$800C`, coords ×16) |
| `EA` | 1 | sub-command via table at `$E2B7` |
| `DE` / `DD` | 1 | `$C296` with arg (sound?) |
| `ED` | 0 | clears `$21` (mid-sentence, e.g. before ‥‥) |
| `E2`-`DF` | 0 | call fixed messages $254-$257 depending on hero |
| `E9 E8 E7 E6 E5 E1 E0 DC DB DA D1` | 0 | game-state actions (not text) |

Names with "?" are guesses; they don't matter for translation as long
as argument lengths are right. `tools/script.py check` parses all 1276
reachable messages with zero errors.

**Menus** — menu row 0 at `$DEB3` is the 6 slot screen positions; other
rows hold verb IDs (01, 02, 03, … 07). The verb names are printed by
`$DE6C` from somewhere not yet located — find in stage 4 (likely the
text-like area in bank 7 around $F800 or bank 3 after $AC00).

### Script dump (stage 4)
- `tools/script.py dump` → `script/jp/msg_000.txt` … `msg_380.txt`, 128
  messages per file, 962 messages (IDs $000-$3C1; bank 3's trailing $FF
  padding is dropped). Each entry: `@@ ID bankN $ADDR`, `JP:` block, `EN:`
  block (pre-filled with the JP for convenience).
- Format: newline = `F5`; `[name hex-args]` = control code; `<XX>` = raw
  byte (tiles $37, $41, $50 and the $8E-$9F inverse kana); `[page]` /
  `[page+goto …]` are followed by a cosmetic newline. `encode()` is the
  inverse of `render()` and `tools/script.py check` confirms all 1276
  messages round-trip byte-for-byte, so the dump format is safe to
  reinsert from.
- **Verb list**: 24 verb names at bank 3 `$BE36`-$BEB4 (IDs $3AA-$3C1 in
  the chain), read by `$DE88` via a *fixed* pointer (`LDA #$36/#$BE` at
  `$DE8B`/`$DE8F`) skipping X−1 `$FF`-terminated names. Reinsertion must
  either keep it at $BE36 or patch those two bytes.
- Volume: bank 2 = 368 messages, 16358 bytes (13565 text / 2793 codes);
  bank 3 (to $BE35) = 570 messages, 15926 bytes (9197 text / 6729 codes).
  ~20,800 Japanese glyphs. English typically needs ~1.5× the kana count,
  so expect ~10 KB more than fits today.
- Text box: max line 24 glyphs (box clear width $19 = 25 tiles), normally
  4 lines/page (5 in 8 places) because each line uses 2 rows.
- **Stage 6 decision (agreed 2026-10-10):** expand PRG to 256 KB (SKROM-compatible; never 512 KB — SUROM conflicts with CHR-ROM banking); DTE only if a later limit appears. Plan: expand PRG to 256 KB (MMC1 handles 16 × 16
  KB banks; copy the fixed bank to bank 15, add the $BFF0 reset stub + vectors to new banks 8-14, set header PRG count to 16), put English text in the new
  banks, and patch `$DBEE` (bank/split) and `$DE88` (verb list). Also
  consider changing the newline step (`ADC #$44` at `$E137`) to one row so
  English (no dakuten row) gets ~8 lines per box.
- Other text found: none in banks 0/1/4/5/6. The title-screen menu is not
  plain script (graphics/nametable data → stage 7). A kana grid layout
  lives in bank 7 `$F94A`-`$FCD3` (character/name-select screen?) →
  stage 7.

### Translation (stage 5)
- Style decisions and names: `script/glossary.md` (no honorifics, place
  names romanised, UK English, ASCII + ♥ only).
- `tools/encheck.py [files]` checks `script/en/` against `script/jp/`:
  identical code/raw-tile sequence, matching trailing newlines (they are
  real F5 bytes), and warns on lines > 24 glyphs or pages > 4 lines
  (name codes count as 7).
- `tools/enbuild.py msg_XXX draft.txt` turns a draft of `@@ ID` + English
  into the EN file with the right labels/trailing newlines, and greedily
  re-wraps any run of text lines that has a line over 24 glyphs.
- Done: all files msg_000-msg_380 (first pass, 2026-10-10, in a Cowork
  chat). Verb menu words are provisional until the menu slot width is
  known (stage 6).
- `script/en/*.txt` are the source of truth. The drafts fed to
  `enbuild.py` were scratch files and are not kept: for later fixes, edit
  the EN file directly and re-run `tools/encheck.py`.
- Stats for stage 6: 962 messages, ~31,200 visible English glyphs (JP
  ~20,800, so ~1.5x as expected). Character set currently used, 69
  glyphs: A-Z except X/Z, a-z, digits except 8, space, `! " ' , - . : ?`
  and `♥`. Make the font complete anyway (A-Z, 0-9) for later edits:
  ~72 tiles, fits the 142 free kana slots in CHR banks 30/31 and leaves
  ~70 for DTE pairs if space gets tight.

#### Handover: open points for later stages
- **Verb menu width (stage 6):** find the slot width used by `$DE6C`/
  `$DE88` (JP max 6 kana; 2-kana verbs are padded with a space, e.g.
  `き く`). If 6: shorten "Promise" (→ "Swear"), "Go down" (→ "Down"),
  "Stakeout" (→ "Case", as in "case the joint"). "Sleep" and "Coffee" were
  chosen deliberately: see the glossary's verb table.
- **Dialogue that names a verb:** 1BA mentions the "Shout" command;
  keep in sync with $3BE.
- **Raw tile `<41>`:** dropped in English in 14E and 182 (part of a JP
  word). encheck only warns for raw tiles; control codes must match.
- **Name codes:** `[cmdE1]`/`[cmdE2]` = this hero's given/surname,
  `[cmdDF]`/`[cmdE0]` = partner's. The partner is the "rival" competing
  for Remi. Names live in $254-$257 (Nakama, Toru, Kato, Hiroshi): check
  whether the hero/name-select screen (bank 7 `$F94A` grid, stage 7)
  draws them from there or from graphics.
- **`EE` code:** meaning still unknown (sets `$7007`, maybe expression/
  pose). Its position inside a line was kept roughly where the JP had it.
- **Newline step:** English never needs the dakuten row, so consider
  `ADC #$44` → `#$24` at `$E137` (8 lines per box). The script was
  written to the current limit of 4 lines/page, so this is optional.
- **Parked wording to revisit after playtesting (Stephen's call):**
  policeman 03B "Right, let's be 'avin' you" (a Sweeney-style line was
  considered but not adopted); "well fit" in 0E3; dog warden line 0F2 (done: "rounded up with the other strays", 2026-10-25);
  "Skylion" car name (done: now "Skyline", 2026-10-19); 12D "fountain in the park" (done: kept
  "park", a paved garden with a fountain pavilion, 2026-10-25; 0B1 is
  "playground"); Gen's Geordie and the "Canny"/"Cannit" sake puns.

### Insertion (stage 6a)
- `python3 tools/insert.py` → `out/bebop_en.nes` + `out/bebop_en.bps`
  (`out/` gitignored). The BPS is built against the original ROM (SHA-1
  above) and self-verified by re-applying it (see stage 6b for why no IPS). Needs `script/jp/` only for
  `encheck`, not for building.
- ROM layout: PRG 256 KB (header byte 4 = 16). Banks 0-6 original;
  banks 7-14 new (FF + the 16-byte `$BFF0` reset stub copied from bank 0);
  bank 15 = old fixed bank 7 + patches. English text packed from bank 8:
  bank 8 (IDs 000-113), bank 9 (114-229), bank 10 (22A-3C1, ~8 KB free).
  Banks 7 and 11-14 spare. Old JP text in banks 2/3 is now unused.
- Fixed-bank patches: `$DBEE` → `JMP $FD00` (new lookup: start-ID table
  at `$FD40`/`$FD43`/`$FD46` lo/hi/bank, selects bank via `$C049`,
  subtracts the start ID, `JMP $DC05` into the original skip loop);
  `$DE88` → `JSR $FD49` (`LDA #10 / JMP $C049`) and `$DE8C`/`$DE90` =
  verb list address (currently bank 10 `$A039`). Verb block is kept in
  one bank by the packer. Free fixed-bank space left: `$FD4E`-`$FFCF`.
- Font: `tools/font.py` (original design, 66 glyphs): A-Z `$00-$19`,
  a-z `$1A-$33`, `! ? . , ' " - : ; ( ) / & %` = `$34-$41`; digits keep
  `$42-$4B` (redrawn thin, slashed 0, plain 1; 2026-10-25), ♥ `$59`, space `$FE`. Written to CHR banks 30 and 31; ink =
  colour 0, background = colour 1 (same as the kana). Kana slots still
  free for DTE later: `$4C-$4F`, `$51-$58`, `$5A-$5D`, `$60-$8D`.
- Verified in Mesen: intro (message $238) shows English, 4-line page and
  page wait work. Not yet checked: verb menu, other screens.

### Stage 6b results
- **Verb menu:** slots are at columns 9 and 17 (rows 6/8/10, PPU
  `$20C9` + `$DEB3` row-0 offsets); the selected verb is shown by a
  palette change, not a box. A 7-letter verb fits in either column (left
  column leaves a 1-tile gap; right column ends one tile before the
  portrait). **Max 7 letters.** Only "Stakeout" (8) was too long →
  "Watch" (clearer than "Case" as a bare command). Verified in Mesen with a test build that opens
  menu `$2B` (Search / Go up / Go down / Stakeout→now Watch / Shout / Move).
- Menu table `$DEB3` is larger than first thought: 6 bytes × ~106 rows,
  `$DEB3`-`$E131`; script uses menu IDs up to `$64`.
- **Status panel** (left of the menu: きりょく / うんせい / どつぼ and
  the pip gauge) still shows kana; drawn from other tiles, not the font
  slots, so it is intact → translate as graphics in stage 7.
- **Patch format: BPS only.** The expansion moves the CHR ROM and fixed
  bank; IPS cannot copy, so an IPS would have to contain ~150 KB of the
  original ROM verbatim. `tools/insert.py` writes `out/bebop_en.bps`
  (~44 KB): SourceRead/SourceCopy for anything already in the original
  (including code-only messages), TargetRead with run-length fills for
  the rest. `check_no_rom_data()` fails the build if any 64-byte literal
  in the patch appears in the original ROM. The BPS also carries CRC32s
  so patchers (Floating IPS/Flips, beat, ROM Patcher JS) reject a wrong
  source ROM.
- **Newline step:** left at 2 rows (4 lines/page) since the whole script
  was written to that limit. Revisit only if playtesting wants denser
  boxes (`ADC #$44` at `$E137` → `#$24`, plus box-clear and page logic).
- Page-wait `▼` on pages that end with blank lines is drawn on the box's
  bottom border row (same as the Japanese, since trailing newlines are
  preserved) — check how it looks during stage 8.
- Intro and following school-corridor scene play through in English
  without errors (to ~frame 3500).

### Graphics (stage 7a)
- **Title screen** = raw nametable in PRG bank 1 `$AAC0` (960 tiles +
  64 attribute bytes), drawn with CHR bank 12 (`$1000`; `$7D`=15 for
  `$0000`). Rows: logo 3-11, kanji subtitle 13-14 (tiles `$C0`-`$CD`,
  `$D0`-`$DD`, 28 tiles), menu 17-22, copyright 25 ("©1988 DATA EAST
  CORP.") and 27 ("© <author name in kana> / YOUNG MAGAZINE").
- Title capitals in CHR 12 (three colour bands: rows 0-2 colour 1, 3-4
  colour 2, 5-7 colour 3): A `B7` C `BD` D `B6` E `B9` G `9D`/`7E` I `A4`
  K `6F` M `7F` N `A9` O `BE`/`8D` P `B2` R `BF` S `BC` T `B8` U `A8`
  Y `9F` Z `A3`, © `A2`, "." `88`, digits `AC`-`AE`. Drawn in 7a: H `27`.
- Tiles freed by the old menu kana (only used there): `28 39 48 49 59 67
  6A 77 78 79 7A 7B 7C EE FE` (`27` now H). `68` (dakuten) is also used
  by the author credit, so keep it until that is redone.
- `tools/title.py` (called by `insert.py`): clears menu rows 17-22,
  writes TORU NAKAMA / HIROSHI KATO / CONTINUE at column 11, and sets the
  attribute quadrants under the menu to the text palette (the English
  lines are wider than the kana ones). Verified in Mesen.
- **Stage 7b (decided with Stephen):** kanji subtitle kept; an English
  line "Legend of High-School Paradise" sits on row 15 under it (not
  beside: no room), centred on the kanji, in an original italic script
  rendered by `title.py` (ink colour 1 + colour-2 drop shadow, like the
  kanji; palette 0 shared with the kanji rows). It uses 18 of the freed
  tiles (6 spare). Wording is `SUBTITLE` in `title.py`.
- Author credit romanised as "©K.KIUCHI/YOUNG MAGAZINE" on row 27 (col
  6), keeping the original blank row 26 between credit lines. The
  full-name version needed two touching rows (title letters are 8 px
  tall); Stephen chose the one-line layout from a side-by-side mock-up.
  Row 26 is cleared only from column 6 so the DECO logo (cols 2-5, rows
  25-26) survives. `$7D` is the "/" glyph and `$88` is ".".
- The copyright lines' white→green banding is original, not a palette
  bug.
- **For 7c:** the status panel left of the verb menu (きりょく / うんせい
  / どつぼ + pip gauge) and the bank 7 `$F94A`-`$FCD3` kana grid.

### Status panel (stage 7c)
- Panel left of the verb menu uses CHR bank 30 at `$1000` (font bank) and
  palette 3 throughout: colour 0 black, 1 white, 2 pink (pip fill), 3
  light blue (background; the screen is filled with tile `$FF`).
- Labels are layout tiles in PRG bank 0: `$AEAB` (row 5) and `$AF2B`
  (row 9), starting column 2; the verb box border is column 8, so ≤ 6
  tiles. Now **NERVE** and **LUCK** (Stephen's choice; NERVE over STEAM
  because "steam" reads oddly as a stat), black as in the original, in the
  old inverse-kana tiles `$8E`-`$95` (letters only used here; `$9D` must
  never be used as it is a message control code).
- Gauge pips (row 7) are tiles `$FB` full / `$FC` half / `$FD` empty.
- Luck grade = message `$37A + level`, printed by `$EB6C` at PPU `$2162`
  (row 11, col 2) without clearing first. Grades worst→best: **JINX /
  BAD / FAIR / GOOD / CHARM** (Stephen's choice; originally どつぼ / 凶 /
  中吉 / 大吉 / ばりきち). Padded to 5 tiles (the original footprint) so
  a shorter grade fully overwrites a longer one. QoL change agreed with
  Stephen: grades are pink like the filled pips, with a black drop
  shadow for contrast, so the level stands apart from the black label.
  Grade glyph tiles are katakana slots `$60`-`$6E` in font banks 30/31.
- `tools/status.py` (called by `insert.py`) owns all of this; the grade
  words override messages `$37A`-`$37E` at build time (the EN file still
  holds the JP raw tiles for those five, which is expected).
- Verified in Mesen with test builds showing JINX and (forced) CHARM.

### Ending credits (found in 7c, for 7d)
- `$EE42` (ending sequence) sets CHR `$7E` = `$1D` (bank 29), points
  `($62)` at `$F941` and draws layout streams with `$EEED`: tile numbers,
  `$F5` = next row, `$FE` = blank, `$FF` = end. The streams run through
  `$F941`-`$FCD3`. Tables at `$EECC`/`$EED7` drive the sequence.
- CHR bank 29 holds the staff-roll glyphs: kanji role titles (原作, 企画,
  音楽 …) and katakana names. The earlier "kana grid" guess was wrong —
  the stream's tile numbers just coincide with dialogue-font kana slots.

### Ending credits (stage 7d)
- Stream format (`$EEED`): byte 0 = low byte of PPU `$20xx`; then tiles;
  `$F5` = upload the run and move down a row (same start column); `$F6 n`
  = move the start column right by n; `$FF` = end. 12 streams: 0 =
  opening exclamation (drawn once before the loop), 1-10 = role screens,
  11 = 終. The loop (`$EE83`, counter `$6C` to 11) clears the top 13
  rows (`$EF50`), changes the lower scene, draws a stream, waits 256
  frames; ~310 frames per screen. The English version keeps the same
  timing to within ~25 frames.
- **CHR bank 29 is not credits-only.** Eight tiles never appear in the
  credit streams — `$81 $BB $FF` (ending frame graphics) plus blanks
  `$E6 $F0 $F1 $F5 $F6`. Overwriting `$81` broke the sprite-0 hit that
  the NMI waits for before its mid-screen CHR switch (`$7F` = bank 6 for
  the lower scene), which hangs the game. `credits.py` starts from the
  original bank and never touches those tiles.
- `tools/credits.py` (called by `insert.py`) rebuilds bank 29: the
  dialogue font at the same tile numbers (so names use `font.char_map`),
  white-on-black role letters (1 px left margin), and pixel-doubled 16×16
  letters for the big opening/closing text; streams are regenerated into
  `$F941`-`$FCFC` (526 of 956 bytes).
- Current English (defaults, for Stephen to review): opening "ARGH!"
  (JP: a large "んがっ"); roles ORIGINAL STORY / PLANNING / GRAPHICS ×2
  / MUSIC ×2 / PROGRAMMING ×2 / SPECIAL THANKS ×2 (原作 / 企画 / 絵画 /
  音楽 / プログラム / 協力); staff names romanised from the hiragana in
  Western order, Hepburn without macrons; closing THE END (終).
  Uncertain readings: じちょう (JICHO), ぐもん (GUMON), しんきゅう
  けいゆう (KEIYU SHINKYU).
- Verified in Mesen with a test build where a spare control code
  (`cmdDB`) is pointed at `JSR $EE42` and placed at the start of the
  intro: every stream is reached in order, opening/closing big text and
  all ten role screens render, no hang. (The test build returns to the
  intro afterwards; that is an artefact of the hack.)

### Scene-art text survey (stage 7e, step 1)
Scene graphics are CHR banks 0-11 and 13-28 (12 = title, 29 = credits,
30/31 = font). Banks 16-28 are portrait/face pieces with no text. Text
found (bank, tiles as col,row in the 16x16 tile grid):

| # | Bank / tiles | Japanese | Meaning | My read on gameplay value |
|---|---|---|---|---|
| 1 | 8 / 0-4,8-A | 閉店 | "Closed" (shop shutter) | **Gameplay**: explains why only Leave works |
| 2 | 3 / C-F,A-B | 東町駅 | Higashimachi Station | Useful: names the location the dialogue refers to |
| 3 | 3 / 9-A,1-2 | 全 (or 金?) | "all" / "gold, money" — rooftop sign | Unclear; likely flavour |
| 4 | 3 / 5-B,8-9 | ＋ 第一 | cross + "Daiichi" (No. 1) — clinic/hospital sign? | Possibly useful if the player must find a hospital |
| 5 | 3 / E-F,4 | small kana, unclear | shop sign | Flavour |
| 6 | 5 / 0-3,A-B | 酒蔵 | sake store / brewery | Flavour (maybe location ID) |
| 7 | 5 / 5-6,8-9 | コーヒー under a cup | "Coffee" | Flavour (the cup says it) |
| 8 | 9 / 3-4,8 | 両替 | "Change" (coin exchange, arcade) | Flavour |
| 9 | 9 / E,5-7 | vertical "…円…" | price sign, e.g. "N yen" | Flavour |
| 10 | 14 / 2-3,4-7 | 大売出 | "Big Sale" banner (a sprite) | Flavour |

Already English in the art: DECO (banks 0, 7), GAME, AFTER BURNER,
OSCAR (bank 9), COFEE (bank 5), DARK… (bank 7).
Where each sign appears:
- **Scene pictures** (lower window): loaded by `$EC7A` with a picture
  number (`[cmdF0 xx]` in the script, also the credits loop). CHR bank =
  `$ED2E[pic]` (into `$7F`); tile layout = PRG bank 1 `$8000 +
  $ED53[pic] × $130`: 20×14 tiles then 24 attribute bytes (written at
  `$23D9`+). 37 pictures, CHR banks 6-13 and 28 only. Signs: #1 閉店 in
  picture `$1D`; #8 両替 (red door) and #9 vertical "…円ゲーム" ("N-yen
  games") in picture `$10` (the arcade). Captured in Mesen with a test
  build whose intro is `[cmdF0 xx][page]`.
- **Street areas** (walking views): `[cmdEC area x y]` → bank 6 `$9AEC`
  object/placement engine; area BG bank = `$C676[area]` (areas 0-5 →
  CHR banks 0-5). Signs #2-#5 are in area 3, #6-#7 in area 5. These are
  only drawn in walking mode, so they could not be captured from a test
  message — capture them during stage 8 playtesting.
- #10 大売出 is in sprite bank 14 (a character holding a banner).

Decisions (Stephen, 2026-10-15): #1 gets a caption; #8 and #9 are
flavour. #2-#7 and #10 to be judged once seen in context (stage 8).

**Caption for #1 (done):** a caption above the picture (row 12) was
rejected after checking: dialogue bubbles use row 12 for their bottom
border (intro: rows 2-12, tail into row 13), and pictures change
mid-dialogue, so drawing or clearing there would corrupt bubbles. Instead
`tools/sceneart.py` draws "CLOSED" (with quotes) on the shutter under the
kanji (picture `$1D` row 6, cols 6-13), in spare CHR bank 8 tiles.
Stephen chose the 'overlay' style: letters drawn over the original art
tiles in plain white (no plate, no shadow) so as little artwork as
possible is covered. Choose the style per caption; a black shadow
(`('overlay', 3, 0)`) or a plate may suit other backgrounds better. Spare = unused by every picture on that bank AND not a frame tile:
the frame round every picture is drawn from the scene bank with tiles
`$02` (left), `$07` (right), `$2A` (bottom), `$FF` (surround) — reusing
`$02`/`$2A` broke the frame in the first attempt. Also `$BB`: row 13
(just above the picture) holds the frame's top line (`$BB`) in menu and
dialogue mode, and the NMI's CHR switch happens partway down that row, so
its lower scanlines come from the scene bank. Reusing `$BB` gave a
flickering strip of letter fragments above the picture (seen by Stephen
in real play; my first test had no menu/box so missed it). Test captions
with the verb menu on screen, not just the bare picture.

**Menu highlight fix:** the highlight is 8 sprites behind the menu text
(`$EA0D`, offsets `$EA80` Y / `$EA88` X); JP covered 6 tiles + 2 on the
dakuten row, so 7-letter verbs (Promise, Go down) lost their last letter.
Now 7 on the text row + 1 parked on the row above (same per-scanline
sprite count). Patched in `insert.py`; verified on "Go down".

Next: once #2-#7/#10 are seen, caption any marked gameplay with
`sceneart.py` (street-area signs will need the bank 6 area engine, not
the picture loader); then find the scene layout
that places the marked tiles and add an English caption beside them
(free tiles in the same CHR bank permitting).

### Stage 8a results
- `tools/pagecheck.py` replays every dialogue message through a model of
  the text engine (start `$2084`, F5 = 2 rows, page cursor drawn one
  space after the last character, box interior cols 3-28 / border col 29,
  4 lines) and reports problems the English has but the Japanese did not.
  Found and fixed: 19 pages with 4 lines + a line break before the page
  code (cursor on the bottom border; break removed, no wording change);
  7 pages ending on a 24-character line (cursor on the right border;
  trimmed by a word, Stephen approved each); 375 jumping into 1C4 with
  the cursor below the box (reflowed to 3 lines). Now 0 issues. **Rule:**
  the last line before a page wait must be <= 23 characters; name codes
  count as 7 (given) / 6 (surname).
- Change audit (built ROM vs original): every changed byte belongs to a
  deliberate change (header, labels, title layout, picture 1D caption,
  fixed-bank patches, text banks 8-10, CHR 8/12/29/30/31 tiles). Banks 7
  and 11-14 unused (at the time; since then 11 = day goal, 12 = text, 14 =
  caretaker data). CHR 29 tile `$81` untouched (sprite-0 split).
- No English message other than the luck grades prints raw tiles, so the
  reused inverse-kana tiles cannot leak. All 24 verbs <= 7 letters.
- Ending: verified via the `cmdDB` shortcut (same `$E770` → `$EE42`
  call as the real game); the build-up in real play is left for 8b.
- Wording fixes from Stephen's play so far: Promise bridge in 02B, 014
  retort, Nobuo's full-name gag in 19A, 203 "face pass" joke; glossary
  style notes on self-reference and Promise.

### Added messages (QoL)
- `tools/additions.py` holds messages the translation adds, with IDs
  after the last original one (`$3C1`), and the fixed-bank patches that
  use them; `insert.py` appends them and `pagecheck.py` checks them.
- `$3C2` out-of-NERVE line (Stephen, 2026-10-17): the `$E8` "lose a NERVE
  pip" handler jumps to the shared ending `1C4` when the gauge empties
  (`$E8D7`); `1C4` is also the arrest (`0F5`) and car-charge (`375`)
  ending, so the original never said why. `$E8DE` now points at `$3C2`, a
  copy of `1C4` whose first page reads "Guv, you've lost your nerve.
  We're finished!". Verified in Mesen by draining the gauge with `cmdE8`.
  - That path never resets the text cursor, so the message started where
    the last line ended and ran into the border (Stephen, 2026-10-18).
    `$E8DB` now calls a helper at `$FFC0` (`JSR $EAF5` / `JMP $E9AC`), which
    puts the cursor back at the top. Checked in both emulators, with and
    without the fix.
- NERVE is `$71B8`, counted in half-pips (5 pips = 10); each `cmdE8`
  removes one and waits for a button.
- **How NERVE changes** (traced 2026-10-18, after Stephen saw sleep not
  raise it):
  - A new game sets it to 5 (2½ pips, `$DA91`). `$E891` adds ½ (capped at
    10); `$E8B5` takes off ½ (game over at 0).
  - **Up, only by:**
    - winning a fight: the fight sub-commands (`cmdEA` `06`, `0F`-`11`,
      `14`-`20`) run `$E2FF`; a win (carry clear) gives +½ and a loss −½;
    - one date: `07B` "Go on then, I'll let you treat me" (`cmdE9`).
      It's the only `cmdE9` in the script.
  - **Down:**
    - losing fights;
    - being turned down and other put-downs (`cmdE8`);
    - the clock running out (`339` "If you don't sleep at night...");
    - the teacher catching you out late;
    - Sleep at night.
  - **Sleep never raises it.** `cmdEA 09` (`$E41F`) takes ½ off if the
    night flag `$71AC` is set; in the morning or evening it does nothing.
    `$71AA`/`$71AB`/`$71AC` are the morning/evening/night flags
    (index `$71B9`).
  - The caretaker's help was wrong ("sleep puts it right") and is now
    corrected.
  - **Home menu by time** (`25F` → `260` / `36D`):
    - first visit (flag `03` clear): Search / Save / Leave. Search gives
      Nobuo's tip (`188`) and sets flag `03`;
    - morning (`$71AA`): Save / Shout / Leave, with **no Sleep**;
    - evening and night: Sleep / Save / Leave.
    - So bed is only possible from evening. Sleeping in the evening is
      free; at night it costs ½ pip (Stephen noticed no Sleep by day,
      2026-10-18).

- **Police (scene 294):** town-map characters (area 6 slots 33-35), gated
  on flag $71; they only block the school exits at the start and are gone
  after the bomb-threat call (038 clears $71). Picked up at night (flag
  $AC) → teacher fetches you (33B), −½ NERVE. Not a night patrol, so the
  caretaker no longer says "or the police nab you"; now "Stay out late, and
  you'll end up back home exhausted." (Stephen, 2026-10-24).
  Staying out to midnight is the `$C352` return home (339).
- **Clock bug fix (original game, found by Stephen 2026-10-24).** Time:
  `$71C5` minutes (+1 every 64 frames, `$C411`), `$71C6` hour, `$71C8`
  day; 1 in-game hour = 56 ticks, about 1 real minute. At minute 0 the
  hour is checked against `$C31C` (7 morning, 17 evening, 20 night, 0);
  at 7:00 `$C33F` resets luck to JINX, sets flag $A9 and clears flag $17
  (today's slip). The new-day routines (sleep, overnight stakeout `cmdEA
  03`) set 7:00 but INC the minutes; from minute 54/55 that skips past
  the `CMP #$38 / BNE` rollover, the minutes wrap round with the hour
  stuck at 7, and the 7:00 reset fires again (luck lost after buying the
  slip). `$C41F` BNE → BCC. Tested in Mesen and Nestopia (minute 57 at
  7:xx: old build back to 7:10 + JINX, fixed build 8:04 → 11:39, CHARM).

### Optional: help pages (idea 2026-10-17, design agreed; not scheduled)
Goal: explain the basic mechanics in-game, since they are opaque without
the manual (see `docs/manual-guide.md`).
**Chosen design (Stephen):** an original, nameless **school caretaker**
(用務員, yōmuin — the familiar "caretaker man" of Japanese school
stories) standing on the map near Aitoku High, the starting area. Meeting
him opens a scene with Talk / Leave; Talk gives a few help pages: NERVE
(what drains it, sleep at home to restore it), LUCK (fortune slip at the
shrine each morning), saving only at home, being home by evening. Plain,
readable lines, mildly in character ("Seen plenty of lads like you come
through here...").
- **Preferred placement (Stephen, 2026-10-17):** his room is inside the
  always-shut building just south of the Aitoku High school building. Its
  door gets the open-door map tile (as on the Mai restaurant when open);
  walking in opens a scene (picture + Talk / Leave), like any shop. No
  new walking character on the map, so less risk. **Check first:** is
  that building/door ever used (story flags, time of day, a 閉店 shop)?
  Trace how map doors link to scenes. Fallback: the caretaker standing
  on the street nearby (below).
- **Findings (2026-10-17): the building is unused.** Its orange door is
  plain wall (no door attribute), and the door table has no entry for it.
  How map doors work:
  - Town = area 1. The map is stored raw in bank 0 at `$800F`, $18 blocks
    wide, one byte per 4×4-metatile block. The game copies it to `$6803`.
    The building is block `$0F` at block (5,$12); block `$0F` is used 15
    times, so don't edit it.
  - Per-area tables, indexed by area `$3F`:
    - `$C6C9`: block definitions (area 1: `$8827`, $48 blocks of 16 bytes,
      ending where the metatile table starts at `$8CA7`);
    - `$C6D5`: metatiles (4 tiles each);
    - `$C6E1`: metatile attributes (area 1: `$A8D2`). In the attribute
      byte, bit $20 = door, bit $10 = solid, low bits = palette.
  - **Block `$3D` is never used in area 1**, and no code writes it, so it
    can be redefined as a copy of `$0F` with the door metatiles
    `$4A`/`$4B` → `$50`/`$5A`. `$50`/`$5A` is the dark open doorway used
    by the school and the awning shop. Then set map (5,$12) to `$3D`.
    The door metatile `$5A` sits at (x $14, y $4B).
  - Bumping a door tile → `$C517` scans the door table at `$EF97`. Each
    entry is 6 bytes: area, x, y (metatiles = pixel position / 16),
    message lo, message hi, flag. The list ends with `$FF`.
    - Flag `$80`+n: message, with n → `$037D`.
    - Flag `$01`: warp, where "message" is a pointer to another entry.
    - Flag `$00`: nothing.
    - Entry 0 (area 1, $17, $40) is the new-game start position (`$C67C`
      indexes entries ×6 from `$EF97`). Don't remove it.
  - To add the room: copy the table plus the new entry (01 14 4B id `$80`)
    into free fixed-bank space, and patch the scan base at `$C51F`/`$C525`
    (`#$97`/`#$EF`). Leave the old table in place for warps and starts.
  - Scene message: `[cmdDE 22][cmdF0 pic][cmdEF face][menu-call 41 talk
    09 03]`. Menu `$41` = Talk / Leave; `0309` is the empty Leave message.
  - **Decision (Stephen):** the caretaker is a proper animated scene
    character (like the teacher), drawn over a new room picture. Fallback:
    paint him into the room picture (static). The small face beside the
    menu is the player's own face, so it needs no change.
  - **Scene characters (decoded):** `[cmdEF id]` picks the character drawn
    over the scene picture (`$7006`, handler `$E208` → loader `$F88D`), and
    `[cmdEE n]` picks his expression (`$7007`). With no `cmdEF`, the picture
    is drawn empty.
    - Record pointers are at PRG bank 5 `$8000` + id×2, ids `$00`-`$36`.
      The data follows at `$806E`, so the table can't grow in place.
      `$34` and `$37` are special-cased to bank 6 `$B500` and `$BD00`
      (`$F8AC`, and again at `$F92C` when drawing).
    - Record layout:
      - byte 0: CHR bank for the sprites (16-26);
      - bytes 1-4: unknown (usually 0);
      - bytes 5-13: 3 sprite palettes × 3 colours;
      - from byte 14 ($0E): frame pointers, 2 per expression (offset
        $0E + 4n = mouth closed, $10 + 4n = talking frame).
    - Frame layout: byte 0 (→ `$9D`), then triplets (cell 0-143,
      attribute, tile), ending with `$FF`. Cells form a 12×12 grid of 8×8
      sprites. Frame 0 is the full body; the other frames are deltas.
      `$F660` converts it to OAM from `$0700+$24`, with the origin at
      x `$50`, y `$88` for ordinary characters.
    - **Hardware limit: at most 8 non-empty cells per row** (the teacher
      uses 4-8 per row), or sprites drop out on a real NES.
    - Teacher (id `$03`): CHR bank 16, frames `$8873`/`$8907`/`$88FF`/`$8907`.
      Rendered correctly from ROM by a script in the scratchpad (`char.py`).
  - **Plan for the new character (id `$38`):**
    - Put the record in a spare PRG bank (7 or 11-14).
    - Hook `$F8AC` and `$F92C` so that id `$38` selects that bank, with a
      pointer to the record.
    - Tiles: bank 26 is only partly used by characters (94 of 256 tiles
      referenced). Check what else uses banks 26/27 before claiming tiles.
      Bank 29 (credits) has ~120 free tiles for the room picture.
    - Art budget: about 50-60 sprite tiles, 9 colours, 2 frames.
  - **Tile space (checked 2026-10-17):**
    - CHR is at the MMC1 maximum, so everything must fit in existing gaps.
    - Banks 26 and 27 are full (27 holds artwork used elsewhere).
    - Unreferenced picture tiles: bank 6 = 55, 10 = 54, 11 = 51.
    - Bank 29 has 116 tiles left after the credits. Credits use only
      uppercase, so the 25 lowercase tiles (not `$2A`) are free too.
    - In a scene, `$7E` = font bank (top), `$7D` = sprite bank (character,
      default 16), `$7F` = picture bank (default 6, `$DB76`). Sprite 0 is
      tile `$19` at y `$69` (the font's "Z", above the split).
    - Plan: **room picture in bank 29** (draft needs 84 unique tiles).
      Copy frame tiles `$02`/`$07`/`$2A` in from bank 10; `$BB`/`$FF`
      already match. Move the credits' C and H (font tiles `$02`/`$07`) to
      free tiles in credits.py. **Caretaker sprites in bank 6**, using its
      55 tiles that no picture uses (draft needs 47).
    - Picture palettes: 13-byte records in the fixed bank from `$D356`
      (background colour + 4×3). Picture n uses record 20+n; record 3 is
      the text palette `20 36 21`.
    - Attributes: picture block (bx,by) → attribute byte
      ((6+2bx)/4 − 1) + 6·((14+2by)/4 − 3), quadrant from the remainders.
      Quadrants outside the picture keep palette 3.
    - A new picture (number 37) needs hooks for the loader tables
      (`$ED2E`/`$ED53`), the layout (bank 1 is full after `$A990`) and
      the palette record.
  - **Art drafts:** `tools/caretaker/` (`char.py`, `room.py`, `mock.py`).
    - Caretaker: bald, grey sides, bushy brows, moustache, kindly closed
      eyes, navy jacket over a grey waistcoat; mouth-open talking frame.
    - Room: wooden ceiling, window (school outside), calendar, key
      board, desk with kettle and mug, fire extinguisher, and a wooden
      tool box (spanner, screwdriver, hammer). The tool box replaced the
      broom (Stephen): pupils do the sweeping in Japanese schools. The
      broom is kept as `room.PROP = 'broom'`.
      floorboards.
    - **Approved by Stephen (2026-10-17)**, with the clock removed (it
      could never show the game's changing time of day).
  - **Built (2026-10-17):** `tools/caretaker/build.py`, applied by
    `insert.py` after the credits. Scene `$3C3` and help `$3C4` are in
    `tools/additions.py`, using wording B (Stephen). Two changes from the
    draft: pupils do the sweeping in Japanese schools, so he's "keeping
    this place going"; and "lads" (he's talking to both heroes).
    - Later tweaks (Stephen):
      - page 1 is now "Been keeping this place going as caretaker since
        before your time": they already know him, so it's a habitual
        grumble rather than an introduction;
      - the NERVE page puts sleep first, then "But run out completely,
        and you're done for", so running out is clearly final;
      - **random sign-off**: the last page ends `[goto $3C5]`, and a hook
        at `$DBEE` (the message lookup) swaps `$3C5` for one of `$3C6`-
        `$3C9`, picked by frame counter `$6E` & 3: gutters ("unblock") / boiler /
        leaky tap / tea's going cold (Stephen: no bins, less degrading;
        no doors, since the map shows his door always open).
      - the room changes with the time of day (Stephen chose this):
        evening sepia and night pale blue, like the school corridor (the
        palette record holds three sets, chosen by `$71B9`). The game also
        dims sprites at night, so he darkens like any other character.
    - The door entry is area 1, (`$14`,`$4B`). The door table, palette
      record and hooks take ~490 bytes from `$FD50`. Layout and record are
      in PRG bank 14.
    - Things found while building:
      - Every character bank shares sprite tiles `$F6`-`$FE`: the speech
        tail (`$F6`-`$FB`) and the menu highlight (`$FE`, solid colour 3).
        Sprite 0 is tile `$19` of the character bank.
      - Bank 6 got the shared sprite tiles. Its picture tiles on `$FA`-`$FD`
        moved to free tiles, with those layouts repointed. Pictures 1, 3,
        `$0D` and `$21` were checked pixel-identical.
      - The caretaker reuses mirrored tiles via the sprite flip bits
        (36 tiles).
      - Credits: only the letters the names use are copied now. C and H
        moved off the frame tiles `$02`/`$07`. The credit screens were
        checked identical.
    - Loading flash fixed (2026-10-18, seen by Stephen): the loader fills
      the picture area with tile `$00` before drawing it. `$00` is blank in
      every picture bank, but in bank 29 it was the credits' "A". `$00` now
      joins the frame tiles: the credits' A moves elsewhere, and the blank
      is copied in. Credits re-checked identical.
    - Tested in the headless Nestopia and in Mesen, with the same result:
      door → room → Talk (8 pages, mouth animates) → menu → Leave → back
      on the street.
- Must be on the map, not in the intro: Continue on the title screen
  (with no game in progress) starts without the intro.
- Reuse existing old-man graphics (a townsperson walking sprite and a
  picture/portrait), so no new art.
- Main work: decode the map object engine (bank 6 `$9AEC` via
  `[cmdEC area x y]`; per-area object tables around `$0494`, `$937D`,
  `$93CD`, `$9416`): how objects are placed, table sizes, and how an
  encounter starts a scene and its menu. Same knowledge helps caption the
  street-area signs (#2-#7).
- Then: add the object, a scene (picture + menu) and the help messages
  via `tools/additions.py`; check with encheck/pagecheck; test with the
  menu/box on screen and on Stephen's handheld (Overclock 1x).
- Risks: table space, disturbing an area's existing logic.
- Rejected: Select-button help (needs a menu hook, less discoverable);
  Nobuo after the intro (intro already long, skipped by Continue); Tomezo
  (his lisp makes help hard to read); the shrine priest (odd on a street).
- Estimate: 2-3 sessions.

### Stage 8b batch 1 (2026-10-16/17)
Fixed from Stephen's play (screenshots and save states):
- Wording: 02B Promise as "meet up / a date" bridge; 014 "what d'you
  think you're looking at?!"; 028 Megumi's 100-metre rule; 02A "sweet
  talk" (not "patter"); 19A Nobuo's full-name gag; 203 Nobuo's "face
  pass" on the underground; 238 "You want to team up...?"; "you two" ->
  "you lot" (03F, 040, 0F5); 195/199 Noboru pun replaced with English
  jokes; shrine fortune slips (189-18D, 1F7, CHARM = "the world's your
  oyster!").
- Verbs: Grovel -> Flatter, Menace -> Lean on (all responses checked).
- QoL: added message `$3C2`, the out-of-NERVE explanation.
- Manual: `docs/manual-guide.md` (English guide to the 1988 booklet,
  mechanics mapped to our names).
- Decided to keep: "extremists"; tough-guy third-person boasts and
  Nobuo's full-name gag; the vague shared game-over line for the arrest
  and car-charge endings.
Open:
- Junko: glossary says she refers to herself as "Junko" — review her
  lines against the self-reference rule (cutesy name-for-I -> "I").
- Street-area signs #2-#7, #10 (stage 7e survey) when Stephen meets them.
- Optional help pages on Select (see below).
- Reading Stephen's save states: `~/.config/MesenCE/SaveStates/
  bebop_en_N.mss`; the first zlib stream (offset 35) is a 256x240 16-bit
  screenshot (NES palette index in the low 6 bits). Use it to identify
  the scene, then find the message in the script.

### Map corruption on other emulators (2026-10-17, solved: emulator setting)
Stephen saw every other metatile row of the town map left blank (the
cleared fill tile) after Leave on his handheld (ArkOS, RetroArch 1.20.0,
Nestopia 1.52.0), in the Japanese ROM too; never in Mesen or his desktop
Nestopia. Decoding the handheld's RetroArch states (`#RZIPv` container ->
zlib -> Nestopia `NST` chunks: CPU RAM, PPU `NMT`, mapper `MM1`) showed
normal registers and half the rows simply missing.
**Cause: the core option `nestopia_overclock = "2x"`.** The overclock
adds extra scanlines per frame; this game redraws the map with the screen
off as fast as it can, and the writes landing in the inserted lines are
lost. Setting Overclock to 1x fixes it. A speculative ROM-side fix (an
NMI guard around the map's direct uploads) was tried and removed; the
ROM's code is unchanged here.

### Release notes (for the patch readme)
- **Emulator settings:** set **Overclock to 1x** (no overclocking). With
  overclocking (e.g. RetroArch Nestopia's "Overclock 2x", common on
  handheld setups) the town map is half-drawn after Leave — every other
  row stays blank until you walk over it. The original Japanese game
  does the same. In RetroArch: Quick Menu -> Core Options -> Overclock ->
  1x, then Manage Core Options -> Save Game Options to keep it for this
  game only.
- Apply the BPS patch to the original Japanese ROM (SHA-1 above).

### Quality-of-life changes (keep up to date; for the patch readme)
Beyond the translation itself. Details in the sections named.
- **New content**
  - Caretaker's room (new door south of Aitoku High): Talk (NERVE,
    nightfall), Ask (fortune slips, LUCK, saving), Beg → Promise (optional
    luck cheat: every slip is CHARM; saved, permanent), Flatter (a hint
    for the next story step, 39 in all, written from Stephen's
    walkthrough). Own picture and character, evening/night tints, random
    sign-offs split between Talk and Ask. See "Optional: help pages",
    "Caretaker extras".
  - Department store picture variants: annexe 3F/4F, main 4F and annexe
    roof each look different. See "Department store variants".
  - Corridor floors: the Nishiyama Building (1F-3F: own door colours,
    extinguisher on 3F) and the area-0 flats (nameplates on every door, as
    Search on 3F reads Tsuji's; 1F potted plant, 2F umbrella) no longer
    share one picture. See "Corridor variants".
- **Bug fixes (original game)**
  - Clock: after sleeping or an overnight stakeout, a new day could
    repeat the 7:00 reset later that morning (luck back to JINX, today's
    slip forgotten). `$C41F` BNE → BCC (2026-10-24).
  - Running out of NERVE started its message mid-box (cursor not reset).
  - Kakui roof: after Search (bomb, 1C6) and Take (1C8), Go down needed
    three presses (each message jumped into a fresh roof menu, nesting a
    level). They now just end, back to the menu you were on (2026-10-25).
  - Stakeouts (roof Watch, car, cmdEA 01/03) added two days when started
    in the morning or evening: time-skip mode 1 ends in the new-day
    routine, then mode $80 starts another. Mode 1's new day now gives the
    day back (`$C3A8` -> helper, now at `$FFC6`); one day per stakeout
    (2026-10-31, both emulators).
  - Out at midnight added two days too (the clock's 0:00 day + the trip
    home's new day, `$C352`/`$C361`); now uses the same helper, so you wake
    on the next day like going to bed in the evening. Checked the earlier
    7:00 re-reset fix still holds: after midnight and after stakeouts
    started at minutes $36/$37, CHARM luck survives four in-game hours
    (2026-10-31, both emulators).
  - Pachinko Shout: the cop's line waited for A before it appeared, then
    cut straight to the police station. The wait is now at the end
    (2BE/134, 2026-10-25).
  - Pylon: Use still blew it up after the bomb was handed to Onijima
    (0F6 clears $9A but leaves $42, which the Kakui roof's Take needs).
    Use now checks $9A: Nobuo "Guv, we already gave the bomb to the
    police. Probably for the best." (additions.py, 2026-10-31).
  - Happiest ending, Toru's run: the second arrival ("Oh! Someone else is
    here.", 246) shows picture `$E812[hero]`, `$24` for Hiroshi (Toru in
    the doorway) or `$25` for Toru, which was never drawn: the original
    read past its picture tables (garbage), and ours showed the
    caretaker's room (Stephen, save 6). New picture `$30`
    (`tools/endingpic.py`): `$24` with Hiroshi's perm in the doorway (olive
    with dark curls as in his scenes, outlined, no wider than his head and
    tapering in: Stephen chose "B3"); the
    man seated on the right is the same in both runs and stays. Bank 13's
    free tiles; `$E813` = `$30`. The extra picture-table entries needed
    the day-fix helper moved from `$FFA9` to `$FFC6` (after the NERVE
    helper). Checked both heroes in Nestopia, Toru's in Mesen; day fixes
    re-tested (2026-10-31).
  - Happiest ending, 241 (Shingo: "...the only real mate I've got, eh?
    Mmmmmmm."): the JP script has a stray `[page]` before its closing
    `[cmdED][delay 3c][page]`, so a blank box waited for A. Removed (240,
    the other branch, has none); listed in encheck's CODE_CHANGES
    (Stephen, save 8; 2026-10-31, both emulators).
  - Same slip in 247 ("Whyyy, you...!!"): it opens with `[page]`, but 246
    already ends with one, so a blank box waited for A (the code switches
    the hero to his angry face in between). Removed, so the face changes
    as the shout starts; CODE_CHANGES (Stephen, save 9; 2026-10-31, both
    emulators, both heroes in Nestopia). The less happy ending ($E81A)
    reuses 247 after 244 ("Oi, Hiroshi, it's great here! Come on in!"),
    which had no page wait, so the shout ran on past the box (Stephen,
    save 7): 244 now ends with `[page]` (only used there), so there too
    the face changes as the shout starts (both emulators; both heroes in
    Nestopia).
- **Clearer feedback**
  - Out-of-NERVE game over says why ("Guv, you've lost your nerve. We're
    finished!") instead of the shared arrest/crash ending.
  - Day goal (2026-10-31): the caretaker's Coffee tells you the day limit
    for the happiest ending; Select in a scene shows GOAL / DAY3/8 /
    14:05 in place of LUCK (pink once the target is missed).
  - Status panel: luck grade in pink with a drop shadow, like the pips.
  - Verb menu: the last letter of a highlighted verb is highlighted too.
  - Digits redrawn thin to match the letters (the game's were bold), with
    a slashed 0 and a plain 1 (2026-10-25).
- **Text that vanished before it could be read now waits for A:** 1FA,
  045, 07A, 082, 138 (before a NERVE loss); 07B (Misako agrees to
  coffee); 238 (the intro's last line).
- **Extra pages / bridge lines so a joke or action is clear:** 236 (car
  Shout), 388 (tailing Teru), 38A (slipping past the thug), 207 (the Joto
  boss), and scene-only copies of shared Nobuo lines (Use, Misako's date,
  car Use).
- **Menu:** Misako's coffee date offers Give instead of Ride (one byte in
  that menu only).
- **Expression timing:** 196, Nobuo keeps his smug look through the pause.
- **Map:** cars drawn in the Nishiyama Building car park for both car
  scenes (the red car always; Teru's black car while you're tailing him).
- **Map:** an English "SAFETY ✓ FIRST" sign above the Japanese 安全✚第一
  on the Higashimachi building site, so the big, clear Japanese sign
  reads as the standard slogan, not a clue (`tools/sitesign.py`; area 3,
  block $14 + spare block 0, CHR bank 3; 2026-10-25).

### Tools
- `tools/dis6502.py BANK ADDR [N]` — quick disassembler over the ROM.
- `tools/bebop.tbl` — script table (see above).
- `tools/insert.py` — build English ROM + BPS patch.
- `tools/font.py` — English font + char→tile map.
- `tools/title.py` — title-screen menu, subtitle and credit (stage 7a/b).
- `tools/status.py` — status panel labels and luck grades (stage 7c).
- `tools/credits.py` — ending staff credits (stage 7d).
- `tools/sceneart.py` — English captions inside scene pictures (stage 7e).
- `tools/pagecheck.py` — text-box layout check for every message (stage 8a); run after any script edit.
- `tools/additions.py` — messages added by the translation (new IDs from `$3C2`).
- `tools/script.py check | show ID…` — message parser (stage 4 builds the
  full dumper on this).

### Tooling notes (mesen-for-ai)
- Execute breakpoints use `access: "exec"` (not `"execute"`); also
  `read` / `write`. Use `memoryType: "nesMemory"`, `cpuType: "nes"`.
- Verified: an exec breakpoint at RESET fires during `run.step_frames` with
  `reset: true` (cycle 7, opcode $78 SEI). The step **stops at the hit**
  (returned at frame 0, not frame 1), so step again to continue.
- `video.export_frame` writes PPM; convert with PIL to view.
- Input: `input.set` with `{"start": true}` / `{"a": true}`, step ~5
  frames, then release. From reset: 300 frames → title; Start → intro
  dialogue by ~frame 545; A advances pages.
- PPU memory types: `nesNametableRam`, `nesPaletteRam`, `nesChrRom`,
  `nesPpuMemory`, `nesSpriteRam`.
- CDL export JSON: `bytes[i].code/data` plus a `summary` range list.
- Watches on `nesPrgRom` never fire; watch the CPU address via
  `nesMemory` instead. Watch events stay in the buffer across
  `watch.list` calls and a busy watch (e.g. `$2002`) can produce >100 KB
  — delete noisy watches immediately and filter events by `handle`.
- Intro timing: page 1 at frame ~545, A → page 2 (~750), A → page 3
  with bank 3 `$A3F8` read by `$EA08` from frame 760, one char / 3 frames.

### Caretaker extras (agreed 2026-10-23)
Optional QoL on top of the caretaker's room (see "Optional: help pages").
- **Menu:** before Beg: Talk / Ask / Beg / Leave. After Beg (flag set):
  Talk / Ask / Beg / Promise / Flatter / Leave (six slots, the maximum).
  The scene picks the menu row by flag. Menu ids $01, $09, $0A, $28, $4A
  and $4D are never used by the script: check the code doesn't use them
  either, then take two.
- **Talk:** first half of the current help (NERVE, home before nightfall).
- **Ask:** opens like an Ask about Shingo ("I turn a blind eye to what
  the students get up to, but I'll tell you this..."), then fortune
  slips, LUCK and saving.
- **Beg:** he tells you about the cheat and the hints, and asks you to
  promise not to abuse the luck. Sets the flag that shows the big menu.
- **Promise:** turns the cheat on for good (saved with the game; no off
  switch). The cheat must be clearly explained before this.
- **Cheat:** fortune slip roll at `$E382` (clear luck flags, roll `$70`
  against thresholds `$E397`, set one of `$71AD`-`$71B1` = flags
  $AD JINX ... $B1 CHARM). Hook: if the cheat flag is set, set CHARM. It
  needs an unused flag (check that the script never uses it, and what a new
  game does to it). JINX/BAD slips lead to the shrine priest's ritual
  (2A5, Beg x5, `cmdE7` luck +1); with the cheat that never happens. Note:
  `cmdE7` at CHARM overflows (`$E8E6`: clears every luck flag, so the grade is blank
  and Misako refuses); unreachable now, so guard it if that ever changes.
- **Flatter (hints):** stage 1 shows one placeholder hint to prove the
  flow. Stage 2: one hint per story milestone, chosen by a firstclear
  chain on progress flags; the same hint until the state changes (no
  "ask again for more"); some hints may mix vague and specific guidance.
  Only seen if the player chooses Flatter.
  - **Built (stage 2, 2026-11-01):** 39 hints from Stephen's walkthrough
    notes, reviewed over three drafts (`docs/caretaker-hints.md`;
    his style: plain steps in the caretaker's voice, one tier, steps that
    must run without a break in one hint, Gen kept a surprise). Text and
    opening flags in `tools/caretaker/hints.py` (one box per paragraph,
    wrapped and size-checked there). Flatter = "Ooh, such kind
    words.[page]" + `[firstset]` over the opening flags, latest first,
    default H01; so flags the game clears again (07, 4E, 7E) are harmless.
    Steps with no lasting flag (begging the rival, the car stakeout,
    handing over the bomb) share a hint with the next step. Hint IDs
    `$3DE`-`$405`; `$3FF` is left empty, since its low byte `$FF` inside the
    chain's arguments would end the message. The text now runs into PRG
    bank 12 (`insert.TEXT_BANKS` = 8, 9, 10, 12; 11 is daygoal's code); the
    lookup's fourth bank entry pushed the verb-list select into the
    lookup's own `$40` bytes (it overflowed into the caretaker code at
    `$FD50`). Tested in Nestopia: each of the 39 flag states shows its own
    hint, H06 pages through all six boxes back to the menu, 30 Flatter
    rounds then Leave work; Mesen: H34 (`$400`, bank 12).
- **Agreed wording (2026-10-23; boxes are 4 lines, max 25, last before a
  wait max 23).** Shrine odd jobs are plausible: local parishioners
  (ujiko) do upkeep as favours; only major work needs shrine carpenters.
  - Beg, first time (5 boxes): "Got yourselves into a bit / of bother,
    lads? Well, I / know people. Comes with / my age, that does." |
    "Now, this isn't how / things are meant to be. / It's an easier road
    than / lads like you deserve." | "First, I can see to it / you always
    draw the very / best fortune slip at the / shrine." | "You'll have to
    promise / to use it for good deeds, / mind. Once it's done, / there's
    no going back." | "I also hear things on the / grapevine. Flatter me a
    / bit, and I'll give you / the latest lowdown."
  - (Beg again: removed 2026-10-31; Beg leaves the menu once used.)
  - Promise: "I trust you, lads. It's / done. The priest owes me / for
    all the odd jobs I've / done round the shrine."
  - Promise again: "Your fortune's already / sorted, lads. A promise / is
    a promise."
  - Flatter: "Ooh, such kind words." (Stephen; not "you charmers", which echoes Risa's 086) + hint. Stage 1 placeholder: "You're only
    just starting / out. Have a wander round / and talk to folk."
- **Built (stage 1, 2026-10-23)** in `tools/additions.py`: messages
  $3CD-$3DA, now $3CD-$3D6 (CHOOSER = `[ifflag-call 0b]` picks menu $09 or $0A; each
  answer just ends, and the call loops back to CHOOSER, so the menu
  switches right after Beg). **Engine rule (crash found by Stephen,
  2026-10-23):** `[menu]` (`$DDB4`) runs the chosen target as a nested
  call (`JSR $EDA3`); a target that ends with a goto back to a menu
  leaves that call frame on the 6502 stack, so a loop overflows it after
  a few dozen choices (Leave then crashed). Loops must return: use
  `*-call` + targets that end. Fixed build: SP 163 at the menu before and
  after a full Ask (Mesen); 40 Flatter rounds then Leave work (the old
  build crashed during them). Talk = $3C4 (NERVE pages + "Right, that's
  your lot. Now clear off." + sign-off 0/1: gutters, boiler); Ask = $3D0
  (ends at ASK_SIGNOFF, now $3D6 → sign-off 2/3: leaky tap, tea; picked by frame bit 0 in
  the `$DBEE` hook), so one visit never repeats a sign-off. Flags $0B (begged)
  and $0C (cheat) live in `$7100` page, which save/load copies whole
  (`$E8FC`, `$E91D`); no code clears flags in bulk. Menu rows $09/$0A
  patched in the menu table. Cheat: `$E382` JSR → helper at `$FFB0` (16
  bytes; caretaker code must end before it). Tested in Nestopia and Mesen:
  every menu path, and 6 slip rolls without (mixed) / with (all CHARM)
  the cheat. Not yet tested: a real save and reload.
- Luck checks in the script (for reference): fortune slip 2A4, Risa
  coffee 2C7 (JINX refuses), Misako coffee 2C4 (needs GOOD/CHARM), Tomezo
  trick shot 2B9 and pachinko parlour 2BB (JINX/BAD fail).

### Day goal (agreed with Stephen 2026-10-31; built the same day)
Ending facts (fixed bank of the original): `$71C8` = day counter, one
byte, 0 at a new game, +1 at midnight (`$C435`) and on the new-day
routines after Sleep / overnight stakeout (`$C3CE`, `$C3FD`); no cap,
wraps 255 -> 0 (harmless; nothing else reads it). `$71B5` = hero
(0 Hiroshi, 1 Toru; also readable as flag $B5). The ending (`$E745`
table `09 08`, read at `$E74E` and `$EE6C`) plays the quicker version
if day < 9 (Hiroshi) / < 8 (Toru), else the slower one: two different
messages. Don't spoil the content to Stephen.
Agreed design:
- Caretaker menus: before Beg Talk / Ask / **Coffee** / Beg / Leave;
  after Beg Talk / Ask / **Coffee** / Promise / Flatter / Leave (Beg
  dropped once used). Coffee verb = $09.
- Coffee text (branch on flag $B5; name via `[cmdE1]`):
  "Coffee? I'll stick to my / own tea, lads. But since / you offered,
  here's a tip: / don't waste any time.[page] [Toru], as it's you, sort /
  things out within 8 days / and you'll get the / happiest ending.[page]
  Press Select in a chat / to see how you're doing." (9 days for
  Hiroshi; last line names whichever button is used.)
- Display: in a scene, the button toggles the panel's LUCK label (row 9)
  and grade (row 11, plus row 13) with: `GOAL` / `DAY3/8` / `14:05`
  (shown day = counter + 1; 24-hour clock from `$71C6`:`$71C5`). Once
  past the target: `GOAL` / `DAY12` / `14:05` (no "/8"; up to `DAY256`
  fits 6 columns). Colours: all black while the goal is reachable; once
  it is missed GOAL stays black and the DAY and time lines turn pink with
  black shadow (the grade / pip colour).
To research first: whether Select or B is free in scenes (joypad byte
`$17`/`$82`: A $80, B $40, Select $20, Start $10; read at `$C1E0`);
how the panel is redrawn (rows 9/11/13, `$EB6C` grade print); glyph
tile budget for digits, "/", ":" and letters in two colours (font
banks 30/31, `$60`-`$9E` minus grade/label use); fixed-bank space (43
bytes before `$FFB0`; banks 11-13 unused for code).
Research (2026-10-31):
- Buttons: `$82` = held (A $80, B $40, Select $20, Start $10, U/D/L/R
  $08/$04/$02/$01). The scene verb menu loop (`$EA15`-`$EA6B`) only
  acts on A and the D-pad; B and Select do nothing there. Hook: the
  loop's frame wait `JSR $EC22` at `$EA4A` -> trampoline (edge-detect
  Select with a saved previous state).
- Screen writes: text goes into the NMI buffer `$02C4` as (PPU hi, PPU
  lo, tile) triplets, `$64` = bytes used; `$EC16` flushes (`$1C` = `$64`,
  waits a frame). The grade print (`$EB6C`) sets the cursor `$4F/$50` =
  `$2162`, instant mode `$20`=1 and runs message `$37A+luck`. Our code
  can write triplets straight into the buffer (no message engine, so
  command-code tile numbers don't matter).
- Panel layout (PRG bank 0, row 5 at `$AEAB`, 32 per row): LUCK row 9,
  grade row 11 (cols 2-7 free; col 8 is the verb box border), row 12
  blank, row 13 col 6+ is the picture frame. So three lines must use
  rows 9/11/12 or 9/10/11 (mock-ups shown to Stephen).
- `$EB6C` (grade reprint, e.g. after a fortune slip) must undo the
  toggle first (LUCK label back, extra row blanked, state cleared): hook
  its `JSR $EB97`.
- Free RAM: SRAM page `$76xx` is never referenced by the original code
  and empty in saves.
- Tiles: label set `$8E`-`$9E` (minus `$9D`) has 8 free; grade set
  `$60`-`$8D` has 31 free. Needed: black G O A D Y 0-9 / : (17) and
  pink Y 0-9 / : (13; D, A already pink). Fits. Font has all glyphs.
- Code: the routine is in spare PRG bank 11 ($8000, ~600 bytes);
  trampolines (30 bytes) in the free run `$FCDE`-`$FCFF` after
  carpark's helper; bank switch via `$C049`.
Built (2026-10-31, `tools/daygoal.py`, called last in `insert.py`):
- Layout A (Stephen): GOAL row 9, day row 11, time row 12; full "DAY".
  Select only (edge-detected; B untouched). Toggle state `$7600`, last
  Select `$7601`, scratch `$7602`-`$760D`.
- The `$EB6C` hook puts LUCK back whenever the grade is reprinted, so a
  new scene always opens with LUCK (tested: toggle, Leave, next scene).
- Clock: `$71C5` is ticks (56 an hour), shown as minutes via a table
  (t x 60 / 56).
- Caretaker (additions.py): COFFEE `$3DB` (ifflag $B5) -> `$3DC`
  Hiroshi "9 days" / `$3DD` Toru "8 days". Wording: "Coffee? I'll stick
  to my / own tea, lads. But since / you offered, here's a / tip: don't
  waste time.[page] [hero], as it's you, / sort things out within / N
  days and you'll get / the happiest ending.[page] Press Select in a chat
  / to see how you're doing / for time." ("here's a tip: don't waste any time"
  trimmed to fit the 23-character page line.) Beg leaves the menu once
  used, so its repeat answers ("Still thinking, lads?", "You've had your
  favours") were removed and the later addition IDs moved down by 4
  (Stephen, 2026-10-31).
- Tested in Nestopia (save 9 late case DAY15 pink; Toru DAY3/8 and
  DAY8/8, Hiroshi DAY9/9 black; Hiroshi DAY10, DAY100, DAY256 pink; the
  caretaker menus, Coffee for both heroes) and in Mesen (toggle on/off
  in the caretaker's room). No picture corruption from row 12.

### Corridor variants (built 2026-10-25, `tools/corridorpics.py`)
- Picture `$19` (corridor, green door) was every floor of both 3-storey
  buildings: the Nishiyama Building in town (door → `2FC`; 1F `2FD`, 2F
  `2E4`, 3F `2FE`, gym on 4F `300`) and the block of flats in area 0
  (door → `361`; 1F `361`, 2F `362`, 3F `360` → `363`/`364`; the Shingo
  rescue `23F` also uses `$19`).
- New pictures `$2A`-`$2F` (Stephen chose the art from mock-ups):
  Nishiyama 1F violet / 2F teal / 3F wooden door, 3F a fire extinguisher;
  flats: a nameplate high on every door (Search on 3F, `1DA`: "the
  nameplate on this door says Tsuji!"), 1F navy door + potted plant on
  the floor, 2F dark red door + closed red umbrella (about a third of the
  door's height), 3F the original door (`$2F`, used by `360` and the
  Shingo rescue `23F`). `corridorpics.retarget()` swaps `cmdF0` in those
  scenes at build time. (2026-10-26: nameplates moved from the Nishiyama
  doors to the flats, umbrella enlarged.)
- Colour: palette 3 of a picture is the status panel's (changing it
  turned the whole backdrop red), so the extinguisher / plant / umbrella
  take their colour from the window's palette 2, and on those three
  floors the window glass is drawn in the greys.
- Tiles: CHR bank 10 had 13 free after the store variants; ten tiles
  were stored twice, so the original bank-10 pictures now point at one
  copy (same pixels, checked) — 23 free. The plant and umbrella are
  sized to the 8-px grid to fit. Fixed bank: 43 bytes left before
  `$FFB0`.
- Checked: all original pictures render identically; the nine new
  pictures' tiles match their art; walked 1F→3F→1F (Nishiyama) and
  1F→3F (flats), and the Shingo scene, in Nestopia and Mesen.

### Car park cars (requested 2026-10-24; built 2026-10-24, `tools/carpark.py`)
- **Built:** both cars share one 32x48 design (22 tiles in CHR bank 1's
  25 free) and differ only by map palette: car 1 = palette 2 (red-brown /
  brown / dark blue), car 2 = palette 0 (charcoal / brown / dark blue);
  Stephen chose this over separate designs (42 tiles, don't fit). Map
  grid is $18 x $2C blocks shared by areas 0-2 (town rows $C-$1B; count
  block usage only there). Car 1: block $2D edited, car squares solid
  (a door only fires when you step onto it), and the 3 squares beside it
  (x $45) are new door metatiles + door entries → scene 2E8 (after
  Leave you stand beside the car). Triggering from above was considered
  and dropped (Stephen, 2026-10-24): the aisle above is a through route, a
  walkable car top leaves the party on the car, and bump-to-trigger needs
  new collision code; not worth it. Car 2: block $1C = $2C + car (solid),
  written over ($10,$17) by a hook at `$CAA0` (helper at `$FCC0`, next
  to the game's own flag-$B2 map patch) when flag $7B is set in area 1;
  the map is re-copied after every scene, so it appears/disappears at
  once. Tested in Nestopia (all 3 times of day, triggers, solidity, flag
  set inside a scene) and Mesen (map + trigger).
- Original request notes:
Stephen: walking into the car scenes feels like bumping into a building
or thin air. Draw the cars on the town map, in the map's top-down style,
coloured like each car's scene picture, with the map's morning / evening
/ night palettes. Mock-ups first; Stephen picks.
- Both are the same car park (white bays, cobbled bank and water below).
  Stephen's Mesen save states: **8** (just before car 1), **9** (before
  Teru arrives), **10** (Teru there, party disguised as plant + signs).
- **Car 1 = door** entry 21 in the door table: area 1, metatile
  ($47, $5E) → scene 2E8 (picture $11, the red car; menu by flags
  $2A/$2C/$2E). The trigger is just right of the bottom-right bay, against
  the building side. Draw a car in the bottom-right bay as background
  metatiles (map edit, like the caretaker door). Always available, so a
  permanent car fits; confirm nothing removes it. Check: free tiles in
  the map CHR bank, tiles not shared with other spots, no walker routes.
- **Car 2 = invisible map character**, scene 2F3 (picture $12: "Teru's
  getting in that car" → 210 "It's the black Skyline!"). Town character
  list (bank 6 `$A312` table) area 6 slot 29, time mask ME, gate byte $0D
  → `$716E+$0D` = flag $7B (set by the Teru Sneak 388, cleared by 210 and
  0B1). Teru stands at the top-left bay; put the car in the bay just
  south of him so it doesn't overlap. Do it as a sprite tied to the same
  flag so it appears/disappears with the scene; needs ~8 sprite tiles
  (32x16), sprite palette per time of day, and a look at how that slot's
  sprite/movement is defined (probably stationary). Mind the 8-sprites-
  per-line limit next to walkers. Check the door-table area numbering vs
  the character-table area index (1 vs 6) before assuming one map.

### Department store variants (planned 2026-10-18)
Stephen (save state 7): every floor of the Kakui Department Store looks
the same, so it feels like a bug until you work it out.
- **Script map (msg_280):**
  - annexe ground floor `27F`: picture `$06` (shuttered; the store is
    改装中, being renovated);
  - annexe 2F `281`, 3F `282`, 4F `283`/`285`: all picture `$07` (shop
    counter). Search gives `1E5`-`1E7`;
  - main building 4F `286` (via Leave once flag `0d` is set): also `$07`;
  - annexe roof `287` and main building roof (`371` → `288`-`28D`, where
    the Shingo trail continues): both `$08`.
- **Terms checked:** べっかん 別館 = annexe, ほんかん 本館 = main building,
  わたりろうか = covered walkway. Japanese floors count like the US:
  1階 / 1F = ground floor, 屋上 = roof.
- **Proposal (pending Stephen):** no floor numbers in the art (Search
  tells you).
  - 2F: keep `$07`.
  - 3F: `$07` with different goods and colours.
  - Annexe 4F: renovation look (dust sheets, boxes, ladder).
  - Main 4F: clearly different, a brighter clothes floor.
  - Main roof: `$08` with a different skyline, plus a water tank or
    rooftop kiddie ride.
- **How:**
  - pictures in bank 10 (54 free tiles), reusing its shop and roof tiles;
  - generalise the caretaker's picture hooks (`tools/caretaker/build.py`,
    one picture `$25`) to a table of new pictures (CHR bank, layout in
    PRG bank 14, palette record);
  - change `cmdF0` in `282`/`283`/`285`/`286`/`371` to the new numbers;
  - mock-ups first, then test in both emulators.
- **Decided (Stephen):** keep the Japanese floor numbers. Build the five
  ideas, changed as below.
- **Built (2026-10-18):** `tools/storepics.py` (art, built on the
  original pictures' pixels) and `tools/pictures.py` (read and render any
  picture).
  - **New pictures:**
    - `$26` annexe 3F: the **furniture floor**. Take there says "There's
      only wardrobes here" (`193`), so two wardrobes replace the shelves.
      Dark teal tint.
    - `$27` annexe 4F: renovation (dust sheet over the counter and till,
      ladder against the pillar, boxes).
    - `$28` main building 4F: lights on, wooden canopy, clothes rail.
      Warmer in the evening, dimmer at night.
    - `$29` annexe roof: skyline halves swapped and the box removed. The
      main roof keeps `$08`, because Watch hides behind the box there.
      Stephen dropped the planned kiddie ride.
    - Annexe floors stay the same at every time of day, like the
      original unlit `$07`. The roof uses `$08`'s three time sets.
  - **Tiles:** 41 new tiles in bank 10's 54 free slots. Tiles any bank-10
    picture already uses are shared, so detail is drawn on the 8×8 grid.
  - **Script:** `storepics.retarget()` swaps the `cmdF0` numbers in
    `282`, `283`, `285`, `286` and `287` at build time. The script files
    keep the Japanese-matching numbers, so encheck stays clean.
  - **Hooks:** `tools/caretaker/build.py` hooks are now table-driven for
    pictures `$25`+. The fixed-bank tables hold the CHR bank and the
    layout and palette addresses; layouts and palette records live in
    PRG bank 14 (from `$8400`). The palette hook switches to bank 14
    around `$D2EB`. Originals only use palette records `$00`-`$2A`.
  - **Checks:**
    - all 37 original pictures are byte-identical to the pre-caretaker
      build;
    - walked 2F → 3F → 4F → roof, and 4F → Leave → main 4F → main roof,
      in Nestopia;
    - the four new pictures checked in Mesen, and at all three times.
