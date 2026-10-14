"""Title-screen menu translation (stage 7).

The title nametable is stored raw in PRG bank 1 at $AAC0 (32x30 tiles +
attributes) and drawn with CHR bank 12. The menu (rows 17-22) used kana
tiles found nowhere else on the title; it is rewritten here using the
Latin capitals already in bank 12 for the copyright lines, plus an H drawn
in the same three-band colour style into a freed menu-kana tile.
"""

NAMETABLE = (1, 0xAAC0)          # PRG bank, CPU address
CHR_BANK = 12
MENU_ROWS = range(17, 23)
MENU_COL = 11

# Letters available in CHR bank 12 (from "DATA EAST CORP." / "YOUNG
# MAGAZINE" and an unused K), plus new ones drawn below.
LETTERS = {
    'A': 0xB7, 'C': 0xBD, 'D': 0xB6, 'E': 0xB9, 'G': 0x9D, 'I': 0xA4,
    'K': 0x6F, 'M': 0x7F, 'N': 0xA9, 'O': 0xBE, 'P': 0xB2, 'R': 0xBF,
    'S': 0xBC, 'T': 0xB8, 'U': 0xA8, 'Y': 0x9F, 'Z': 0xA3, ' ': 0x00,
}

# New glyphs: digit = colour index (rows 0-2 use 1, 3-4 use 2, 5-7 use 3,
# matching the existing title capitals). Stored in freed menu-kana tiles.
NEW_TILES = {
    'H': (0x27, [
        '11...11.',
        '11...11.',
        '11...11.',
        '2222222.',
        '22...22.',
        '33...33.',
        '33...33.',
        '33...33.',
    ]),
}

MENU = {18: 'TORU NAKAMA', 20: 'HIROSHI KATO', 22: 'CONTINUE'}


def tile_bytes(rows):
    lo = bytes(sum((int(r[x]) & 1) << (7 - x) for x in range(8))
               for r in (row.replace('.', '0') for row in rows))
    hi = bytes(sum((int(r[x]) >> 1) << (7 - x) for x in range(8))
               for r in (row.replace('.', '0') for row in rows))
    return lo + hi


def apply(prg, chr_, bank_size=0x4000):
    """Patch PRG (bytearray, any size >= bank 1) and CHR in place."""
    letters = dict(LETTERS)
    for ch, (tile, rows) in NEW_TILES.items():
        o = CHR_BANK * 0x1000 + tile * 16
        chr_[o:o + 16] = tile_bytes(rows)
        letters[ch] = tile
    bank, addr = NAMETABLE
    base = bank * bank_size + addr - 0x8000
    for row in MENU_ROWS:                     # clear kana and dakuten rows
        o = base + row * 32
        prg[o:o + 32] = bytes(32)
    for row, text in MENU.items():
        o = base + row * 32 + MENU_COL
        assert MENU_COL + len(text) <= 30, text
        prg[o:o + len(text)] = bytes(letters[c] for c in text)
    # The English lines are wider than the kana ones, so give every 2x2
    # attribute quadrant under the menu the palette of the first letter.
    attr = base + 960
    quad = lambda r, c: (attr + (r // 4) * 8 + c // 4, ((r // 2) % 2) * 4 + ((c // 2) % 2) * 2)
    o, sh = quad(min(MENU), MENU_COL + 1)
    pal = (prg[o] >> sh) & 3
    for r in range(min(MENU), max(MENU) + 2, 2):
        for c in range(MENU_COL - 1, MENU_COL + max(map(len, MENU.values())) + 1, 2):
            o, sh = quad(r, c)
            prg[o] = (prg[o] & ~(3 << sh) & 0xFF) | (pal << sh)
