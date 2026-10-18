"""Read, render and build scene pictures (the 20x14-tile lower window).

A picture: CHR bank, 280 tile numbers, a 10x7 grid of 16x16 block
palettes (from the 24 attribute bytes) and three palette sets (morning /
evening / night, 13 bytes each: background colour + 4 palettes x 3).
Loader facts (PLAN.md): CHR bank = $ED2E[pic], layout = PRG bank 1
$8000 + $ED53[pic] * $130, palette record = $D356 + (pic + 6) * 39.

    python3 tools/pictures.py PIC OUT.png [--grid]   render all three times
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, 'caretaker'))
from nespal import NES  # noqa: E402

BANK = 0x4000
W, H = 20, 14


def rom():
    return open(glob.glob(os.path.join(ROOT, 'rom', '*.nes'))[0], 'rb').read()


def attr_index(bx, by):
    """Picture block -> (attribute byte index, bit shift)."""
    col, row = 6 + 2 * bx, 14 + 2 * by
    return (col // 4 - 1) + 6 * (row // 4 - 3), 2 * (((col % 4) // 2) + 2 * ((row % 4) // 2))


class Picture:
    def __init__(self, chr_bank, tiles, blocks, palsets, chr_data):
        self.chr_bank = chr_bank
        self.tiles = list(tiles)          # 280 tile numbers
        self.blocks = [list(r) for r in blocks]   # 7 rows x 10 palette numbers
        self.palsets = [list(p) for p in palsets]  # 3 x 13 bytes
        self.chr = bytearray(chr_data)    # 4 KB pattern data (tiles may be replaced)

    @classmethod
    def original(cls, pic, data=None):
        data = data or rom()
        prg = data[16:16 + 8 * BANK]
        chr_ = data[16 + 8 * BANK:]
        fixed = prg[7 * BANK:]
        bank = fixed[0xED2E - 0xC000 + pic]
        idx = fixed[0xED53 - 0xC000 + pic]
        lay = prg[1 * BANK + idx * 0x130:1 * BANK + idx * 0x130 + 0x130]
        blocks = []
        for by in range(7):
            row = []
            for bx in range(10):
                i, sh = attr_index(bx, by)
                row.append((lay[280 + i] >> sh) & 3)
            blocks.append(row)
        rec = 0xD356 + (pic + 6) * 39 - 0xC000
        palsets = [fixed[rec + 13 * t:rec + 13 * t + 13] for t in range(3)]
        return cls(bank, lay[:280], blocks, palsets, chr_[bank * 0x1000:(bank + 1) * 0x1000])

    def pixel_index(self, t, x, y):
        lo = self.chr[t * 16 + y]
        hi = self.chr[t * 16 + 8 + y]
        return ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)

    def render(self, time=0):
        from PIL import Image
        im = Image.new('RGB', (W * 8, H * 8))
        ps = self.palsets[time]
        px = im.load()
        for ty in range(H):
            for tx in range(W):
                t = self.tiles[ty * W + tx]
                p = self.blocks[ty // 2][tx // 2]
                for y in range(8):
                    for x in range(8):
                        v = self.pixel_index(t, x, y)
                        c = ps[0] if v == 0 else ps[1 + p * 3 + v - 1]
                        px[tx * 8 + x, ty * 8 + y] = NES[c & 0x3F]
        return im

    def layout_bytes(self):
        attr = [0xFF] * 24
        for by in range(7):
            for bx in range(10):
                i, sh = attr_index(bx, by)
                attr[i] = (attr[i] & ~(3 << sh)) | (self.blocks[by][bx] << sh)
        return bytes(self.tiles) + bytes(attr)

    def palette_record(self):
        return b''.join(bytes(p) for p in self.palsets)


def sheet(pic_obj, scale=3, grid=False):
    """Morning / evening / night side by side."""
    from PIL import Image, ImageDraw
    ims = [pic_obj.render(t) for t in range(3)]
    out = Image.new('RGB', (3 * 168, 112), (255, 255, 255))
    for i, im in enumerate(ims):
        out.paste(im, (i * 168, 0))
    out = out.resize((out.width * scale, out.height * scale), 0)
    if grid:
        d = ImageDraw.Draw(out)
        for i in range(3):
            for tx in range(W + 1):
                x = (i * 168 + tx * 8) * scale
                d.line([(x, 0), (x, 112 * scale)], fill=(255, 0, 255) if tx % 2 == 0 else (120, 0, 120))
            for ty in range(H + 1):
                y = ty * 8 * scale
                d.line([(i * 168 * scale, y), ((i * 168 + 160) * scale, y)],
                       fill=(255, 0, 255) if ty % 2 == 0 else (120, 0, 120))
    return out


if __name__ == '__main__':
    pic = int(sys.argv[1], 16)
    p = Picture.original(pic)
    print('CHR bank', p.chr_bank, 'palettes', [bytes(s).hex(' ') for s in p.palsets])
    for r in range(H):
        print(' '.join('%02X' % t for t in p.tiles[r * W:(r + 1) * W]))
    print('blocks', p.blocks)
    sheet(p, grid='--grid' in sys.argv).save(sys.argv[2])
