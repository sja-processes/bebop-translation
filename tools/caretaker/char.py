"""Caretaker character draft v2: 64x64 sprite bust, cells 8x8, one palette per cell.

Colour codes: '.' transparent, '#' black (any palette)
  A (head):   's' skin, 'g' grey hair
  B (jacket): 'j' navy, 'J' blue
  C (towel):  'c' grey, 'w' white
"""
PALS = {'A': (0x0F, 0x36, 0x10), 'B': (0x0F, 0x01, 0x11), 'C': (0x0F, 0x00, 0x30)}
CODE = {'s': ('A', 2), 'g': ('A', 3), 'j': ('B', 2), 'J': ('B', 3), 'c': ('C', 2), 'w': ('C', 3)}
W = H = 64

# left edge of the head (excluding ears) per row; the right edge mirrors it (63 - x)
EDGE = {1: 26, 2: 23, 3: 21, 4: 20, 5: 19, 6: 18, 7: 18}
EDGE.update({y: 17 for y in range(8, 29)})
EDGE.update({29: 18, 30: 18, 31: 19, 32: 20, 33: 21, 34: 22, 35: 23, 36: 25, 37: 27})


class Canvas:
    def __init__(self):
        self.p = [['.'] * W for _ in range(H)]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < W and 0 <= y < H else '.'

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def patch(self, x0, y0, rows, mirror=False):
        """Draw rows at (x0,y0); with mirror, also draw the reflection about x=31.5."""
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c != ' ':
                    self.set(x0 + dx, y0 + dy, c)
                    if mirror:
                        self.set(63 - (x0 + dx), y0 + dy, c)

    def outline(self, inside):
        out = [(x, y) for y in range(H) for x in range(W)
               if self.p[y][x] == '.' and any(inside(self.get(x + dx, y + dy))
                                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in out:
            self.set(x, y, '#')


def head(cv):
    for y, xl in EDGE.items():
        cv.rect(xl, y, 63 - xl, y, 's')
    cv.rect(26, 37, 37, 39, 's')                       # neck (collar covers below)
    # ears (left, mirrored)
    cv.patch(14, 16, ["  ", " s", "ss", "ss", "ss", "ss", "ss", " s", " s"], mirror=True)
    cv.outline(lambda c: c in 'sg')
    # grey hair above and round the ears: tufts with dark strands
    cv.patch(16, 7, [
        " #g  ",
        "#ggg ",
        "#g#gg",
        "#gg#g",
        "#g#gg",
        "#gg#g",
        "#g#g ",
        "#gg# ",
        "#g#  ",
        "#gg  ",
        "#g   ",
    ], mirror=True)
    # forehead lines and crown shine
    cv.patch(24, 6, [
        "     #### ",
        "          ",
        " ###    ###",
    ])
    cv.patch(36, 3, ["##", "#"])
    cv.patch(36, 9, ["####"])
    # bushy grey brows, kindly closed eyes with crow's feet
    cv.patch(19, 12, [
        "   gggggg  ",
        "  gggggggg ",
        " g#g##g##  ",
        "           ",
        "    ####   ",
        "   #    #  ",
        "#          ",
        " #  #      ",
        "  ##   ##  ",
    ], mirror=True)
    # nose
    cv.patch(29, 20, [
        "  #  ",
        "  #  ",
        "  # #",
        " #   ",
        "#     ",
        "#  ## ",
        " ##  #",
    ])
    cv.patch(35, 22, ["#", "#", " #", "  #", "  #", " #"])
    # cheek lines and moustache
    cv.patch(21, 24, [
        "#     ",
        " #    ",
        " #    ",
        "  #   ",
    ], mirror=True)
    cv.patch(23, 27, [
        "    gggg",
        "  gggg#g",
        " ggg#ggg",
        "gg##gg##",
        "#     ##",
    ], mirror=True)
    # mouth (closed) and chin
    cv.patch(28, 33, ["########"])
    cv.patch(29, 35, ["      "])
    cv.patch(27, 36, [" #    #"])


def talk(cv):
    """Talking frame: open mouth under the moustache."""
    cv.patch(27, 32, [
        " ######### ",
        " #sssssss# ",
        "  #######  ",
    ])


def body(cv):
    # navy work jacket on the shoulders, sloping up to the neck
    for x in range(64):
        d = abs(x - 31.5)
        top = 42 + max(0, int((d - 13) * 0.5))
        for y in range(top, 64):
            cv.set(x, y, 'j')
    for x in range(64):                               # highlight along the shoulder line
        for y in range(40, 64):
            if cv.get(x, y) == 'j' and cv.get(x, y - 2) == '.':
                cv.set(x, y, 'J')
    # shirt opening in cols 3-4 (x24..39): white collar, grey vest, V neck
    cv.rect(24, 40, 39, 63, 'c')
    cv.patch(24, 40, [
        "wwww########wwww",
        "wwwww#cccc#wwwww",
        "#wwwww#cc#wwwww#",
        "c#wwwww##wwwww#c",
        "cc#wwww##wwww#cc",
        "ccc#www##www#ccc",
        "cccc#ww##ww#cccc",
        "ccccc######ccccc",
        "ccccccc##ccccccc",
        "ccccccc#cccccccc",
    ])
    cv.patch(24, 40, ["", "", "", "", "", "", "", "", "", ""])
    for y in (52, 57, 62):
        cv.set(30, y, 'w'); cv.set(31, y, '#')
    # lapels in cols 2 and 5
    cv.patch(16, 40, [
        "    ####",
        "   #JJJ#",
        "  #JJJJ#",
        "  #JJJJ#",
        "  #JJJ# ",
        "  #JJJ# ",
        "  #JJ#  ",
        "  #JJ#  ",
        "  #JJ#  ",
        "   #J#  ",
        "   #J#  ",
        "   ##   ",
    ], mirror=True)
    for y in range(52, 64):
        cv.set(23, y, '#'); cv.set(40, y, '#')
    # neck skin shows above the collar in cols 3-4 only
    # breast pocket with a pen (viewer's right)
    cv.patch(49, 50, [
        "    J    ",
        "    J    ",
        "#########",
        "#jjjJjjj#",
        "#jjjjjjj#",
        "#jjjjjjj#",
        "#########",
    ])
    cv.patch(10, 58, ["#", "#", "#", "#", "#", "#"])
    cv.patch(7, 52, ["#", "#", " #", " #"])


def build(talking=False):
    cv = Canvas()
    body(cv)
    head(cv)
    if talking:
        talk(cv)
    return cv


def cells(cv):
    out = {}
    for r in range(8):
        for c in range(8):
            px = [[cv.p[r * 8 + y][c * 8 + x] for x in range(8)] for y in range(8)]
            flat = [p for row in px for p in row]
            if all(p == '.' for p in flat):
                continue
            pals = {CODE[p][0] for p in flat if p in CODE}
            if len(pals) > 1:
                print('MIXED', c, r, pals)
                pals = {sorted(pals)[0]}
            pal = pals.pop() if pals else 'A'
            idx = [[0 if p == '.' else 1 if p == '#' else CODE[p][1] for p in row] for row in px]
            out[(c, r)] = (pal, idx)
    return out


def image(cs, bg=(90, 90, 90)):
    from nespal import NES
    from PIL import Image
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0) if bg is None else bg + (255,))
    for (c, r), (pal, idx) in cs.items():
        for y in range(8):
            for x in range(8):
                v = idx[y][x]
                if v:
                    im.putpixel((c * 8 + x, r * 8 + y), NES[PALS[pal][v - 1]] + (255,))
    return im


if __name__ == '__main__':
    import sys
    sys.path.insert(0, sys.argv[1])
    from PIL import Image
    imgs = []
    for t in (False, True):
        cs = cells(build(t))
        imgs.append(image(cs))
        uniq = {tuple(tuple(r) for r in idx) for _, idx in cs.values()}
        print('talking' if t else 'base', 'cells', len(cs), 'unique tiles', len(uniq))
    sheet = Image.new('RGB', (136, 64), (255, 255, 255))
    sheet.paste(imgs[0], (0, 0)); sheet.paste(imgs[1], (72, 0))
    sheet.resize((136 * 4, 64 * 4), 0).save(sys.argv[1] + '/ct_char.png')
