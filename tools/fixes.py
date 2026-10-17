"""Fixes for timing bugs in the original game code (stage 8b).

Map tile uploads race the NMI. In three places the main code fills the
NMI's own upload queue and then calls the NMI's uploader directly:
  - $D121 / $D13D: JSR $D0C2 (set up a run: $60/$61 address, ($62)
    source, $1D length) then JSR $D207 (copy $1D bytes, clear $1D).
    If an NMI lands between the two calls it uploads the run and clears
    $1D, and $D207 then loops 256 times: ~8 rows of junk tiles across the
    map. Writes from main code can also land mid-frame.
  - $C86B: LDA $64 / STA $1C / JSR $D21F (the same, for the tile list).
Seen on Stephen's handheld (RetroArch lr-nestopia) after Leave, in the
Japanese ROM too; never in Mesen, whose timing happens to miss the window.

Fix: keep the original direct uploads, but hold the game's own "NMI may
work" flag $19 at 0 around each one (saving and restoring it). An NMI
that lands in the window then only counts the frame (it checks $19
first), so it can't clear the length or upload the same queue twice.
(A first attempt that instead waited for the NMI hung: $19 is not a
reliable "NMI enabled" flag, as the bank-switch helpers set it to 1
even while the screen is off.)
"""

BASE = 0xFD60                 # free fixed-bank space after our other code


def _code():
    hold = bytes([0xA5, 0x19, 0x48,       # LDA $19 / PHA
                  0xA9, 0x00, 0x85, 0x19])  # LDA #0 / STA $19
    release = bytes([0x68, 0x85, 0x19,    # PLA / STA $19
                     0x60])               # RTS
    run = hold + bytes([0x20, 0xC2, 0xD0,   # JSR $D0C2 (set up the run)
                        0x20, 0x07, 0xD2]) + release   # JSR $D207
    lst = hold + bytes([0xA5, 0x64, 0x85, 0x1C,       # LDA $64 / STA $1C
                        0x20, 0x1F, 0xD2]) + release  # JSR $D21F
    return run + lst, BASE, BASE + len(run)


CODE, SAFE_RUN, SAFE_LIST = _code()
NOP = 0xEA

# (CPU address, original bytes, new bytes)
PATCHES = [
    (BASE, bytes([0xFF]) * len(CODE), CODE),
    (0xD121, bytes.fromhex('20 C2 D0 20 07 D2'),
     bytes([0x20, SAFE_RUN & 0xFF, SAFE_RUN >> 8, NOP, NOP, NOP])),
    (0xD13D, bytes.fromhex('20 C2 D0 20 07 D2'),
     bytes([0x20, SAFE_RUN & 0xFF, SAFE_RUN >> 8, NOP, NOP, NOP])),
    (0xC86B, bytes.fromhex('A5 64 85 1C 20 1F D2'),
     bytes([0x20, SAFE_LIST & 0xFF, SAFE_LIST >> 8, NOP, NOP, NOP, NOP])),
]
