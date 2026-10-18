"""Kakui Department Store picture variants (PLAN.md "Department store
variants"): every floor used the same unlit shop picture ($07) and both
roofs the same roof ($08), which read like a bug.

New pictures (all CHR bank 10, the bank $07 and $08 use):
  $26 annexe 3F   - $07 as the furniture floor (Take: "only wardrobes
                    here"): wardrobes instead of shelves, another tint
  $27 annexe 4F   - $07 under renovation: dust sheets, stepladder, boxes
  $28 main 4F     - $07 with the lights on and a rack of clothes
                    (warmer in the evening, dimmer at night)
  $29 annexe roof - $08 with the skyline rearranged and the box
                    removed (the main roof keeps $08: Watch hides
                    behind the box there)
No floor numbers in the art: Search tells you where you are.

Each picture starts from the original's pixels; edits are painted as
colour indices (0-3) and the result is cut back into tiles. A tile that
matches one the bank's pictures already use is shared; new tiles take
bank 10's free slots (tiles no picture references).

    python3 tools/storepics.py OUTDIR    mock-ups (morning / evening / night)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pictures  # noqa: E402

CHR_BANK = 10
W, H = 160, 112


class Canvas:
    """A picture as pixels (colour indices) + 16x16 block palettes."""

    def __init__(self, pic):
        self.blocks = [list(r) for r in pic.blocks]
        self.palsets = [list(p) for p in pic.palsets]
        self.px = [[pic.pixel_index(pic.tiles[(y // 8) * 20 + x // 8], x % 8, y % 8)
                    for x in range(W)] for y in range(H)]

    def set(self, x, y, v):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = v

    def rect(self, x0, y0, x1, y1, v):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, v)

    def patch(self, x0, y0, rows):
        """rows of '0'-'3' (colour index) / ' ' (leave)."""
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c != ' ':
                    self.set(x0 + dx, y0 + dy, int(c))

    def copy(self, src, sx, sy, w, h, dx, dy):
        """Copy a pixel rectangle (from this or another canvas)."""
        part = [[src.px[sy + y][sx + x] for x in range(w)] for y in range(h)]
        for y in range(h):
            for x in range(w):
                self.set(dx + x, dy + y, part[y][x])

    def palette(self, slot, colours):
        """Set palette `slot` (0-3) to 3 colours for all times, or to a
        list of three 3-tuples (morning, evening, night)."""
        sets = colours if isinstance(colours[0], (tuple, list)) else [colours] * 3
        for t in range(3):
            self.palsets[t][1 + slot * 3:4 + slot * 3] = list(sets[t])

    def block(self, bx0, by0, bx1, by1, slot):
        for by in range(by0, by1 + 1):
            for bx in range(bx0, bx1 + 1):
                self.blocks[by][bx] = slot

    def tile_patterns(self):
        return [tuple(self.px[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
                for ty in range(14) for tx in range(20)]


def pattern_of(chr_data, t):
    lo = chr_data[t * 16:t * 16 + 8]
    hi = chr_data[t * 16 + 8:t * 16 + 16]
    return tuple(((lo[y] >> (7 - x)) & 1) | (((hi[y] >> (7 - x)) & 1) << 1)
                 for y in range(8) for x in range(8))


def chr_bytes(pat):
    lo = bytes(sum((pat[y * 8 + x] & 1) << (7 - x) for x in range(8)) for y in range(8))
    hi = bytes(sum((pat[y * 8 + x] >> 1) << (7 - x) for x in range(8)) for y in range(8))
    return lo + hi


# ---------------------------------------------------------------- variants

def annexe_3f(o7):
    """The furniture floor: Take here gets "There's only wardrobes here"
    (193), so two wardrobes stand where the 2F has dark shelves."""
    cv = Canvas(o7)
    cv.rect(0, 0, 47, 63, 0)
    cv.block(0, 0, 2, 0, 2)                  # block (2,0) was palette 3, unused
    for x0 in (0, 24):                       # two identical 3-tile wardrobes
        cv.rect(x0 + 1, 8, x0 + 22, 63, 2)   # body
        cv.rect(x0, 6, x0 + 23, 9, 2)        # cornice
        cv.rect(x0, 10, x0 + 23, 10, 0)
        cv.rect(x0 + 11, 12, x0 + 12, 59, 0)  # the doors' join
        cv.rect(x0 + 3, 12, x0 + 3, 59, 1); cv.rect(x0 + 20, 12, x0 + 20, 59, 1)
        cv.rect(x0 + 9, 32, x0 + 9, 39, 1); cv.rect(x0 + 14, 32, x0 + 14, 39, 1)  # handles
        cv.rect(x0 + 1, 60, x0 + 22, 61, 1)  # plinth
        cv.rect(x0 + 2, 62, x0 + 3, 63, 1); cv.rect(x0 + 20, 62, x0 + 21, 63, 1)  # feet
    # a different emergency-light tint from the 2F's blue: dark teal
    cv.palette(2, (0x0C, 0x1C, 0x1C))
    return cv


def annexe_4f(o7):
    """Drawn on the 8x8 grid so tiles repeat (bank 10 has 54 free)."""
    cv = Canvas(o7)
    # dust sheet over the counter (tiles 10-19 x 5-9) and the till: palette
    # 1 = the annexe blue plus a pale third colour for highlights
    cv.palette(1, (0x01, 0x11, 0x21))
    cv.block(5, 1, 9, 4, 1)
    cv.rect(80, 16, 159, 79, 0)

    def cloth(x, y, top):
        f = x % 16
        if y < top + 2:
            return 3
        return 1 if f == 0 else 3 if f == 1 else 2
    for x in range(80, 160):
        for y in range(40, 76):
            cv.set(x, y, cloth(x, y, 40))
        for y in range(76, 80):                         # hem, 8-px wave
            cv.set(x, y, 0 if (y - 76) > (2 if x % 8 < 4 else 0) else cloth(x, y, 40))
    # lump over the till (tiles 17-19 x 2-4)
    for x in range(136, 160):
        top = 18 if 140 <= x <= 155 else 24 if 138 <= x <= 157 else 32
        for y in range(top, 40):
            cv.set(x, y, cloth(x, y, top))
    # ladder leaning on the pillar (tiles 6-8), rungs every 8 px
    for y in range(24, 88):
        for x in (52, 53, 66, 67):
            cv.set(x, y, 2)
        if y % 8 == 4:
            cv.rect(54, y, 65, y, 2)
    # boxes on the floor, right: 2x2-tile boxes with a lit top row
    def box(tx, ty):
        x0, y0 = tx * 8, ty * 8
        cv.rect(x0, y0, x0 + 15, y0 + 15, 2)
        cv.rect(x0, y0, x0 + 15, y0 + 1, 3)
        cv.rect(x0 + 7, y0, x0 + 8, y0 + 4, 1)
        cv.rect(x0, y0 + 15, x0 + 15, y0 + 15, 0)
        cv.rect(x0 + 15, y0, x0 + 15, y0 + 15, 0)
    cv.block(7, 5, 9, 6, 1)
    box(16, 12); box(18, 12); box(17, 10)
    cv.rect(128, 80, 135, 95, cv.px[90][128])          # floor beside the top box
    return cv


def main_4f(o7):
    cv = Canvas(o7)
    # lights on: the same shop in greys, wood and colour
    # morning / evening (slightly warmer: whites to cream) / night (one
    # step dimmer)
    cv.palette(2, [(0x00, 0x10, 0x30), (0x00, 0x10, 0x37), (0x00, 0x10, 0x10)])
    cv.palette(1, [(0x07, 0x17, 0x27), (0x07, 0x17, 0x27), (0x07, 0x17, 0x17)])
    cv.palette(0, [(0x16, 0x12, 0x30), (0x16, 0x12, 0x37), (0x06, 0x02, 0x10)])
    # wooden canopy over the counter
    cv.block(5, 0, 9, 0, 1)
    # left: a rail of hanging clothes instead of the dark shelves, one
    # garment per 8-px column so tiles repeat
    cv.rect(0, 0, 47, 79, 0)
    cv.block(0, 0, 2, 4, 0)
    cv.rect(0, 8, 47, 9, 3)                      # rail
    colours = [1, 2, 3, 1, 3, 2]
    for k in range(6):
        x0 = k * 8 + 1
        c = colours[k]
        cv.set(x0 + 3, 10, 3); cv.set(x0 + 3, 11, 3)          # hanger hook
        cv.rect(x0, 12, x0 + 6, 12, 3)                        # hanger bar
        cv.rect(x0, 13, x0 + 6, 13 + (39 if k % 2 else 31), c)  # garment
    cv.rect(2, 64, 3, 79, 3); cv.rect(44, 64, 45, 79, 3)      # rack legs
    return cv


def annexe_roof(o8):
    cv = Canvas(o8)
    # skyline: swap the left and right halves of the buildings band
    left = Canvas.__new__(Canvas)
    left.px = [row[:] for row in cv.px]
    left_blocks = [r[:] for r in cv.blocks]
    for y in range(24, 64):
        for x in range(W):
            cv.px[y][x] = left.px[y][(x + 80) % W]
    for by in range(1, 4):
        for bx in range(10):
            cv.blocks[by][bx] = left_blocks[by][(bx + 5) % 10]
    # the box goes (the main roof keeps it: Watch hides behind it);
    # plain roof floor in its place, in the floor's palette
    cv.copy(cv, 0, 80, 64, 32, 96, 80)
    cv.block(6, 5, 9, 6, cv.blocks[5][0])
    return cv


# Which store scenes show which picture (msg_280; the script files keep
# the original numbers so encheck still matches them with the Japanese).
RETARGET = {
    0x282: (0x07, 0x26),     # annexe 3F
    0x283: (0x07, 0x27),     # annexe 4F
    0x285: (0x07, 0x27),     # annexe 4F (after learning of the walkway)
    0x286: (0x07, 0x28),     # main building 4F
    0x287: (0x08, 0x29),     # annexe roof
}


def retarget(msgs):
    """Swap [cmdF0 old] for [cmdF0 new] in the store scenes (dict id->text)."""
    for mid, (old, new) in RETARGET.items():
        tag = '[cmdF0 %02x]' % old
        assert msgs[mid].count(tag) == 1, (hex(mid), msgs[mid])
        msgs[mid] = msgs[mid].replace(tag, '[cmdF0 %02x]' % new)


VARIANTS = [(0x26, 'annexe 3F', 7, annexe_3f), (0x27, 'annexe 4F', 7, annexe_4f),
            (0x28, 'main 4F', 7, main_4f), (0x29, 'annexe roof', 8, annexe_roof)]


def build(data=None, used=None, free=None):
    """-> ([(pic, layout bytes, palette record)], {tile: chr bytes}).
    used = tiles of bank 10 pictures reference; free = slots to use."""
    data = data or pictures.rom()
    base = {n: pictures.Picture.original(n, data) for n in (7, 8)}
    chr_data = base[7].chr
    known = {}
    for t in sorted(used):
        known.setdefault(pattern_of(chr_data, t), t)
    free = list(free)
    new_tiles = {}
    out = []
    for pic, _, src, fn in VARIANTS:
        cv = fn(base[src])
        tiles = []
        for pat in cv.tile_patterns():
            if pat not in known:
                t = free.pop(0)
                known[pat] = t
                new_tiles[t] = chr_bytes(pat)
            tiles.append(known[pat])
        p = pictures.Picture(CHR_BANK, tiles, cv.blocks, cv.palsets, chr_data)
        out.append((pic, p.layout_bytes(), p.palette_record()))
    return out, new_tiles


def mockups(outdir):
    from PIL import Image
    data = pictures.rom()
    base = {n: pictures.Picture.original(n, data) for n in (7, 8)}
    rows = [('annexe 2F (as now)', base[7])]
    for pic, name, src, fn in VARIANTS:
        cv = fn(base[src])
        # render straight from pixels (tile allocation doesn't change the look)
        p = pictures.Picture(CHR_BANK, list(range(280)), cv.blocks, cv.palsets, bytes(4096))
        p.chr = bytearray(4096 * 2)
        pats = cv.tile_patterns()
        chr_data = bytearray()
        for pat in pats:
            chr_data += chr_bytes(pat)
        p.chr = chr_data
        p.tiles = list(range(280))
        rows.append((name, p))
    rows.insert(4, ('main roof (as now)', base[8]))
    sheet = Image.new('RGB', (3 * 168, len(rows) * 120), (255, 255, 255))
    for i, (name, p) in enumerate(rows):
        for t in range(3):
            sheet.paste(p.render(t), (t * 168, i * 120))
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), 0)
    sheet.save(os.path.join(outdir, 'store_variants.png'))


if __name__ == '__main__':
    mockups(sys.argv[1])
