# Be-Bop High School (J) — English translation plan

Work is split into stages sized for one sitting each (roughly an hour of agent
time). Start each session with: "Continue the Be-Bop translation — next stage
in PLAN.md". Update the **Status** and **Findings** sections at the end of
each session so the next one doesn't re-derive anything.

## Status

- [x] **Stage 0 — Tooling check** (2026-10-10)
- [ ] Stage 1 — Static ROM survey
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

### Tooling notes (mesen-for-ai)
- Execute breakpoints use `access: "exec"` (not `"execute"`); also
  `read` / `write`. Use `memoryType: "nesMemory"`, `cpuType: "nes"`.
- Verified: an exec breakpoint at RESET fires during `run.step_frames` with
  `reset: true` (cycle 7, opcode $78 SEI). The step **stops at the hit**
  (returned at frame 0, not frame 1), so step again to continue.
- `video.export_frame` writes PPM; convert with PIL to view.
