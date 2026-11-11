#!/usr/bin/env python3
"""Compare the 37 original scene pictures in the original ROM and out/bebop_en.nes.

usage: tools/picdiff.py [--all] [OUT_DIR]

Renders each picture (morning palette) from both ROMs with the loader's
own tables (pictures.py's facts, fixed bank = the last PRG bank, so it
works on the expanded ROM too) and lists the ones that differ, with the
tiles that changed. Writes OUT_DIR/picNN.png (original | ours | changed
tiles in red) for each difference (default out/picdiff). Only $1D (the
"CLOSED" caption) should differ.

Then the new pictures (the caretaker's room $25, the floor variants
$26-$2F, Toru's ending $30), which have no original: it runs the build
with insert.SNAPSHOTS on, so each one comes back with its CHR bank as it
was right after its own tiles were written, and checks that the finished
ROM still has the same pixels in every tile the picture uses (all three
times of day), and its layout and palette record in the data bank. A
difference means a later step drew over it, as the title info did to the
warehouse. Writes OUT_DIR/newNN.png (as built | finished | changed) for
each one that differs.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pictures  # noqa: E402

BANK = 0x4000


def load(data, pic):
    nprg = data[4]
    prg = data[16:16 + nprg * BANK]
    chr_ = data[16 + nprg * BANK:]
    fixed = prg[(nprg - 1) * BANK:]
    bank = fixed[0xED2E - 0xC000 + pic]
    idx = fixed[0xED53 - 0xC000 + pic]
    lay = prg[BANK + idx * 0x130:BANK + idx * 0x130 + 0x130]
    blocks = []
    for by in range(7):
        row = []
        for bx in range(10):
            i, sh = pictures.attr_index(bx, by)
            row.append((lay[280 + i] >> sh) & 3)
        blocks.append(row)
    rec = 0xD356 + (pic + 6) * 39 - 0xC000
    palsets = [fixed[rec + 13 * t:rec + 13 * t + 13] for t in range(3)]
    return pictures.Picture(bank, lay[:280], blocks, palsets,
                            chr_[bank * 0x1000:(bank + 1) * 0x1000])


def from_layout(bank, lay, pal, chr_data):
    blocks = []
    for by in range(7):
        row = []
        for bx in range(10):
            i, sh = pictures.attr_index(bx, by)
            row.append((lay[280 + i] >> sh) & 3)
        blocks.append(row)
    palsets = [pal[13 * t:13 * t + 13] for t in range(3)]
    return pictures.Picture(bank, lay[:280], blocks, palsets, chr_data)


def strip(p):
    from PIL import Image
    im = Image.new('RGB', (160, 112 * 3))
    for t in range(3):
        im.paste(p.render(t), (0, 112 * t))
    return im


def check_new(out):
    """-> number of new pictures that differ."""
    from PIL import Image, ImageDraw
    import insert
    insert.SNAPSHOTS = []
    try:
        _, rom, *_ = insert.build()
    finally:
        snaps, insert.SNAPSHOTS = insert.SNAPSHOTS, None
    nprg = rom[4]
    prg = rom[16:16 + nprg * BANK]
    chr_ = rom[16 + nprg * BANK:]
    data_bank = prg[14 * BANK:15 * BANK]
    bad = 0
    for num, bank, lay, pal, built in snaps:
        final = chr_[bank * 0x1000:(bank + 1) * 0x1000]
        a = from_layout(bank, lay, pal, built)
        b = from_layout(bank, lay, pal, final)
        ia, ib = strip(a), strip(b)
        problems = []
        if lay not in data_bank:
            problems.append('layout not in the data bank')
        if pal not in data_bank:
            problems.append('palette record not in the data bank')
        tiles = sorted({t for t in lay[:280] if built[t * 16:t * 16 + 16] != final[t * 16:t * 16 + 16]})
        if tiles:
            problems.append('CHR bank %d tiles drawn over: %s' % (
                bank, ' '.join('%02X' % t for t in tiles)))
        print('new %02X (CHR bank %d): %s' % (num, bank, '; '.join(problems) or 'ok'))
        if problems:
            bad += 1
            mark = ib.copy()
            d = ImageDraw.Draw(mark)
            for t in range(3):
                for i in range(280):
                    if lay[i] in tiles:
                        x, y = i % 20 * 8, i // 20 * 8 + 112 * t
                        d.rectangle((x, y, x + 7, y + 7), outline=(255, 0, 0))
            sheet = Image.new('RGB', (160 * 3 + 16, 112 * 3), (255, 255, 255))
            for i, im in enumerate((ia, ib, mark)):
                sheet.paste(im, (i * 168, 0))
            sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(
                os.path.join(out, 'new%02X.png' % num))
    return bad


def tile_pixels(p, t):
    return bytes(p.chr[t * 16:t * 16 + 16])


def main():
    from PIL import Image, ImageDraw
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else os.path.join(ROOT, 'out', 'picdiff')
    os.makedirs(out, exist_ok=True)
    o = open(glob.glob(os.path.join(ROOT, 'rom', '*.nes'))[0], 'rb').read()
    n = open(os.path.join(ROOT, 'out', 'bebop_en.nes'), 'rb').read()
    count = 37                                    # the original pictures; ours load through hooks
    for pic in range(count):
        try:
            a, b = load(o, pic), load(n, pic)
            ia, ib = a.render(), b.render()
        except (IndexError, ValueError):
            continue
        if ia.tobytes() == ib.tobytes() and '--all' not in sys.argv:
            continue
        cells = [(i % 20, i // 20) for i in range(280)
                 if ia.crop((i % 20 * 8, i // 20 * 8, i % 20 * 8 + 8, i // 20 * 8 + 8)).tobytes()
                 != ib.crop((i % 20 * 8, i // 20 * 8, i % 20 * 8 + 8, i // 20 * 8 + 8)).tobytes()]
        why = []
        if a.chr_bank != b.chr_bank:
            why.append('CHR bank %02X -> %02X' % (a.chr_bank, b.chr_bank))
        lay = sum(1 for i in range(280) if a.tiles[i] != b.tiles[i])
        if lay:
            why.append('%d layout bytes' % lay)
        art = sorted({a.tiles[y * 20 + x] for x, y in cells
                      if a.tiles[y * 20 + x] == b.tiles[y * 20 + x]
                      and tile_pixels(a, a.tiles[y * 20 + x]) != tile_pixels(b, b.tiles[y * 20 + x])})
        if art:
            why.append('tile art changed: ' + ' '.join('%02X' % t for t in art))
        if a.palsets != b.palsets:
            why.append('palettes')
        if a.blocks != b.blocks:
            why.append('attributes')
        print('pic %02X: %d cells differ; %s' % (pic, len(cells), '; '.join(why) or 'same'))
        mark = ib.copy()
        d = ImageDraw.Draw(mark)
        for x, y in cells:
            d.rectangle((x * 8, y * 8, x * 8 + 7, y * 8 + 7), outline=(255, 0, 0))
        sheet = Image.new('RGB', (160 * 3 + 16, 112), (255, 255, 255))
        for i, im in enumerate((ia, ib, mark)):
            sheet.paste(im, (i * 168, 0))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(
            os.path.join(out, 'pic%02X.png' % pic))
    check_new(out)


if __name__ == '__main__':
    main()
