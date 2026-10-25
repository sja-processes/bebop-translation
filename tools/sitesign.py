"""English "SAFETY ✓ FIRST" sign above the Japanese 安全✚第一 on the
building site in Higashimachi (area 3).

The Japanese sign is large and clear, so players might wonder whether it
matters; it is just the standard workplace slogan (Stephen, 2026-10-25).
The English sign sits on the blue sheeting directly above it, the same
width (5 metatiles, map metatile row $1B, columns $16-$1A), and copies its
look: light panel, black letters, black frame, with an olive tick (black
outline, like the green cross) in the middle as the cross is. Same map
palette 0 as the Japanese sign (black / olive / grey / light grey by day),
so it changes with the time of day the same way and stays readable at
night (light-on-olive would vanish: the night palette makes them equal).

Map facts: area 3's map is bank 0 $9657 (W $C, H $10 blocks, data at +3),
its block / metatile / attribute tables come from $C6C9 / $C6D5 / $C6E1,
CHR bank 3. Row $1B is the last row of block row 6, where both blocks
(5,6) and (6,6) are block $14 (used nowhere else). The left part of the
sign (block-local columns 2-3) goes into $14 in place; the right part
(columns 0-2) needs a different block, so (6,6) becomes spare block 0
(unused by the map and written by no code; $17 / $18 are the flag-$B4
shutter blocks). Flag $B4 swaps block row 7 (the Japanese sign row and
shutter), which keeps the Japanese sign, so the pair still lines up.
"""
BANK = 0x4000
AREA = 3
CHR_BANK = 3
MAP_PTR = 0x8000 + AREA * 2
ROW, COL0, WIDTH = 0x1B, 0x16, 5          # map metatile row and columns
OLD_BLOCK, NEW_BLOCK = 0x14, 0x00
BLOCK_ROW, LEFT_BX, RIGHT_BX = 6, 5, 6
ATTR = 0x10                               # solid, palette 0 (as the Japanese sign)
N_METAS = 0xB2                            # attribute table $AA52-$AB03

# colours: 0 black, 1 olive, 3 light grey (palette 0)
_GLYPHS = {
    'S': [".##.", "#..#", "#...", ".##.", "...#", "#..#", ".##."],
    'A': [".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#"],
    'F': ["####", "#...", "#...", "###.", "#...", "#...", "#..."],
    'E': ["####", "#...", "#...", "###.", "#...", "#...", "####"],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'I': ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    'R': ["###.", "#..#", "#..#", "###.", "#.#.", "#..#", "#..#"],
}
TICK = ["........#", ".......##", "#.....##.", "##...##..", ".##.##...", "..###....", "...#....."]


def _word(w):
    return [''.join(_GLYPHS[c][y] + ('.' if i < len(w) - 1 else '') for i, c in enumerate(w))
            for y in range(7)]


def sign_pixels():
    """-> 16 rows x 80 colour indices."""
    px = [[0 if y in (0, 15) or x in (0, 79) else 3 for x in range(80)] for y in range(16)]

    def put(rows, x0, colour, y0=4):
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == '#':
                    px[y0 + y][x0 + x] = colour
    put(_word('SAFETY'), 3, 0)
    tx, ty = 42 - len(TICK[0]) // 2, 8 - len(TICK) // 2
    pts = {(tx + x, ty + y) for y, r in enumerate(TICK) for x, c in enumerate(r) if c == '#'}
    for x, y in pts:                      # outline: straight neighbours only
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (x + dx, y + dy) not in pts:
                px[y + dy][x + dx] = 0
    for x, y in pts:
        px[y][x] = 1
    put(_word('FIRST'), 51, 0)
    return px


def _tile_bytes(rows):
    lo = bytes(sum((rows[y][x] & 1) << (7 - x) for x in range(8)) for y in range(8))
    hi = bytes(sum((rows[y][x] >> 1) << (7 - x) for x in range(8)) for y in range(8))
    return lo + hi


def apply(new, chr_, fixed):
    """Edit bank 0 (map tables) and CHR bank 3 in place."""
    b0 = lambda a: new[a - 0x8000]
    fw = lambda a: fixed[a - 0xC000] | fixed[a - 0xC000 + 1] << 8
    blocks, metas, attrs = fw(0xC6C9 + AREA * 2), fw(0xC6D5 + AREA * 2), fw(0xC6E1 + AREA * 2)
    p = b0(MAP_PTR) | b0(MAP_PTR + 1) << 8
    w, h = b0(p), b0(p + 1)
    grid = [b0(p + 3 + i) for i in range(w * h)]
    n_blocks = (metas - blocks) // 16
    assert grid.count(OLD_BLOCK) == 2 and NEW_BLOCK not in grid
    assert grid[BLOCK_ROW * w + LEFT_BX] == grid[BLOCK_ROW * w + RIGHT_BX] == OLD_BLOCK
    used_mt = {b0(blocks + b * 16 + i) for b in range(n_blocks) for i in range(16)}
    used_tiles = {b0(metas + m * 4 + q) for m in used_mt for q in range(4)}
    cb = CHR_BANK * 0x1000
    existing = {}
    for t in sorted(used_tiles):
        existing.setdefault(bytes(chr_[cb + t * 16:cb + t * 16 + 16]), t)
    free_tiles = [t for t in range(256) if t not in used_tiles]
    free_mt = [m for m in range(N_METAS) if m not in used_mt]
    px = sign_pixels()
    sign_mt, added = [], 0
    for k in range(WIDTH):
        quads = []
        for q in range(4):
            rows = [px[(q // 2) * 8 + y][k * 16 + (q % 2) * 8:k * 16 + (q % 2) * 8 + 8] for y in range(8)]
            data = _tile_bytes(rows)
            if data not in existing:
                t = free_tiles.pop(0)
                chr_[cb + t * 16:cb + t * 16 + 16] = data
                existing[data] = t
                added += 1
            quads.append(existing[data])
        m = free_mt.pop(0)
        new[metas - 0x8000 + m * 4:metas - 0x8000 + m * 4 + 4] = bytes(quads)
        new[attrs - 0x8000 + m] = ATTR
        sign_mt.append(m)
    # right block: copy of the original $14, then both get their part of the sign
    src = blocks - 0x8000 + OLD_BLOCK * 16
    dst = blocks - 0x8000 + NEW_BLOCK * 16
    new[dst:dst + 16] = new[src:src + 16]
    local_row = ROW % 4
    for k, m in enumerate(sign_mt):
        mx = COL0 + k
        blk = OLD_BLOCK if mx // 4 == LEFT_BX else NEW_BLOCK
        new[blocks - 0x8000 + blk * 16 + local_row * 4 + mx % 4] = m
    new[p - 0x8000 + 3 + BLOCK_ROW * w + RIGHT_BX] = NEW_BLOCK
    return {'new tiles': added, 'free tiles left': len(free_tiles), 'metatiles': sign_mt}
