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
- [ ] Stage 5 — Translation (several sessions, mostly you + Claude chat) — msg_000 to msg_180 done 2026-10-10
- [ ] Stage 6 — Insertion tooling
- [ ] Stage 7 — Graphics (title logo kanji, menus)
- [ ] Stage 8 — Playtest & polish (several sessions)

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

**6. Insertion.** Inserter that re-encodes English, repoints, and emits an
IPS/BPS patch. A likely need: an 8×8 Latin font in CHR and possibly DTE/
word compression or text relocation if space runs out (MMC1 128 KB PRG can
be expanded to 256 KB if necessary).

**7. Graphics.** Title kanji subtitle, any graphic menus/signs.

**8. Playtest.** Scripted playthroughs in Mesen, checking for overflowing
boxes, broken control codes and crashes.

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
- Done: msg_000-msg_180 (IDs $000-$1FF).

### Tools
- `tools/dis6502.py BANK ADDR [N]` — quick disassembler over the ROM.
- `tools/bebop.tbl` — script table (see above).
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
