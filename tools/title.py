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

# Author credit (was kana on row 27 with dakuten on row 26).
LETTERS['©'] = 0xA2
CREDIT_ROWS = range(26, 28)
CREDIT_CLEAR_COL = 6
# One line with the original blank row above it; the full given name
# would need two stacked rows that touch (this lettering is 8 px tall).
LETTERS['.'] = 0x88
LETTERS['/'] = 0x7D
CREDIT = {27: (6, '©K.KIUCHI/YOUNG MAGAZINE')}

# English subtitle under the kanji (rows 13-14, palette 0): one row of
# small italic script, ink colour 1 with a colour-2 drop shadow like the
# kanji. Rendered to a bitmap and cut into tiles placed in FREE_TILES.
SUBTITLE = 'Legend of High-School Paradise'
SUBTITLE_ROW = 15
SUBTITLE_CENTRE_X = 144          # centre of the kanji (columns 11-24)

# Tiles used only by the old kana menu / kana credit (checked: each kana
# sequence occurs once in PRG, in this nametable). $27 is now H.
FREE_TILES = [0x28, 0x39, 0x48, 0x49, 0x59, 0x67, 0x6A, 0x77, 0x78, 0x79,
              0x7A, 0x7B, 0x7C, 0xEE, 0xFE, 0x3E, 0x4E, 0x4F, 0x5E, 0x5F,
              0x6D, 0x6E, 0x68]          # $7D kept: it is the '/' glyph

# Original upright glyphs, 8 rows (baseline after row 5, descenders 6-7);
# render_subtitle() slants them into italics.
SCRIPT = {
    'L': ['#....', '#....', '#....', '#....', '#....', '#####', '.....', '.....'],
    'H': ['#...#', '#...#', '#####', '#...#', '#...#', '#...#', '.....', '.....'],
    'S': ['.###', '#...', '.##.', '...#', '...#', '###.', '....', '....'],
    'P': ['###.', '#..#', '#..#', '###.', '#...', '#...', '....', '....'],
    'a': ['....', '....', '.###', '#..#', '#..#', '.###', '....', '....'],
    'c': ['...', '...', '.##', '#..', '#..', '.##', '...', '...'],
    'd': ['...#', '...#', '.###', '#..#', '#..#', '.###', '....', '....'],
    'e': ['....', '....', '.##.', '####', '#...', '.###', '....', '....'],
    'f': ['..##', '.#..', '###.', '.#..', '.#..', '.#..', '....', '....'],
    'g': ['....', '....', '.###', '#..#', '#..#', '.###', '...#', '.##.'],
    'h': ['#...', '#...', '###.', '#..#', '#..#', '#..#', '....', '....'],
    'i': ['#', '.', '#', '#', '#', '#', '.', '.'],
    'l': ['#', '#', '#', '#', '#', '#', '.', '.'],
    'n': ['....', '....', '###.', '#..#', '#..#', '#..#', '....', '....'],
    'o': ['....', '....', '.##.', '#..#', '#..#', '.##.', '....', '....'],
    'r': ['...', '...', '#.#', '##.', '#..', '#..', '...', '...'],
    's': ['...', '...', '.##', '#..', '..#', '##.', '...', '...'],
    '-': ['...', '...', '...', '###', '...', '...', '...', '...'],
    ' ': ['..', '..', '..', '..', '..', '..', '..', '..'],
}


def render_subtitle(text):
    """-> list of 8 pixel rows (lists of colour indices)."""
    cols = []
    for ch in text:
        g = SCRIPT[ch]
        for x in range(len(g[0])):
            cols.append([g[y][x] == '#' for y in range(8)])
        cols.append([False] * 8)                       # 1px letter gap
    width = len(cols) + 3
    ink = [[False] * width for _ in range(8)]
    for x, col in enumerate(cols):
        for y in range(8):
            if col[y]:
                ink[y][x + (7 - y) // 3] = True        # italic shear
    out = [[0] * width for _ in range(8)]
    for y in range(8):
        for x in range(width):
            if ink[y][x]:
                out[y][x] = 1
            elif y and x and ink[y - 1][x - 1]:
                out[y][x] = 2                          # drop shadow
    return out


def subtitle_tiles():
    """-> (first column, [tile bitmaps or None for blank]) for row 15."""
    pix = render_subtitle(SUBTITLE)
    w = len(pix[0])
    x0 = SUBTITLE_CENTRE_X - w // 2
    col0, pad = x0 // 8, x0 % 8
    ncols = (pad + w + 7) // 8
    tiles = []
    for c in range(ncols):
        rows = []
        for y in range(8):
            rows.append(''.join(str(pix[y][x]) if 0 <= (x := c * 8 + i - pad) < w else '0'
                                for i in range(8)))
        tiles.append(None if all(r == '0' * 8 for r in rows) else rows)
    return col0, tiles


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
    for row in CREDIT_ROWS:                   # keep the DECO logo (cols 2-5)
        prg[base + row * 32 + CREDIT_CLEAR_COL:base + row * 32 + 32] = \
            bytes(32 - CREDIT_CLEAR_COL)
    for row, (col, text) in CREDIT.items():
        o = base + row * 32 + col
        prg[o:o + len(text)] = bytes(letters[c] for c in text)

    col0, tiles = subtitle_tiles()
    free, seen = list(FREE_TILES), {}
    o = base + SUBTITLE_ROW * 32 + col0
    for i, rows in enumerate(tiles):
        if rows is None:
            prg[o + i] = 0x00
            continue
        key = tuple(rows)
        if key not in seen:
            assert free, 'subtitle needs more free tiles'
            seen[key] = free.pop(0)
            t = CHR_BANK * 0x1000 + seen[key] * 16
            chr_[t:t + 16] = tile_bytes(rows)
        prg[o + i] = seen[key]

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
