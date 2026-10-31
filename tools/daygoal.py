"""Day goal (Stephen, 2026-10-31; PLAN.md "Day goal").

The ending plays its quicker version only if the day counter `$71C8`
is below `$E745[hero]` (9 for Hiroshi, 8 for Toru; hero = `$71B5`). In a
scene, Select now swaps the status panel's LUCK label and grade for

    GOAL        row 9 (LUCK's place), black
    DAY3/8      row 11 (the grade's place): shown day = counter + 1
    14:05       row 12, 24-hour clock ($71C6 hour, $71C5 ticks, 56 an hour)

and back. Once the target is missed the day line drops the "/8" (DAY12,
up to DAY256) and the day and time turn pink with a black shadow, like
the grades; GOAL stays black.

Hooks (fixed bank, in the free run after carpark's helper):
- `$EA4A` JSR $EC22 (the verb menu's frame wait) -> JSR T_MENU: the wait,
  then the bank-11 routine with Y=0 (Select edge -> toggle).
- `$EB6C` JSR $EB97 (start of the grade reprint, e.g. after a fortune
  slip or a new scene) -> JSR T_GRADE: the bank-11 routine with Y=1 (if
  shown: LUCK back, rows 11/12 blanked, state cleared), then $EB97.
The routine writes (PPU hi, lo, tile) triplets into the NMI buffer at
$02C4 (`$64` = bytes used) and flushes with $EC16, as text printing does.
State lives in save RAM page $76xx, which the original never touches.

Glyphs: new black and pink tiles in font CHR banks 30/31, from the
status panel's spare slots (status.py's label and grade sets).
"""
import font
import status

CODE_BANK = 11
CODE = 0x8000
TRAMP = 0xFCDE                 # free fixed-bank run up to the text lookup at $FD00
TRAMP_END = 0xFD00
MENU_HOOK, GRADE_HOOK = 0xEA4A, 0xEB6C
EC22, EB97, EB6C, EC16, C049 = 0xEC22, 0xEB97, 0xEB6C, 0xEC16, 0xC049
DAY, HOUR, TICKS, HERO, TARGETS = 0x71C8, 0x71C6, 0x71C5, 0x71B5, 0xE745
BUTTONS, SELECT = 0x82, 0x20
BUF, BUF_USED = 0x02C4, 0x64
ROW_LABEL, ROW_DAY, ROW_TIME = 0x22, 0x62, 0x82     # PPU $21xx, column 2
WIDTH = 6
BLANK = status.BLANK

# save RAM scratch
SHOWN, PREV, TMP, COL, H, T, O = 0x7600, 0x7601, 0x7602, 0x7603, 0x7604, 0x7605, 0x7606
ROW = 0x7608                   # 6 tiles

BLACK_CHARS = 'GOADY0123456789/:'      # L is already a label tile
PINK_CHARS = 'Y0123456789/:'           # D, A are already grade tiles
# digit table layout per colour: 0-9, '/', ':', 'D', 'A', 'Y'
TABLE_CHARS = '0123456789/:DAY'
PINK_OFFSET = 16


def tile_maps():
    """-> (black {char: tile}, pink {char: tile})"""
    lab, grd = status.label_map(), status.grade_map()
    free_label = [t for t in status.LABEL_TILES if t not in lab.values()]
    free_grade = [t for t in status.GRADE_TILES if t not in grd.values()]
    pool = free_label + free_grade
    black = {'L': lab['L']}
    for c in BLACK_CHARS:
        black[c] = pool.pop(0)
    pink = {'D': grd['D'], 'A': grd['A']}
    for c in PINK_CHARS:
        pink[c] = pool.pop(0)
    return black, pink


def apply_chr(chr_):
    glyphs = {ch: rows for ch, (_, rows) in font.build().items()}
    black, pink = tile_maps()
    for m, style in ((black, status.LABEL_STYLE), (pink, status.GRADE_STYLE)):
        for ch, tile in m.items():
            data = status._tile(glyphs[ch], style)
            for cb in status.FONT_CHR_BANKS:
                o = cb * 0x1000 + tile * 16
                chr_[o:o + 16] = data


# --- a small 6502 assembler (just the modes used here) ---
OPS = {
    ('LDA', 'imm'): 0xA9, ('LDA', 'zp'): 0xA5, ('LDA', 'abs'): 0xAD,
    ('LDA', 'absx'): 0xBD, ('LDA', 'absy'): 0xB9,
    ('STA', 'abs'): 0x8D, ('STA', 'absx'): 0x9D, ('STA', 'absy'): 0x99,
    ('LDX', 'imm'): 0xA2, ('LDY', 'imm'): 0xA0, ('LDY', 'zp'): 0xA4, ('LDY', 'abs'): 0xAC,
    ('STY', 'zp'): 0x84, ('STX', 'abs'): 0x8E, ('LDX', 'abs'): 0xAE,
    ('CMP', 'imm'): 0xC9, ('CMP', 'abs'): 0xCD, ('CPX', 'imm'): 0xE0, ('CPY', 'imm'): 0xC0,
    ('AND', 'imm'): 0x29, ('EOR', 'imm'): 0x49, ('ADC', 'imm'): 0x69, ('ADC', 'abs'): 0x6D,
    ('SBC', 'imm'): 0xE9, ('INC', 'abs'): 0xEE,
    ('INX', ''): 0xE8, ('INY', ''): 0xC8, ('TAX', ''): 0xAA, ('TAY', ''): 0xA8, ('TXA', ''): 0x8A,
    ('CLC', ''): 0x18, ('SEC', ''): 0x38, ('RTS', ''): 0x60, ('PHA', ''): 0x48, ('PLA', ''): 0x68,
    ('JMP', 'abs'): 0x4C, ('JSR', 'abs'): 0x20,
}
BRANCH = {'BEQ': 0xF0, 'BNE': 0xD0, 'BCC': 0x90, 'BCS': 0xB0}
SIZE = {'': 1, 'imm': 2, 'zp': 2, 'abs': 3, 'absx': 3, 'absy': 3}


def assemble(base, prog):
    """prog: labels (str) and tuples (op, mode, value); a value may be
    a label name, or 'label+n'."""
    labels, pc = {}, base
    for item in prog:
        if isinstance(item, str):
            labels[item] = pc
        elif item[0] == '.db':
            pc += len(item[1])
        else:
            pc += 2 if item[0] in BRANCH else SIZE[item[1]]
    out = bytearray()
    for item in prog:
        if isinstance(item, str):
            continue
        if item[0] == '.db':
            out += bytes(item[1])
            continue
        op, mode, val = (item + (None,))[:3]
        if isinstance(val, str):
            name, _, n = val.partition('+')
            val = labels[name] + int(n or 0)
        if op in BRANCH:
            d = val - (base + len(out) + 2)
            assert -128 <= d <= 127, (op, val)
            out += bytes([BRANCH[op], d & 0xFF])
        else:
            out.append(OPS[(op, mode)])
            if SIZE[mode] == 2:
                out.append(val & 0xFF)
            elif SIZE[mode] == 3:
                out += bytes([val & 0xFF, val >> 8])
    return bytes(out), labels


def routine():
    black, pink = tile_maps()
    lab = status.label_map()
    table = [black[c] for c in TABLE_CHARS] + [BLANK] * (PINK_OFFSET - len(TABLE_CHARS))
    table += [pink[c] for c in TABLE_CHARS]
    minutes = [min(t * 60 // 56, 59) for t in range(64)]

    def fill(tiles):                       # ROW = constant tiles
        return [x for i, t in enumerate(tiles) for x in (('LDA', 'imm', t), ('STA', 'abs', ROW + i))]

    def letters():                         # ROW[0..2] = D A Y in colour COL
        return [('LDY', 'abs', COL),
                ('LDA', 'absy', 'table+12'), ('STA', 'abs', ROW),
                ('LDA', 'absy', 'table+13'), ('STA', 'abs', ROW + 1),
                ('LDA', 'absy', 'table+14'), ('STA', 'abs', ROW + 2)]

    word = lambda s, m: [m[c] if c != ' ' else BLANK for c in s.ljust(WIDTH)]
    prog = [
        ('CPY', 'imm', 0), ('BEQ', None, 'menu'),
        # --- Y=1: the grade is about to be reprinted ---
        ('LDA', 'abs', SHOWN), ('BEQ', None, 'rts'),
        ('LDA', 'imm', 0), ('STA', 'abs', SHOWN),
        ('JMP', 'abs', 'restore'),
        # --- Y=0: verb menu frame ---
        'menu',
        ('LDA', 'zp', BUTTONS), ('AND', 'imm', SELECT),
        ('CMP', 'abs', PREV), ('BEQ', None, 'rts'),
        ('STA', 'abs', PREV), ('TAX', ''), ('BEQ', None, 'rts'),     # released
        ('LDA', 'abs', SHOWN), ('EOR', 'imm', 1), ('STA', 'abs', SHOWN),
        ('BNE', None, 'show'),
        ('JSR', 'abs', 'restore'),
        ('JMP', 'abs', EB6C),                                       # grade back
        'rts', ('RTS', ''),

        'restore',                                                  # LUCK, blank rows
        *fill(word('LUCK', lab)), ('LDA', 'imm', ROW_LABEL), ('JSR', 'abs', 'emit'),
        *fill([BLANK] * WIDTH), ('LDA', 'imm', ROW_DAY), ('JSR', 'abs', 'emit'),
        *fill([BLANK] * WIDTH), ('LDA', 'imm', ROW_TIME), ('JMP', 'abs', 'emit'),

        'show',
        *fill(word('GOAL', black)), ('LDA', 'imm', ROW_LABEL), ('JSR', 'abs', 'emit'),
        ('LDY', 'abs', HERO), ('LDA', 'absy', TARGETS), ('STA', 'abs', TMP),
        ('LDA', 'abs', DAY), ('CMP', 'abs', TMP), ('BCS', None, 'late'),
        # on target: DAYd/t, black (d = counter + 1 <= 9)
        ('LDA', 'imm', 0), ('STA', 'abs', COL),
        *letters(),
        ('LDX', 'imm', 3),
        ('LDA', 'abs', DAY), ('CLC', ''), ('ADC', 'imm', 1), ('JSR', 'abs', 'put'),
        ('LDA', 'imm', 10), ('JSR', 'abs', 'put'),
        ('LDA', 'abs', TMP), ('JSR', 'abs', 'put'),
        ('JMP', 'abs', 'dayrow'),
        'late',                                                     # DAYn, pink
        ('LDA', 'imm', PINK_OFFSET), ('STA', 'abs', COL),
        *letters(),
        ('LDA', 'imm', BLANK), ('STA', 'abs', ROW + 3), ('STA', 'abs', ROW + 4), ('STA', 'abs', ROW + 5),
        ('LDA', 'abs', DAY),                                        # counter -> H T O
        ('LDX', 'imm', 0),
        'h', ('CMP', 'imm', 100), ('BCC', None, 'h_done'), ('SBC', 'imm', 100), ('INX', ''), ('BNE', None, 'h'),
        'h_done', ('STX', 'abs', H),
        ('JSR', 'abs', 'tens'), ('STX', 'abs', T), ('STA', 'abs', O),
        # + 1 (decimal)
        ('INC', 'abs', O), ('LDA', 'abs', O), ('CMP', 'imm', 10), ('BNE', None, 'inc_done'),
        ('LDA', 'imm', 0), ('STA', 'abs', O), ('INC', 'abs', T),
        ('LDA', 'abs', T), ('CMP', 'imm', 10), ('BNE', None, 'inc_done'),
        ('LDA', 'imm', 0), ('STA', 'abs', T), ('INC', 'abs', H),
        'inc_done',
        ('LDX', 'imm', 3),
        ('LDA', 'abs', H), ('BEQ', None, 'no_h'), ('JSR', 'abs', 'put'),
        ('LDA', 'abs', T), ('JMP', 'abs', 'do_t'),
        'no_h', ('LDA', 'abs', T), ('BEQ', None, 'do_o'),
        'do_t', ('JSR', 'abs', 'put'),
        'do_o', ('LDA', 'abs', O), ('JSR', 'abs', 'put'),
        'dayrow',
        ('LDA', 'imm', ROW_DAY), ('JSR', 'abs', 'emit'),
        # time HH:MM in the same colour
        ('LDA', 'abs', HOUR), ('JSR', 'abs', 'tens'),               # X = tens, A = ones
        ('PHA', ''), ('TXA', ''),
        ('LDX', 'imm', 0), ('JSR', 'abs', 'put'),
        ('PLA', ''), ('JSR', 'abs', 'put'),
        ('LDA', 'imm', 11), ('JSR', 'abs', 'put'),
        ('LDA', 'abs', TICKS), ('AND', 'imm', 0x3F), ('TAY', ''), ('LDA', 'absy', 'minutes'),
        ('STX', 'abs', TMP),
        ('JSR', 'abs', 'tens'),
        ('PHA', ''), ('TXA', ''),
        ('LDX', 'abs', TMP), ('JSR', 'abs', 'put'),
        ('PLA', ''), ('JSR', 'abs', 'put'),
        ('LDA', 'imm', BLANK), ('STA', 'abs', ROW + 5),
        ('LDA', 'imm', ROW_TIME), ('JMP', 'abs', 'emit'),

        # put: ROW[X] = table[COL + A]; X += 1
        'put', ('CLC', ''), ('ADC', 'abs', COL), ('TAY', ''), ('LDA', 'absy', 'table'),
        ('STA', 'absx', ROW), ('INX', ''), ('RTS', ''),
        # tens: A -> X = A / 10, A = A % 10
        'tens', ('LDX', 'imm', 0),
        't_loop', ('CMP', 'imm', 10), ('BCC', None, 't_done'), ('SBC', 'imm', 10), ('INX', ''), ('BNE', None, 't_loop'),
        't_done', ('RTS', ''),
        # emit: row A (PPU $21xx) <- ROW[0..5], then flush
        'emit', ('STA', 'abs', TMP), ('LDX', 'imm', 0), ('LDY', 'zp', BUF_USED),
        'e_loop', ('LDA', 'imm', 0x21), ('STA', 'absy', BUF),
        ('LDA', 'abs', TMP), ('STA', 'absy', BUF + 1), ('INC', 'abs', TMP),
        ('LDA', 'absx', ROW), ('STA', 'absy', BUF + 2),
        ('INY', ''), ('INY', ''), ('INY', ''), ('INX', ''), ('CPX', 'imm', WIDTH), ('BNE', None, 'e_loop'),
        ('STY', 'zp', BUF_USED), ('JMP', 'abs', EC16),
        'table', ('.db', table),
        'minutes', ('.db', minutes),
    ]
    return prog


def build():
    """-> (bank-11 code, fixed-bank trampolines, [(addr, was, now)])"""
    code, _ = assemble(CODE, routine())
    tramp, tl = assemble(TRAMP, [
        'menu', ('JSR', 'abs', EC22), ('LDY', 'imm', 0), ('BEQ', None, 'call'),
        'grade', ('LDY', 'imm', 1), ('JSR', 'abs', 'call'), ('JMP', 'abs', EB97),
        'call', ('LDA', 'zp', 0x7C), ('PHA', ''), ('LDA', 'imm', CODE_BANK), ('JSR', 'abs', C049),
        ('JSR', 'abs', CODE), ('PLA', ''), ('JMP', 'abs', C049),
    ])
    assert TRAMP + len(tramp) <= TRAMP_END, hex(TRAMP + len(tramp))
    patches = [(MENU_HOOK, bytes([0x20, EC22 & 0xFF, EC22 >> 8]),
                bytes([0x20, tl['menu'] & 0xFF, tl['menu'] >> 8])),
               (GRADE_HOOK, bytes([0x20, EB97 & 0xFF, EB97 >> 8]),
                bytes([0x20, tl['grade'] & 0xFF, tl['grade'] >> 8]))]
    return code, tramp, patches


def apply(new, chr_, bank_size=0x4000, fixed_bank=15):
    code, tramp, patches = build()
    o = CODE_BANK * bank_size
    assert new[o:o + len(code)] == b'\xFF' * len(code)
    new[o:o + len(code)] = code
    fx = fixed_bank * bank_size - 0xC000
    assert new[fx + TRAMP:fx + TRAMP + len(tramp)] == b'\xFF' * len(tramp)
    new[fx + TRAMP:fx + TRAMP + len(tramp)] = tramp
    for addr, was, now in patches:
        assert new[fx + addr:fx + addr + len(was)] == was, hex(addr)
        new[fx + addr:fx + addr + len(now)] = now
    apply_chr(chr_)
    return {'code bytes': len(code), 'trampoline bytes': len(tramp)}
