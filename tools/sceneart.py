"""English captions inside scene pictures (stage 7e).

Policy (agreed with Stephen): Japanese painted into scene art stays; where
it matters for play, add a small English caption inside the same picture.

Scene pictures are loaded by $EC7A: CHR bank = $ED2E[pic] (fixed bank),
tile layout = PRG bank 1 at $8000 + $ED53[pic] * $130 (20x14 tiles, then
24 attribute bytes). A caption is a one-row plate written into the
picture's layout, drawn with spare tiles of its CHR bank -- tiles that no
picture using that bank references. Nothing is drawn outside the picture,
so captions can never clash with dialogue boxes.
"""
import font

LOADER_CHR = 0xED2E           # fixed-bank table: picture -> CHR bank
LOADER_IDX = 0xED53           # fixed-bank table: picture -> layout index
PICTURES = 37
W, H = 20, 14

# picture: (row, first column, text, style). Styles:
#   ('plate', ink, plate)    letters on a solid plate, one blank tile each end
#   ('overlay', ink, shadow) letters drawn over the original art tiles, with
#                            an optional 1 px drop shadow (None = no shadow)
CAPTIONS = {
    0x1D: (6, 6, '"CLOSED"', ('overlay', 3, None)),   # 閉店 on the shutter; plain white reads best over these stripes
}
# The frame drawn round every picture (outside its 20x14 layout) uses
# these tile numbers in the scene bank too: left edge, right edge, bottom
# row, and the blank surround. Never reuse them.
FRAME_TILES = {0x02, 0x07, 0x2A, 0xFF}


def _tables(prg):
    fixed = len(prg) // 0x4000 - 1          # 15 once the PRG is expanded
    f = lambda a: fixed * 0x4000 + a - 0xC000
    return (prg[f(LOADER_CHR):f(LOADER_CHR) + PICTURES],
            prg[f(LOADER_IDX):f(LOADER_IDX) + PICTURES])


def _layout_offset(idx, n):
    return 1 * 0x4000 + idx[n] * 0x130


def _pixels(chr_, bank, tile):
    o = bank * 0x1000 + tile * 16
    return [[((chr_[o + y] >> (7 - x)) & 1) | (((chr_[o + y + 8] >> (7 - x)) & 1) << 1)
             for x in range(8)] for y in range(8)]


def _tile(rows, style, base):
    """Glyph rows (drawn one pixel lower) -> CHR bytes in the given style;
    base = 8x8 colour indices of the original tile (overlay style)."""
    mode, ink, other = style
    rows = ['.' * 8] + [r.ljust(8, '.') for r in rows[:7]]
    if mode == 'plate':
        pix = [[ink if r[x] == '#' else other for x in range(8)] for r in rows]
    else:
        pix = [row[:] for row in base]
        for y in range(8):
            for x in range(8):
                if rows[y][x] == '#':
                    pix[y][x] = ink
                elif (other is not None and y and x and rows[y - 1][x - 1] == '#'):
                    pix[y][x] = other
    lo = bytes(sum((p[x] & 1) << (7 - x) for x in range(8)) for p in pix)
    hi = bytes(sum((p[x] >> 1) << (7 - x) for x in range(8)) for p in pix)
    return lo + hi


def apply(prg, chr_):
    chrtab, idx = _tables(prg)
    glyphs = {ch: rows for ch, (_, rows) in font.build().items()}
    blank = ['.' * 8] * 8
    for pic, (row, col, text, style) in CAPTIONS.items():
        bank = chrtab[pic]
        assert list(idx).count(idx[pic]) == 1, 'layout shared with another picture'
        used = set()
        for n in range(PICTURES):
            if chrtab[n] == bank:
                o = _layout_offset(idx, n)
                used |= set(prg[o:o + W * H])
        free = [t for t in range(256) if t not in used and t not in FRAME_TILES]
        cells = (' ' + text + ' ') if style[0] == 'plate' else text
        assert col + len(cells) <= W
        o = _layout_offset(idx, pic) + row * W + col
        made = {}
        for i, ch in enumerate(cells):
            under = prg[o + i]                   # original art tile here
            key = (ch, under if style[0] == 'overlay' else None)
            if key not in made:
                t = free.pop(0)
                made[key] = t
                data = _tile(glyphs.get(ch, blank), style, _pixels(chr_, bank, under))
                chr_[bank * 0x1000 + t * 16:bank * 0x1000 + t * 16 + 16] = data
            prg[o + i] = made[key]
