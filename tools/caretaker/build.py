"""Put the caretaker's room into the ROM (optional help, PLAN.md).

The building just south of Aitoku High (town = area 1) gets an open door;
walking in opens a scene: new picture $25 (the room, CHR bank 29) with a
new animated character $38 (the caretaker, sprites from CHR bank 6) and
the Talk / Leave menu. Talk gives the help pages (tools/additions.py).

What changes (all original data is checked before it is overwritten):
  - PRG bank 0: unused town block $3D becomes building block $0F with the
    open doorway ($50/$5A, as on the school) instead of the shut door
    ($4A/$4B); the map cell at block (5,$12) points to it.
  - Fixed bank: the door table ($EF97, 6-byte entries, $FF end) is copied
    to free space with the new door added, and its scan ($C51E) repointed.
  - Fixed bank hooks, each a JMP that falls back to the original code:
      $EC7A picture CHR bank, $EC98 picture layout, $D2D3 palette,
      $F8AC character record, $F92C character data bank,
      $DBEE message lookup: the sign-off ID becomes one of four variants,
      picked by the frame counter $6E.
  - PRG bank 14 (spare): the room layout and the caretaker record.
  - CHR bank 29: room tiles in tiles the credits don't use, plus the
    picture-frame tiles $02/$07/$2A and the blank $00 (the loader clears
    the picture area with it first) copied from bank 10.
  - CHR bank 6: caretaker tiles in tiles no bank-6 picture references,
    plus the sprite tiles every character bank shares ($F6-$FE). Four
    bank-6 picture tiles sat there; they move to free tiles and those
    pictures' layouts (PRG bank 1) are repointed.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import char     # noqa: E402
import room     # noqa: E402
import credits  # noqa: E402
import additions  # noqa: E402

BANK = 0x4000
FIXED = 15
DATA_BANK = 14
FIRST_PIC = 0x25               # new pictures from here (originals: $00-$24)
PIC = 0x25                     # the caretaker's room
CHAR_ID = 0x38                 # new character (originals: $00-$37)
ROOM_CHR, CHAR_CHR = 29, 6
FRAME_SRC_CHR = 10             # a picture bank to copy the frame tiles from
SCENE_FRAME = (0x00, 0x02, 0x07, 0x2A, 0xBB, 0xFF)   # + the blank $00 the loader clears with
# Sprite tiles every scene takes from the character's CHR bank: $19 is
# sprite 0 (the mid-screen split, must stay opaque); $F6-$FE are identical
# in every original character bank (speech-bubble tail $F6-$FB, menu
# highlight $FE = solid colour 3, ...), so they are copied in from bank 16.
# ($FF differs: blank there, a solid frame tile here; only hidden sprites
# use it.)
SPRITE_0 = 0x19
SHARED_SPRITES = range(0xF6, 0xFF)
SHARED_SRC_CHR = 16

LAYOUT_ADDR = 0x8000           # in DATA_BANK
RECORD_ADDR = 0x8140
PICTURES_ADDR = 0x8400         # other new pictures' layouts and palettes
CODE_ADDR = 0xFD50             # free fixed-bank space after the text lookup

# town map (PRG bank 0): blocks at $8827, map at $800F, $18 blocks wide
BLOCKS, MAP, MAP_W = 0x0827, 0x000F, 0x18
SHUT_BLOCK, OPEN_BLOCK = 0x0F, 0x3D
CELL = (5, 0x12)
DOOR = (0x01, 0x14, 0x4B)      # area, metatile x, y of the doorway ($5A)

DOOR_TABLE = 0xEF97


def lo(a): return a & 0xFF
def hi(a): return a >> 8


def _2bpp(pix):
    """64 colour indices (0-3) -> 16 CHR bytes."""
    lo_ = bytes(sum((pix[y * 8 + x] & 1) << (7 - x) for x in range(8)) for y in range(8))
    hi_ = bytes(sum((pix[y * 8 + x] >> 1) << (7 - x) for x in range(8)) for y in range(8))
    return lo_ + hi_


def _picture_tiles_used(prg, chr_bank):
    """Tiles of chr_bank referenced by any original picture layout."""
    f = prg[FIXED * BANK:]
    chrs = f[0xED2E - 0xC000:0xED2E - 0xC000 + 37]
    idx = f[0xED53 - 0xC000:0xED53 - 0xC000 + 37]
    b1 = prg[1 * BANK:2 * BANK]
    used = set()
    for p in range(37):
        if chrs[p] == chr_bank:
            used |= set(b1[idx[p] * 0x130:idx[p] * 0x130 + 280])
    return used


def room_data(chr_, used):
    """-> (304-byte layout, {tile: chr bytes}) for the room in ROOM_CHR."""
    pc = room.draw()
    bl, bad = room.blocks(pc)
    assert not bad, bad
    pats = room.tiles(pc, bl)
    free = [t for t in range(256) if t not in used and t not in SCENE_FRAME]
    tiles, layout = {}, []
    for p in pats:
        if p not in tiles:
            tiles[p] = free.pop(0)
        layout.append(tiles[p])
    # attributes: picture block (bx,by) sits at screen tiles (6+2bx, 14+2by)
    attr = [0xFF] * 24                        # quadrants outside: palette 3
    for by in range(7):
        for bx in range(10):
            col, row = 6 + 2 * bx, 14 + 2 * by
            i = (col // 4 - 1) + 6 * (row // 4 - 3)
            shift = 2 * (((col % 4) // 2) + 2 * ((row % 4) // 2))
            attr[i] = (attr[i] & ~(3 << shift)) | (bl[by][bx] << shift)
    return bytes(layout) + bytes(attr), {t: _2bpp(p) for p, t in tiles.items()}


def palette_record():
    """3 x 13 bytes (morning/evening/night, chosen by $71B9): bg + 4
    palettes x 3; palette 3 is the dialogue's. Evening and night are
    tinted like the school corridor."""
    rec = b''
    for pals in (room.PALS, room.EVENING_PALS, room.NIGHT_PALS):
        rec += bytes([0x0F]) + bytes(c for p in pals for c in p) + bytes([0x20, 0x36, 0x21])
    return rec


def char_data(free):
    """-> (record bytes at RECORD_ADDR, {tile: chr bytes}) for CHAR_CHR.
    Mirror-image cells share a tile through the sprite flip bits."""
    base = char.cells(char.build(False))
    talk = char.cells(char.build(True))
    pal_no = {'A': 0, 'B': 1, 'C': 2}
    tiles = {}

    def tile_of(idx):
        key = tuple(v for row in idx for v in row)
        hflip = tuple(v for row in idx for v in reversed(row))
        vflip = tuple(v for row in reversed(idx) for v in row)
        hvflip = tuple(v for row in reversed(idx) for v in reversed(row))
        for k, attr in ((key, 0x00), (hflip, 0x40), (vflip, 0x80), (hvflip, 0xC0)):
            if k in tiles:
                return tiles[k], attr
        tiles[key] = free.pop(0)
        return tiles[key], 0x00

    def frame(cs):
        out = bytearray([0x00])
        for (c, r), (pal, idx) in sorted(cs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            t, flip = tile_of(idx)
            out += bytes([(r + 3) * 12 + (c + 2), pal_no[pal] | flip, t])
        return out + b'\xFF'

    f0 = frame(base)
    f1 = frame({k: v for k, v in talk.items() if base.get(k) != v})
    rec = bytearray([CHAR_CHR, 0, 0, 0, 0])
    for p in 'ABC':
        rec += bytes(char.PALS[p])
    a0 = RECORD_ADDR + len(rec) + 4
    a1 = a0 + len(f0)
    rec += bytes([lo(a0), hi(a0), lo(a1), hi(a1)]) + f0 + f1
    return bytes(rec), {t: _2bpp(k) for k, t in tiles.items()}


def door_table(fixed, scene_id, extra=()):
    o = DOOR_TABLE - 0xC000
    end = o
    while fixed[end] != 0xFF:
        end += 6
    entry = bytes(DOOR) + bytes([lo(scene_id), hi(scene_id), 0x80])
    return bytes(fixed[o:end]) + entry + b''.join(extra) + b'\xFF'


def hooks(base, table_addr, tabs):
    """-> (code, [(addr, original bytes, new bytes)]) for the fixed bank."""
    code = bytearray()
    patches = []

    def jmp(at, was):
        here = base + len(code)
        patches.append((at, bytes(was), bytes([0x4C, lo(here), hi(here)])))

    # New pictures $25.. come from tables (CHR bank, layout and palette
    # record addresses in DATA_BANK); originals fall through unchanged.
    # $EC7A PHA / TAY / LDX $ED2E,Y -> picture CHR bank
    jmp(0xEC7A, [0x48, 0xA8, 0xBE])
    code += bytes([0x48, 0xA8,                            # PHA / TAY
                   0xC0, FIRST_PIC, 0xB0, 0x06,           # CPY #first / BCS new
                   0xBE, 0x2E, 0xED, 0x4C, 0x7F, 0xEC,    # LDX $ED2E,Y / JMP $EC7F
                   0xBE, lo(tabs['chr'] - FIRST_PIC), hi(tabs['chr'] - FIRST_PIC),
                   0x4C, 0x7F, 0xEC])                     # new: LDX chr,Y / JMP $EC7F
    # $EC98 LDA $ED53,Y -> picture layout (bank, address)
    jmp(0xEC98, [0xB9, 0x53, 0xED])
    code += bytes([0xC0, FIRST_PIC, 0xB0, 0x06,           # CPY #first / BCS mine
                   0xB9, 0x53, 0xED, 0x4C, 0x9B, 0xEC,    # LDA $ED53,Y / JMP $EC9B
                   0xB9, lo(tabs['laylo'] - FIRST_PIC), hi(tabs['laylo'] - FIRST_PIC),
                   0x85, 0x0E,                            # mine: $0E/$0F = layout
                   0xB9, lo(tabs['layhi'] - FIRST_PIC), hi(tabs['layhi'] - FIRST_PIC),
                   0x85, 0x0F,
                   0xA5, 0x7C, 0x48,                      # LDA $7C / PHA (restored at $ED1D)
                   0xA9, DATA_BANK, 0x20, 0x49, 0xC0,     # LDA #bank / JSR $C049
                   0x4C, 0xBB, 0xEC])                     # JMP $ECBB
    # $D2D3 STA $12 / LDA #$27 -> palette record (originals use records
    # $00-$2A only: pictures $00-$24 + 6, street areas 0-5)
    first_pal = FIRST_PIC + 6
    jmp(0xD2D3, [0x85, 0x12, 0xA9])
    code += bytes([0xC9, first_pal, 0xB0, 0x07,           # CMP #first / BCS mine
                   0x85, 0x12, 0xA9, 0x27, 0x4C, 0xD7, 0xD2,
                   0xA8,                                  # mine: TAY
                   0xB9, lo(tabs['pallo'] - first_pal), hi(tabs['pallo'] - first_pal),
                   0x85, 0x00,                            # ($00) = record in DATA_BANK
                   0xB9, lo(tabs['palhi'] - first_pal), hi(tabs['palhi'] - first_pal),
                   0x85, 0x01,
                   0xA5, 0x7C, 0x48,                      # LDA $7C / PHA
                   0xA9, DATA_BANK, 0x20, 0x49, 0xC0,     # LDA #bank / JSR $C049
                   0x20, 0xEB, 0xD2,                      # JSR $D2EB (adds time of day)
                   0x68, 0x4C, 0x49, 0xC0])               # PLA / JMP $C049
    # $F8AC LDA $7006 -> character record
    jmp(0xF8AC, [0xAD, 0x06, 0x70])
    code += bytes([0xAD, 0x06, 0x70, 0xC9, CHAR_ID, 0xF0, 0x05,
                   0xC9, 0x34, 0x4C, 0xB1, 0xF8,          # CMP #$34 / JMP $F8B1
                   0xA9, DATA_BANK, 0x20, 0x49, 0xC0,     # mine: select bank
                   0xA9, lo(RECORD_ADDR), 0x85, 0x06, 0x85, 0x95,
                   0xA9, hi(RECORD_ADDR), 0x85, 0x07, 0x85, 0x96,
                   0x4C, 0x05, 0xF9])                     # JMP $F905
    # $F92C LDA $7006 -> bank holding the character's frames
    jmp(0xF92C, [0xAD, 0x06, 0x70])
    code += bytes([0xAD, 0x06, 0x70, 0xC9, CHAR_ID, 0xD0, 0x05,
                   0xA9, DATA_BANK, 0x4C, 0x49, 0xC0,     # LDA #bank / JMP $C049
                   0x4C, 0x2F, 0xF9])                     # JMP $F92F
    # $DBEE JMP $FD00 (the message lookup) -> random sign-off variant
    sign, first = additions.CARETAKER_SIGNOFF, additions.SIGNOFF_FIRST
    assert len(additions.SIGNOFFS) == 4 and lo(first) + 3 <= 0xFF
    here = base + len(code)
    patches.append((0xDBEE, bytes([0x4C, 0x00, 0xFD]), bytes([0x4C, lo(here), hi(here)])))
    # Talk's sign-off ID -> SIGNOFFS 0/1, Ask's -> SIGNOFFS 2/3 (frame bit 0)
    ask = additions.ASK_SIGNOFF
    assert hi(ask) == hi(sign) == hi(first)
    code += bytes([0xC0, hi(sign), 0xD0, 23,              # CPY #hi / BNE go
                   0xE0, lo(sign), 0xF0, 8,               # CPX #talk / BEQ t
                   0xE0, lo(ask), 0xD0, 15,               # CPX #ask / BNE go
                   0xA2, lo(first) + 2, 0xD0, 2,          # LDX #first+2 / BNE p
                   0xA2, lo(first),                       # t: LDX #first
                   0xA5, 0x6E, 0x4A,                      # p: LDA $6E / LSR A
                   0x8A, 0x69, 0x00, 0xAA,                # TXA / ADC #0 / TAX
                   0xA0, hi(first),                       # LDY #hi(first)
                   0x4C, 0x00, 0xFD])                     # go: JMP $FD00
    # door table scan base: $C51E LDA #$97 ... $C524 LDA #$EF
    patches.append((0xC51E, bytes([0xA9, 0x97]), bytes([0xA9, lo(table_addr)])))
    patches.append((0xC524, bytes([0xA9, 0xEF]), bytes([0xA9, hi(table_addr)])))
    return bytes(code), patches


def apply(new, chr_, scene_id, extra=(), doors=()):
    """new = the expanded PRG (bytearray, 16 banks), chr_ = CHR ROM;
    extra = further new pictures [(number, CHR bank, layout, palette
    record)], numbered on from PIC."""
    # town map
    b = BLOCKS + SHUT_BLOCK * 16
    shut = bytes(new[b:b + 16])
    assert shut == bytes.fromhex('22231d1b4389895e4a89421b4b2a2a5f'), shut.hex()
    open_ = bytearray(shut)
    open_[8], open_[12] = 0x50, 0x5A
    new[BLOCKS + OPEN_BLOCK * 16:BLOCKS + OPEN_BLOCK * 16 + 16] = open_
    m = MAP + CELL[1] * MAP_W + CELL[0]
    assert new[m] == SHUT_BLOCK
    new[m] = OPEN_BLOCK

    fixed = FIXED * BANK
    f = lambda addr: fixed + addr - 0xC000
    # room picture (CHR bank 29) and frame tiles
    used = set(credits.USED)
    layout, rtiles = room_data(chr_, used)
    for t in SCENE_FRAME:
        src = (FRAME_SRC_CHR * 0x1000 + t * 16)
        chr_[ROOM_CHR * 0x1000 + t * 16:ROOM_CHR * 0x1000 + t * 16 + 16] = chr_[src:src + 16]
    for t, data in rtiles.items():
        chr_[ROOM_CHR * 0x1000 + t * 16:ROOM_CHR * 0x1000 + t * 16 + 16] = data
    # caretaker (CHR bank 6): first move the bank-6 picture tiles that sit
    # on shared sprite tiles to free tiles, and repoint those pictures
    pused = _picture_tiles_used(new, CHAR_CHR)
    assert SPRITE_0 in pused
    cfree = [t for t in range(256) if t not in pused and t not in SCENE_FRAME
             and t != SPRITE_0 and t not in SHARED_SPRITES]
    cb = CHAR_CHR * 0x1000
    moved = {}
    for t in SHARED_SPRITES:
        if t in pused:
            moved[t] = cfree.pop(0)
            chr_[cb + moved[t] * 16:cb + moved[t] * 16 + 16] = chr_[cb + t * 16:cb + t * 16 + 16]
    fx = new[FIXED * BANK:]
    chrs = fx[0xED2E - 0xC000:0xED2E - 0xC000 + 37]
    idxs = fx[0xED53 - 0xC000:0xED53 - 0xC000 + 37]
    for p in range(37):
        if chrs[p] == CHAR_CHR:
            o = 1 * BANK + idxs[p] * 0x130
            for i in range(280):
                if new[o + i] in moved:
                    new[o + i] = moved[new[o + i]]
    sb = SHARED_SRC_CHR * 0x1000
    for t in SHARED_SPRITES:
        chr_[cb + t * 16:cb + t * 16 + 16] = chr_[sb + t * 16:sb + t * 16 + 16]
    record, ctiles = char_data(cfree)
    for t, data in ctiles.items():
        chr_[cb + t * 16:cb + t * 16 + 16] = data
    # data bank
    d = DATA_BANK * BANK
    assert set(new[d:d + 0x2000]) == {0xFF}
    new[d + LAYOUT_ADDR - 0x8000:d + LAYOUT_ADDR - 0x8000 + len(layout)] = layout
    assert LAYOUT_ADDR + len(layout) <= RECORD_ADDR
    new[d + RECORD_ADDR - 0x8000:d + RECORD_ADDR - 0x8000 + len(record)] = record
    # new pictures: layouts and palette records in DATA_BANK
    pics = [(PIC, ROOM_CHR, layout, palette_record())] + list(extra)
    assert [p[0] for p in pics] == list(range(FIRST_PIC, FIRST_PIC + len(pics)))
    lay_addr, pal_addr = [], []
    a = PICTURES_ADDR
    for n, (num, bank, lay, pal) in enumerate(pics):
        if n == 0:
            lay_addr.append(LAYOUT_ADDR)
        else:
            new[d + a - 0x8000:d + a - 0x8000 + len(lay)] = lay
            lay_addr.append(a)
            a += len(lay)
        new[d + a - 0x8000:d + a - 0x8000 + len(pal)] = pal
        pal_addr.append(a)
        a += len(pal)
    assert a <= 0xBFF0
    # fixed bank: door table, picture tables, hooks
    table = door_table(new[fixed:fixed + BANK], scene_id, doors)
    table_addr = CODE_ADDR
    t = table_addr + len(table)
    tabs = {}
    blob_tabs = b''
    for name, vals in (('chr', [p[1] for p in pics]), ('laylo', [lo(x) for x in lay_addr]),
                       ('layhi', [hi(x) for x in lay_addr]), ('pallo', [lo(x) for x in pal_addr]),
                       ('palhi', [hi(x) for x in pal_addr])):
        tabs[name] = t
        blob_tabs += bytes(vals)
        t += len(vals)
    code_addr = t
    code, patches = hooks(code_addr, table_addr, tabs)
    blob = table + blob_tabs + code
    assert code_addr + len(code) <= additions.CHEAT_HELPER, hex(code_addr + len(code))
    assert set(new[f(CODE_ADDR):f(CODE_ADDR) + len(blob)]) == {0xFF}
    new[f(CODE_ADDR):f(CODE_ADDR) + len(blob)] = blob
    for at, was, now in patches:
        assert bytes(new[f(at):f(at) + len(was)]) == was, (hex(at), was.hex())
        new[f(at):f(at) + len(now)] = now
    return {'room tiles': len(rtiles), 'caretaker tiles': len(ctiles),
            'fixed bytes': len(blob), 'free fixed after': 0xFFD0 - (code_addr + len(code))}
