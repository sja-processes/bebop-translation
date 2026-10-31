"""Toru's picture for the happiest ending (original bug, found by Stephen
2026-10-31).

The ending ($E747, cmdEA 23) shows a second arrival at the House of
Heaven with picture $E812[hero]: $24 for Hiroshi (Toru arriving in the
doorway) and $25 for Toru. The original never drew $25: its picture
tables end at $24, so Toru's run read past them and showed garbage. (We had since given $25 to
the caretaker's room.)

    $30  $24 with Hiroshi's perm in the doorway instead of Toru's regent
         (the arrival is the other hero; the man seated on the right is
         the same in both runs, so he stays as he is)

CHR bank 13 ($24's bank), using its free tiles; $E813 points at $30.

    python3 tools/endingpic.py OUT.png    mock-up (beside $24)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pictures  # noqa: E402
from storepics import Canvas, chr_bytes, pattern_of  # noqa: E402

CHR_BANK = 13
BASE = 0x24
PIC = 0x30
HERO_PICS = 0xE812            # fixed bank: [Hiroshi's, Toru's] picture


def canvas(o24):
    cv = Canvas(o24)
    # doorway: Toru's regent -> Hiroshi's perm (rounder, curls)
    cx, cy, rx, ry = 83.5, 18, 11, 9.6
    for y in range(8, 18):
        for x in range(72, 96):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                curl = (x * 3 + y * 5) % 7 == 0 and y % 2 == (x // 3) % 2
                cv.set(x, y, 2 if curl else 0)
    return cv


def build(data, chr_data, used, free):
    """-> ([(pic, layout bytes, palette record)], {tile: chr bytes}).
    used = tiles of bank 13 in use; free = slots to use."""
    cv = canvas(pictures.Picture.original(BASE, data))
    known = {}
    for t in sorted(used):
        known.setdefault(pattern_of(chr_data, t), t)
    free = list(free)
    new_tiles, tiles = {}, []
    for pat in cv.tile_patterns():
        if pat not in known:
            t = free.pop(0)
            known[pat] = t
            new_tiles[t] = chr_bytes(pat)
        tiles.append(known[pat])
    p = pictures.Picture(CHR_BANK, tiles, cv.blocks, cv.palsets, chr_data)
    return [(PIC, p.layout_bytes(), p.palette_record())], new_tiles


def apply_hook(fixed):
    """Toru's run shows $30 (fixed = the fixed bank's bytes)."""
    o = HERO_PICS + 1 - 0xC000
    assert fixed[o - 1:o + 1] == bytes([0x24, 0x25]), fixed[o - 1:o + 1].hex()
    fixed[o] = PIC


if __name__ == '__main__':
    from PIL import Image
    o24 = pictures.Picture.original(BASE)
    cv = canvas(o24)
    p = pictures.Picture(CHR_BANK, list(range(280)), cv.blocks, cv.palsets, bytes(4096))
    p.chr = b''.join(chr_bytes(pat) for pat in cv.tile_patterns())
    sheet = Image.new('RGB', (2 * 168, 112), (255, 255, 255))
    sheet.paste(o24.render(0), (0, 0))
    sheet.paste(p.render(0), (168, 0))
    sheet.resize((sheet.width * 3, sheet.height * 3), 0).save(sys.argv[1])
