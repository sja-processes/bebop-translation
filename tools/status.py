"""Status panel (left of the verb menu) translation (stage 7c).

The panel labels and the luck grade use white-on-black glyph tiles in the
font CHR banks 30/31 (ink colour 0 on colour 3, like the old inverse kana
at $8E-$9F). Labels are tiles in the status-screen layout in PRG bank 0;
the luck grade is message $37A + level, printed by $EB6C at PPU $2162
(row 11, column 2) with nothing cleared first, so every grade is padded
to the same width (the verb box's corner tile is at column 8).
"""
import font

FONT_CHR_BANKS = (30, 31)
# Label letters: inverse kana $8E-$9E (only used by this panel). $9D is
# skipped: in a message it is the inverse-dakuten control code.
LABEL_TILES = [t for t in range(0x8E, 0x9F) if t != 0x9D]
# Grade letters (pink, like the filled gauge pips) + a blank: spare
# katakana slots, which are plain tile numbers in a message.
GRADE_TILES = list(range(0x60, 0x8E))

LABELS = {(0, 0xAEAB): 'NERVE', (0, 0xAF2B): 'LUCK'}   # PRG bank, CPU addr
LABEL_WIDTH = 6           # columns 2-7; column 8 is the verb box border
GRADE_FIRST_ID = 0x37A
GRADES = ['JINX', 'BAD', 'FAIR', 'GOOD', 'CHARM']       # worst -> best
GRADE_WIDTH = 5           # columns 2-6, the original grades' footprint
BLANK = 0xFF              # all colour 3 in the font banks (panel background)

# Panel palette (palette 3): 0 black, 1 white, 2 pink (pip fill), 3 light
# blue (background). Labels stay black as in the original; grades are
# pink with a black drop shadow so they read like the pips.
LABEL_STYLE = (0, None)   # (ink colour, shadow colour)
GRADE_STYLE = (2, 0)
BG = 3


def _tile(rows, style):
    """Font glyph rows -> CHR bytes in the given (ink, shadow) colours."""
    ink, shadow = style
    rows = [r.ljust(8, '.') for r in rows]
    pix = [[BG] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            if rows[y][x] == '#':
                pix[y][x] = ink
            elif shadow is not None and y and x and rows[y - 1][x - 1] == '#':
                pix[y][x] = shadow
    lo = bytes(sum((pix[y][x] & 1) << (7 - x) for x in range(8)) for y in range(8))
    hi = bytes(sum((pix[y][x] >> 1) << (7 - x) for x in range(8)) for y in range(8))
    return lo + hi


def _alloc(words, tiles, blank=False):
    letters = sorted(set(''.join(words)))
    need = len(letters) + blank
    assert need <= len(tiles), 'not enough status tiles'
    m = {ch: tiles[i] for i, ch in enumerate(letters)}
    if blank:
        m[' '] = tiles[len(letters)]
    return m


def label_map():
    return _alloc(LABELS.values(), LABEL_TILES)


def grade_map():
    return _alloc(GRADES, GRADE_TILES, blank=True)


def grade_texts():
    """-> {message id: raw-tile text for script.encode}"""
    m = grade_map()
    out = {}
    for i, word in enumerate(GRADES):
        assert len(word) <= GRADE_WIDTH, word
        out[GRADE_FIRST_ID + i] = ''.join('<%02X>' % m[c] for c in word.ljust(GRADE_WIDTH))
    return out


def apply(prg, chr_, bank_size=0x4000):
    glyphs = {ch: rows for ch, (_, rows) in font.build().items()}
    for m, style in ((label_map(), LABEL_STYLE), (grade_map(), GRADE_STYLE)):
        for ch, tile in m.items():
            data = _tile(glyphs.get(ch, ['.' * 8] * 8), style)
            for cb in FONT_CHR_BANKS:
                o = cb * 0x1000 + tile * 16
                chr_[o:o + 16] = data
    m = label_map()
    for (bank, addr), word in LABELS.items():
        assert len(word) <= LABEL_WIDTH, word
        o = bank * bank_size + addr - 0x8000
        prg[o:o + LABEL_WIDTH] = bytes(m[c] if c != ' ' else BLANK
                                       for c in word.ljust(LABEL_WIDTH))
