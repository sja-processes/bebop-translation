"""Caretaker's room picture draft (no clock: the game's time of day changes): 160x112 (20x14 tiles), one palette per 16x16 block.

Colours: 'k' black (universal), P0 wood 'b' 07 'm' 17 't' 27,
P1 grey 'G' 00 'l' 10 'W' 30, P2 red 'r' 16 'p' 26 'W' 30.
"""
PALS = [(0x07, 0x17, 0x27), (0x00, 0x10, 0x30), (0x16, 0x26, 0x30)]
NESIDX = {'b': 0x07, 'm': 0x17, 't': 0x27, 'G': 0x00, 'l': 0x10, 'W': 0x30, 'r': 0x16, 'p': 0x26, 'k': 0x0F}
W, H = 160, 112


class Pic:
    def __init__(self):
        self.p = [['W'] * W for _ in range(H)]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def frame(self, x0, y0, x1, y1, c):
        self.rect(x0, y0, x1, y0, c); self.rect(x0, y1, x1, y1, c)
        self.rect(x0, y0, x0, y1, c); self.rect(x1, y0, x1, y1, c)

    def patch(self, x0, y0, rows):
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c != ' ':
                    self.set(x0 + dx, y0 + dy, c)


def draw():
    pc = Pic()
    # ceiling boards and the wooden beam (rows 0..15)
    pc.rect(0, 0, 159, 11, 'm')
    for x in range(0, 160, 16):
        pc.rect(x, 0, x, 11, 'b')
    pc.rect(0, 11, 159, 11, 'b')
    pc.rect(0, 12, 159, 15, 't')
    pc.rect(0, 15, 159, 15, 'b')
    # wall (light grey plaster) rows 16..79 is the default 'l'
    # floorboards rows 80..111
    pc.rect(0, 80, 159, 111, 't')
    pc.rect(0, 80, 159, 81, 'b')                       # skirting shadow
    for y in range(87, 112, 8):
        pc.rect(0, y, 159, y, 'm')
    for y0 in range(82, 112, 8):
        off = 24 if (y0 // 8) % 2 else 0
        for x in range(off, 160, 48):
            pc.rect(x, y0, x, min(y0 + 4, 111), 'm')
    # window, left: x 0..47, y 16..47 (P1)
    pc.rect(0, 16, 47, 47, 'G')
    pc.rect(3, 19, 44, 44, 'W')                        # sky
    pc.rect(3, 33, 44, 44, 'l')                        # school building outside
    for x in range(6, 44, 8):
        pc.rect(x, 36, x + 4, 38, 'G'); pc.rect(x, 41, x + 4, 43, 'G')
    pc.rect(3, 32, 44, 32, 'G')
    pc.rect(23, 19, 24, 44, 'G')                       # sash bar
    pc.frame(2, 18, 45, 45, 'k')
    pc.rect(0, 46, 47, 47, 'k')                        # sill
    # desk under the window, x 0..47, y 80..111 is floor; desk top at y 64..79 (P0)
    pc.rect(0, 64, 47, 79, 'm')
    pc.rect(0, 64, 47, 66, 't')
    pc.rect(0, 67, 47, 67, 'k')
    pc.patch(4, 70, ["kkkkkkkkkkkk"]); pc.patch(30, 70, ["kkkkkkkkkkkk"])   # drawer edges
    pc.patch(9, 72, ["kk"]); pc.patch(35, 72, ["kk"])                        # handles
    # desk legs over the floor
    pc.rect(1, 80, 3, 95, 'b'); pc.rect(44, 80, 46, 95, 'b')
    # kettle on a tray against the wall above the desk: x 16..31, y 48..63 (P1)
    pc.patch(16, 49, [
        "     kkkk       ",
        "    kGGGGk      ",
        "  kkkkkkkkkk    ",
        " kllllllllllk  k",
        "kllWWllllllllkkk",
        "kllWWllllllllkk ",
        "klllllllllllllk ",
        "klllllllllllllk ",
        "kGGGGGGGGGGGGGk ",
        " kGGGGGGGGGGGk  ",
        "  kkkkkkkkkkk   ",
        "                ",
        "kkkkkkkkkkkkkkkk",
        "GGGGGGGGGGGGGGGG",
        "kkkkkkkkkkkkkkkk",
    ])
    # mug: x 32..47, y 48..63 (P1)
    pc.patch(34, 54, [
        " kkkkkk  ",
        " kWWWWkkk",
        " kWWWWk k",
        " kWWWWkkk",
        " kWWWWk  ",
        "  kkkk   ",
        "         ",
        "kkkkkkkkk",
        "GGGGGGGGG",
        "kkkkkkkkk",
    ])
    pc.rect(43, 61, 47, 63, 'G'); pc.rect(43, 61, 47, 61, 'k'); pc.rect(43, 63, 47, 63, 'k')
    # calendar: x 96..111 y 16..47 (P2: red header, white page, red dates)
    pc.rect(96, 16, 111, 47, 'W')
    pc.rect(98, 18, 109, 45, 'W')
    pc.rect(98, 18, 109, 23, 'r')
    pc.frame(97, 17, 110, 46, 'k')
    for yy in range(26, 44, 4):
        for xx in range(99, 109, 3):
            pc.set(xx, yy, 'k')
    pc.set(105, 30, 'r'); pc.set(106, 30, 'r'); pc.set(105, 31, 'r'); pc.set(106, 31, 'r')
    # but blocks 96..111 x 16..47 must hold only P2 colours: wall there is white
    # key board, right: x 112..159 y 16..63 (P0 wood) with keys on hooks
    pc.rect(112, 16, 159, 47, 'm')
    pc.rect(114, 18, 157, 45, 't')
    pc.frame(113, 17, 158, 46, 'k')
    for row, y in enumerate((20, 33)):
        for x in range(118, 156, 8):
            pc.set(x + 2, y, 'k')                      # hook
            pc.patch(x, y + 1, [
                " kk ",
                "k  k",
                " kk ",
                " bb ",
                " bk ",
                " bb ",
                "kkkk",
                "kmmk",
                "kkkk",
            ])
    # fire extinguisher on a wall bracket: x 144..159 y 48..79 (P2)
    pc.patch(146, 50, [
        "   kkkk     ",
        "  kkrrkkkk  ",
        "   kkkk  kk ",
        "  krrrrk  k ",
        " krrrrrrk k ",
        " krrrrrrkk  ",
        " krWrrrrk   ",
        " krWrrrrk   ",
        " krWWWWrk   ",
        " krWkkWrk   ",
        " krWWWWrk   ",
        " krWrrrrk   ",
        "kkrWrrrrkk  ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        " krrrrrrk   ",
        "  kkkkkk    ",
    ])
    # straw broom (houki) leaning on the wall: handle over the wall in grey
    # (P1 blocks), straw head on the floor in browns (P0 blocks, x 128..143)
    for i in range(39):
        y = 51 + i
        x = 141 - i // 6
        c1, c2 = ('k', 'G') if y < 80 else ('k', 'b')
        pc.set(x - 1, y, c1); pc.set(x, y, c2); pc.set(x + 1, y, 'k')
    cx = 135
    pc.patch(cx - 2, 88, ["kkkkk", "kmbmk", "kkkkk"])           # cord binding
    for y in range(91, 100):
        w = 2 + (y - 91) * 0.55
        x0, x1 = int(cx - w), int(cx + w)
        for x in range(x0, x1 + 1):
            if x in (x0, x1):
                c = 'k'
            else:
                strand = int((x - cx) * 6 / (w + 1))
                c = 'm' if strand % 2 == 0 else 'b'
                if (x + y) % 7 == 0:
                    c = 'k'
            pc.set(x, y, c)
    # ragged bristle ends: strands of uneven length, a few splaying out
    lengths = [1, 3, 2, 0, 3, 1, 2, 4, 1, 2, 0, 3, 2, 1]
    x0 = int(cx - 6.4)
    for k, x in enumerate(range(x0, int(cx + 6.4) + 1)):
        n = lengths[k % len(lengths)]
        for d in range(n + 1):
            pc.set(x, 100 + d, 'b' if (x + d) % 2 else 'm')
        pc.set(x, 101 + n, 'k') if n >= 2 else None
    for (x, y) in ((x0 - 1, 99), (x0 - 2, 100), (x0 - 3, 101), (int(cx + 6.4) + 1, 99), (int(cx + 6.4) + 2, 101)):
        pc.set(x, y, 'b')
    return pc


def blocks(pc):
    """-> 10x7 palette numbers; reports blocks whose colours fit no palette."""
    pal_sets = [set(c for c, n in NESIDX.items() if n in p) | {'k'} for p in PALS]
    out = []
    bad = []
    for by in range(7):
        row = []
        for bx in range(10):
            cols = {pc.get(x, y) for y in range(by * 16, by * 16 + 16) for x in range(bx * 16, bx * 16 + 16)}
            fits = [i for i, s in enumerate(pal_sets) if cols <= s]
            if not fits:
                bad.append((bx, by, cols)); fits = [1]
            row.append(fits[0])
        out.append(row)
    return out, bad


def tiles(pc, bl):
    """-> layout of 20x14 tile patterns (tuple of 64 indices)."""
    pats = []
    for ty in range(14):
        for tx in range(20):
            pal = PALS[bl[ty // 2][tx // 2]]
            pat = []
            for y in range(8):
                for x in range(8):
                    c = pc.get(tx * 8 + x, ty * 8 + y)
                    pat.append(0 if c == 'k' else pal.index(NESIDX[c]) + 1)
            pats.append(tuple(pat))
    return pats


def render(pc, scale=1):
    from nespal import NES
    from PIL import Image
    im = Image.new('RGB', (W, H))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), NES[NESIDX[pc.get(x, y)]])
    return im


if __name__ == '__main__':
    import sys
    sys.path.insert(0, sys.argv[1])
    pc = draw()
    bl, bad = blocks(pc)
    for b in bad:
        print('BAD block', b)
    pats = tiles(pc, bl)
    print('unique tiles', len(set(pats)))
    render(pc).resize((W * 4, H * 4), 0).save(sys.argv[1] + '/ct_room.png')
