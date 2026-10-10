# Be-Bop High School (J) — English translation plan

Work is split into stages sized for one sitting each (roughly an hour of agent
time). Start each session with: "Continue the Be-Bop translation — next stage
in PLAN.md". Update the **Status** and **Findings** sections at the end of
each session so the next one doesn't re-derive anything.

## Status

- [x] **Stage 0 — Tooling check** (2026-10-10)
- [x] Stage 1 — Static ROM survey (2026-10-10)
- [ ] Stage 2 — Find the font & table file
- [ ] Stage 3 — Trace the text engine
- [ ] Stage 4 — Script dump
- [ ] Stage 5 — Translation (several sessions, mostly you + Claude chat)
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

**5. Translation.** Fill in English next to each line. This is mostly
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
- **Hypothesis:** the CDL showed bank 3 read *continuously* from `$8000`
  to just past that line (`$A41E`), so the engine may find message N by
  scanning terminators from the start of the bank rather than using a
  pointer table. Verify in stage 3 — it makes reinsertion much easier.
- Dialogue box (intro): text starts at nametable column 2, row 4.

### Tools
- `tools/dis6502.py BANK ADDR [N]` — quick disassembler over the ROM.

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
