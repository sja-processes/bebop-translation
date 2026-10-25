"""Corridor picture variants (Stephen, 2026-10-25): both three-storey
buildings used the same corridor picture ($19) on every floor.

- Nishiyama Building (town; Hokuto Gym on 4F, a business building): each
  floor gets an office nameplate high on the door, above the handle, and
  its own door colour; 3F also has a fire extinguisher.
    $2A 1F (2FD) violet door      $2B 2F (2E4) teal door
    $2C 3F (2FE) wooden door + extinguisher
- Block of flats (area 0): homely touches. 3F stays $19, because the
  Shingo scenes there (364, 23F) are a story point.
    $2D 1F (361) navy door + potted plant on the floor, right of the door
    $2E 2F (362) dark red door + closed red umbrella standing by the door
    (shoes would sit inside, in the genkan, not in a shared corridor)
1F of the two buildings differ as well. The door is palette 1 (a new set
per variant, by time of day). The extinguisher, plant and umbrella need
one more colour on the grey wall: palette 3 is the status panel's, so
on those floors the window's palette 2 becomes wall greys + that colour,
and the window glass is drawn in the greys instead (see _accent).

All in CHR bank 10, $19's bank, which the department store variants
(storepics) have nearly filled. Ten of its tiles are stored twice, so
the original bank-10 pictures are first pointed at one copy of each
(same pixels), freeing those slots.

    python3 tools/corridorpics.py OUTDIR    mock-ups (morning / evening / night)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pictures  # noqa: E402
from storepics import Canvas, chr_bytes, pattern_of  # noqa: E402

CHR_BANK = 10
BASE = 0x19
BANK = 0x4000
FIXED = 15


def _accent(cv, extra, blocks):
    """One extra colour on wall blocks. Palette 3 is the status panel's
    and palette 0 needs its white, so the window gives up palette 2: its
    glass is redrawn in the greys (dark glass, white glint), and palette
    2 becomes palette 0's two greys + `extra` (by time of day)."""
    if cv.blocks[0][0] == 2:
        for y in range(32):
            for x in range(16):
                v = cv.px[y][x]
                cv.px[y][x] = {2: 1}.get(v, v)
        cv.block(0, 0, 0, 1, 0)
    p0 = [cv.palsets[t][1:4] for t in range(3)]
    cv.palette(2, [(p0[t][0], p0[t][1], extra[t]) for t in range(3)])
    for bx, by in blocks:
        cv.block(bx, by, bx, by, 2)


def nameplate(cv):
    x0, y0, x1, y1 = 81, 9, 94, 14
    cv.rect(x0, y0, x1, y1, 2)
    cv.rect(x0, y0, x1, y0, 0); cv.rect(x0, y1, x1, y1, 0)
    cv.rect(x0, y0, x0, y1, 0); cv.rect(x1, y0, x1, y1, 0)
    cv.rect(x0 + 3, y0 + 2, x1 - 3, y0 + 2, 0); cv.rect(x0 + 3, y0 + 3, x1 - 6, y0 + 3, 0)


def extinguisher(cv):
    _accent(cv, (0x16, 0x16, 0x06), [(7, 2)])
    cv.patch(113, 32, ["0110  ", " 00   ", "03330 "] + ["033330"] * 12 + [" 0000 "])


def plant(cv):
    _accent(cv, (0x1A, 0x19, 0x0A), [(7, 3), (7, 4)])
    cv.patch(112, 48, [              # tile rows 6-9
        "    3   3   3   ",
        "  3  3  3  3  3 ",
        "   3 33 3 33 3  ",
        " 3  3333333333 3",
        "  33333333333333",
        "3  333333333333 ",
        " 333333333333333",
        "  33333333333333",
        "3333333333333333",
        " 33333333333333 ",
        "333333333333333 ",
        " 3333333333333 3",
        "  333333333333  ",
        "   3333333333   ",
        "    33333333    ",
        "  000000000000  ",
        "  011111111110  ",
        "  000000000000  ",
        "   0111111110   ",
        "   0111111110   ",
        "   0111111110   ",
        "   0111111110   ",
        "    01111110    ",
        "    01111110    ",
        "    01111110    ",
        "    01111110    ",
        "     011110     ",
        "     000000     "])
    # black stems fanning out from the pot, so the leaves read as leaves
    for bx, tx, ty in ((5, 1, 6), (6, 4, 2), (8, 8, 1), (10, 12, 2), (11, 15, 6),
                       (6, 2, 10), (10, 14, 10)):
        x0, y0, x1, y1 = 112 + bx, 61, 112 + tx, 48 + ty
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
            if cv.px[y][x] == 3:
                cv.set(x, y, 0)


def umbrella(cv):
    _accent(cv, (0x16, 0x16, 0x06), [(3, 2), (3, 3)])
    cv.patch(52, 40, [              # 24 rows: tile rows 5-7 only
        "     00  ",                # hooked handle, curling over to the right
        "    0  0 ",
        "    0   0",
        "    0   0",
        "    0    ",
        "0   0   0",                # scalloped canopy top
        "30 030 03",
        "033303330",
        "033313330",
        "033313330",
        " 0331330 ",
        " 0331330 ",
        " 0331330 ",
        "  03130  ",
        "  03130  ",
        "  03130  ",
        "  03130  ",
        "   010   ",
        "   010   ",
        "   010   ",
        "    0    ",
        "    3    ",                # tip
        "    3    ",
        "    0    "])


# door colours (morning, evening, night): main, highlight, main
VIOLET = [(0x03, 0x13, 0x03), (0x08, 0x18, 0x08), (0x03, 0x13, 0x03)]
TEAL = [(0x1C, 0x2C, 0x1C), (0x0C, 0x1C, 0x0C), (0x01, 0x11, 0x0C)]
WOOD = [(0x07, 0x17, 0x07), (0x07, 0x17, 0x07), (0x0C, 0x1C, 0x0C)]
NAVY = [(0x02, 0x12, 0x02), (0x17, 0x27, 0x17), (0x0C, 0x1C, 0x0C)]
RED = [(0x06, 0x16, 0x06), (0x07, 0x17, 0x07), (0x02, 0x12, 0x02)]

VARIANTS = [  # (picture, name, scene, door, details)
    (0x2A, 'Nishiyama 1F', 0x2FD, VIOLET, (nameplate,)),
    (0x2B, 'Nishiyama 2F', 0x2E4, TEAL, (nameplate,)),
    (0x2C, 'Nishiyama 3F', 0x2FE, WOOD, (nameplate, extinguisher)),
    (0x2D, 'Flats 1F', 0x361, NAVY, (plant,)),
    (0x2E, 'Flats 2F', 0x362, RED, (umbrella,)),
]


def canvas(base, door, details):
    cv = Canvas(base)
    cv.palette(1, door)
    for d in details:
        d(cv)
    return cv


def retarget(msgs):
    """Swap [cmdF0 19] for the variant in each floor's scene."""
    for pic, _, mid, _, _ in VARIANTS:
        tag = '[cmdF0 %02x]' % BASE
        assert msgs[mid].count(tag) == 1, (hex(mid), msgs[mid])
        msgs[mid] = msgs[mid].replace(tag, '[cmdF0 %02x]' % pic)


def dedupe(new, chr_, keep):
    """Point the original bank-10 pictures at one copy of each tile they
    share a pattern with (same pixels). Returns the slots this frees.
    keep = tiles not to free (frame tiles, tiles new pictures use)."""
    fx = new[FIXED * BANK:]
    chrs = fx[0xED2E - 0xC000:0xED2E - 0xC000 + 37]
    idxs = fx[0xED53 - 0xC000:0xED53 - 0xC000 + 37]
    cb = CHR_BANK * 0x1000
    pics = [p for p in range(37) if chrs[p] == CHR_BANK]
    used = set()
    for p in pics:
        o = 1 * BANK + idxs[p] * 0x130
        used |= set(new[o:o + 280])
    first = {}
    for t in sorted(used | set(keep)):
        first.setdefault(pattern_of(chr_[cb:cb + 0x1000], t), t)
    remap = {t: first[pattern_of(chr_[cb:cb + 0x1000], t)] for t in used}
    remap = {t: c for t, c in remap.items() if t != c and t not in keep}
    for p in pics:
        o = 1 * BANK + idxs[p] * 0x130
        for i in range(280):
            new[o + i] = remap.get(new[o + i], new[o + i])
    return sorted(remap)


def build(data, chr_data, used, free):
    """-> ([(pic, layout bytes, palette record)], {tile: chr bytes}).
    used = tiles of bank 10 in use (any picture); free = slots to use."""
    base = pictures.Picture.original(BASE, data)
    known = {}
    for t in sorted(used):
        known.setdefault(pattern_of(chr_data, t), t)
    free = list(free)
    new_tiles, out = {}, []
    for pic, _, _, door, details in VARIANTS:
        cv = canvas(base, door, details)
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
    base = pictures.Picture.original(BASE, data)
    rows = []
    for pic, name, _, door, details in VARIANTS:
        cv = canvas(base, door, details)
        p = pictures.Picture(CHR_BANK, list(range(280)), cv.blocks, cv.palsets, bytes(4096))
        p.chr = bytearray(b''.join(chr_bytes(pat) for pat in cv.tile_patterns()))
        rows.append(p)
    rows.append(base)
    sheet = Image.new('RGB', (3 * 168, len(rows) * 120), (255, 255, 255))
    for i, p in enumerate(rows):
        for t in range(3):
            sheet.paste(p.render(t), (t * 168, i * 120))
    sheet.resize((sheet.width * 2, sheet.height * 2), 0).save(
        os.path.join(outdir, 'corridor_variants.png'))


if __name__ == '__main__':
    mockups(sys.argv[1])
