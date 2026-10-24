"""Cars drawn in the Nishiyama Building car park (town map, area 1).

Two car scenes had nothing on the map (Stephen, 2026-10-24): you walked
into the side of a building (car 1) or the car simply wasn't there while
Teru stood by it (car 2). Both cars are background metatiles sharing one
set of tiles; only the palette differs (the town CHR bank 1 has 25 free
tiles, two separate designs would need 42):

- car 1 (the red car, scene 2E8): bottom-right bay, block $2D (used only
  here) edited in place. Map palette 2 (red-brown / brown / dark blue by
  time of day, like its scene picture). The car is solid; the scene opens
  from the three squares beside it (right half of the next bay), which
  become door squares with door-table entries. (A door only fires when you
  step onto it, so solid car squares can't be doors, and walkable ones
  left the party standing on the car after Leave.)
- car 2 (the black Skyline, Teru's scene 2F3): bottom-left bay, only while
  flag $7B is set (Teru Sneak 388 sets it, 210 / 0B1 clear it). Spare
  block $1C (unused in the town's rows, written by no code) = block $2C with the car; a hook next to the game's own
  flag-based map patches ($CAA0, after the map is copied to RAM) writes it
  over block ($10, $17). Map palette 0 (charcoal / brown / dark blue).
  Solid, so the party can't walk over it.

Map facts (PLAN.md "Car park cars"): the map grid in bank 0 at $800F is
$18 x $2C blocks, shared by areas 0-2 (area 0 rows 0-7, town = area 1
rows $C-$1B, area 2 below); each area reads it with its own tables. Area 1: block defs $8827 (16 metatiles each, $48 blocks); metatile tiles
$8CA7 (4 each, $E6 metatiles); attributes $A8D2 (bit $20 door, bit $10
solid, low bits palette). In RAM the map is at $6800 (3-byte header).
"""
BANK = 0x4000
MAP, W, H = 0x800F, 0x18, 0x2C
TOWN_ROWS = range(0x08, 0x1C)   # rows the town camera can show (incl. the road)
BLOCKS, METAS, ATTRS = 0x8827, 0x8CA7, 0xA8D2
N_BLOCKS, N_METAS = 0x48, 0xE6
CHR_BANK = 1                      # town background tiles (area n uses bank n)
DOOR_SCENE = 0x2E8
FLAG_TERU = 0x7B
AREA = 1

CAR1_BLOCK, CAR1_COLS = 0x2D, (2, 3)           # block-local metatile columns
CAR1_ORIGIN = (0x46, 0x5C)                      # map metatile of its top-left
CAR1_ATTR = 0x12                                # solid, palette 2
DOOR_COL = 1                                    # block-local column beside the car
CAR2_BASE, CAR2_BLOCK, CAR2_COLS = 0x2C, 0x1C, (0, 1)
CAR2_AT = (0x10, 0x17)                          # map block replaced
CAR2_ATTR = 0x10                                # solid, palette 0

HOOK_AT = 0xCAA0                  # LDA $71B2 (start of the $B2 map patch)
HELPER = 0xFCC0                   # free fixed-bank space after the credits

# 32x48 car, nose towards the viewer, symmetric (left half mirrored).
# o outline, b body, g glass, h highlight, w wheel, l headlight,
# r roof edge, s bonnet stripe, . tarmac
_HALF = [
    "................", "................", "......oooooooooo", ".....obbbbbbbbbb",
    "....obhhhhhhhhhh", "....obbbbbbbbbbb", "...wobbggggggggg", "...wobgggggggggg",
    "...wobgggggggggg", "...wobgggggggggg", "...wobbggggggggg", "....obbbbbbbbbbb",
    "....obrbbbbbbbbb", "....obrbbbbbbbbb", "....obrbbbbbbbbb", "....obrbbbbbbbbb",
    "....obrbbbbbbbbb", "....obrbbbbbbbbb", "....obrbbbbbbbbb", "....obrbbbbbbbbb",
    "....obbbbbbbbbbb", "...oobgggggggggg", "...oobgggggggggg", "....obgggggggggg",
    "....obgggggggggg", "....obgggggggggg", "....obbggggggggg", "....obbbbbbbbbbb",
    "....obbbbbbbbbbs", "...wobbbbbbbbbbs", "...wobbbbbbbbbbs", "...wobbbbbbbbbbs",
    "...wobbbbbbbbbbs", "...wobbbbbbbbbbs", "....obbbbbbbbbbb", "....obbbbbbbbbbb",
    "....oooooooooooo", "....ollllogogogo", "....ollllogogogo", "....oooooooooooo",
    ".....obbbbbbbbbb", "......oooooooooo",
] + ["................"] * 6
ART = [h + h[::-1] for h in _HALF]
for _x, _y in ((9, 8), (10, 9), (22, 23), (23, 22), (24, 21)):     # glass glints
    _r = list(ART[_y]); _r[_x] = 'h'; ART[_y] = ''.join(_r)
COLOUR = {'.': 2, 'o': 0, 'b': 1, 'g': 0, 'h': 3, 'w': 0, 'l': 3, 'r': 3, 's': 3}


def _b0(prg, a):
    return prg[a - 0x8000]


def _tile_bytes(px):
    """64 colour indices (rows) -> 16 bytes of NES 2bpp."""
    lo = bytes(sum(((px[y * 8 + x] & 1) << (7 - x)) for x in range(8)) for y in range(8))
    hi = bytes(sum(((px[y * 8 + x] >> 1) << (7 - x)) for x in range(8)) for y in range(8))
    return lo + hi


def car_tiles():
    """-> 6x4 grid (rows, cols) of 16-byte tiles."""
    grid = []
    for ty in range(6):
        row = []
        for tx in range(4):
            row.append(_tile_bytes([COLOUR[ART[ty * 8 + y][tx * 8 + x]]
                                    for y in range(8) for x in range(8)]))
        grid.append(row)
    return grid


def used_metatiles(bank0):
    used = set()
    for blk in range(N_BLOCKS):
        for i in range(16):
            used.add(_b0(bank0, BLOCKS + blk * 16 + i))
    return {m for m in used if m < N_METAS}


def town_blocks(bank0):
    """Block ids in the rows the town (area 1) shows, row-major from TOWN_ROWS[0]."""
    return [_b0(bank0, MAP + by * W + bx) for by in TOWN_ROWS for bx in range(W)]


def apply(new, chr_):
    """Edit bank 0 (map) and CHR bank 1 in place; return extra door
    entries [(area, x, y, scene lo, scene hi, flag)] for car 1."""
    bank0 = new[0:BANK]
    blocks = town_blocks(bank0)
    assert blocks.count(CAR1_BLOCK) == 1 and blocks.count(CAR2_BASE) == 1
    assert CAR2_BLOCK not in blocks
    assert _b0(bank0, MAP + CAR2_AT[1] * W + CAR2_AT[0]) == CAR2_BASE
    used_mt = used_metatiles(bank0)
    # tiles: reuse identical existing tiles, else take free ones
    cb = CHR_BANK * 0x1000
    existing = {}
    used_tiles = set()
    for m in used_mt:
        for q in range(4):
            used_tiles.add(_b0(bank0, METAS + m * 4 + q))
    for t in sorted(used_tiles):
        existing.setdefault(bytes(chr_[cb + t * 16:cb + t * 16 + 16]), t)
    free = [t for t in range(256) if t not in used_tiles]
    grid = car_tiles()
    ids = []
    for row in grid:
        r = []
        for data in row:
            if data not in existing:
                t = free.pop(0)
                chr_[cb + t * 16:cb + t * 16 + 16] = data
                existing[data] = t
            r.append(existing[data])
        ids.append(r)
    # metatiles: 6 for car 1, 6 for car 2 (same tiles, other attribute)
    free_mt = [m for m in range(N_METAS) if m not in used_mt]
    def make(attr):
        out = []
        for my in range(3):
            row = []
            for mx in range(2):
                m = free_mt.pop(0)
                tl = [ids[my * 2][mx * 2], ids[my * 2][mx * 2 + 1],
                      ids[my * 2 + 1][mx * 2], ids[my * 2 + 1][mx * 2 + 1]]
                new[METAS - 0x8000 + m * 4:METAS - 0x8000 + m * 4 + 4] = bytes(tl)
                new[ATTRS - 0x8000 + m] = attr
                row.append(m)
            out.append(row)
        return out
    car1, car2 = make(CAR1_ATTR), make(CAR2_ATTR)
    # door squares beside car 1: copies of the bay metatiles with the door bit
    door_mt = {}
    for my in range(3):
        a = BLOCKS - 0x8000 + CAR1_BLOCK * 16 + my * 4 + DOOR_COL
        orig = new[a]
        if orig not in door_mt:
            m = free_mt.pop(0)
            new[METAS - 0x8000 + m * 4:METAS - 0x8000 + m * 4 + 4] = \
                new[METAS - 0x8000 + orig * 4:METAS - 0x8000 + orig * 4 + 4]
            new[ATTRS - 0x8000 + m] = new[ATTRS - 0x8000 + orig] | 0x20
            door_mt[orig] = m
        new[a] = door_mt[orig]
    # car 1: edit its block in place
    for my in range(3):
        for k, col in enumerate(CAR1_COLS):
            new[BLOCKS - 0x8000 + CAR1_BLOCK * 16 + my * 4 + col] = car1[my][k]
    # car 2: spare block = base block with the car
    base = bytearray(new[BLOCKS - 0x8000 + CAR2_BASE * 16:BLOCKS - 0x8000 + CAR2_BASE * 16 + 16])
    for my in range(3):
        for k, col in enumerate(CAR2_COLS):
            base[my * 4 + col] = car2[my][k]
    new[BLOCKS - 0x8000 + CAR2_BLOCK * 16:BLOCKS - 0x8000 + CAR2_BLOCK * 16 + 16] = base
    # door entries for the squares beside car 1 (the original ($47, $5E) is
    # now under the solid car and can't be entered)
    x0, y0 = CAR1_ORIGIN
    doors = [bytes([AREA, x0 - 1, y0 + dy, DOOR_SCENE & 0xFF, DOOR_SCENE >> 8, 0x80])
             for dy in range(3)]
    return doors, {'car tiles': len({t for r in ids for t in r}), 'free tiles left': len(free),
                   'metatiles': [m for r in car1 + car2 for m in r]}


def apply_hook(fixed):
    """fixed = the fixed bank (bytearray, $C000-$FFFF)."""
    f = lambda a: a - 0xC000
    off = 3 + CAR2_AT[1] * W + CAR2_AT[0]
    code = bytes([
        0xAD, FLAG_TERU, 0x71,          # LDA $717B
        0xF0, 0x15,                     # BEQ done
        0xA5, 0x3F,                     # LDA $3F (area)
        0xC9, AREA,                     # CMP #1
        0xD0, 0x0F,                     # BNE done
        0xA9, off & 0xFF, 0x85, 0x12,   # map offset lo
        0xA9, off >> 8, 0x85, 0x13,     # map offset hi
        0xA9, CAR2_BLOCK, 0x85, 0x14,   # block
        0x20, 0xDE, 0xCA,               # JSR $CADE (write map[$12/$13] = $14)
        0xAD, 0xB2, 0x71,               # done: LDA $71B2 (the instruction replaced)
        0x60])                          # RTS
    done = len(code) - 4               # LDA $71B2
    assert code[4] == done - 5 and code[10] == done - 11
    at = f(HELPER)
    assert set(fixed[at:at + len(code)]) == {0xFF}, 'carpark helper space is taken'
    fixed[at:at + len(code)] = code
    assert bytes(fixed[f(HOOK_AT):f(HOOK_AT) + 3]) == bytes([0xAD, 0xB2, 0x71])
    fixed[f(HOOK_AT):f(HOOK_AT) + 3] = bytes([0x20, HELPER & 0xFF, HELPER >> 8])
