"""Title-screen version info (Stephen, 2026-11-05).

Left or Right on the title screen (both unused there) swaps the two
copyright lines for

     ENGLISH VERSION 1.0             row 25 (or DEV on a development build;
                                     one column in, like the original line)
    BY SJA-PROCESSES 2026.11         row 27 (the commit on a development build)

and back, in the same three-band capitals. The version and date are baked
in at build time: tools/release.py passes the git tag and its commit date;
any other build is DEV + the short commit id (version_info()).

The title loop ($DAF9) waits a frame with JSR $EC22 at $DB1D; that call
now goes through a fixed-bank trampoline to the bank-11 routine, which on
a new Left/Right press flips SHOWN and redraws the two rows over the next
two frames with the game's own row writer (NMI: $1D tiles from ($62) to
PPU $61:$60, as $EC33 uses). The loop's set-up `LDA #0 / STA $65` at $DAF9
calls INIT instead, which also clears the state each time the title
screen starts. State lives in save RAM page $76xx (see daygoal.py).

New glyphs (L V B J F - and the digits the title lacks) go in CHR bank 12
tiles that no screen uses: not in the title nametable, not in the
other bank-12 screen's strings ($E4C9/$E4DA, tiles $E0-$FD) and not in
the Gold Emperor warehouse picture ($1E), which uses this bank too.
"""
import subprocess

import daygoal
import title

CODE_BANK = daygoal.CODE_BANK
CODE = 0x8400                  # bank 11, after daygoal's routine
TRAMP, TRAMP_END = 0xFC90, 0xFCC0   # free fixed-bank run before daygoal's trampoline
TITLE_INIT, TITLE_WAIT = 0xDAF9, 0xDB1D
EC22, C049 = 0xEC22, 0xC049
BUTTONS, LEFT_RIGHT = 0x82, 0x03
ROW_COL = 6                    # rows 25 and 27 are rewritten from column 6
WIDTH = 32 - ROW_COL
TEXT_MAX = 24                  # to column 29, as the original lines; 30-31 colour wrongly
ROWS = (25, 27)
OTHER_SCREEN = range(0xE0, 0xFE)

# save RAM scratch (daygoal uses $7600-$760D)
SHOWN, PREV, PENDING = 0x7620, 0x7621, 0x7622
ROWBUF = 0x7630

AUTHOR = 'SJA-PROCESSES'

# colour digit per pixel, three bands like the other title capitals
GLYPHS = {
    'L': ['.11.....', '.11.....', '.11.....', '.22.....', '.22.....', '.33.....', '.33.....', '.3333333'],
    'V': ['11...11.', '11...11.', '11...11.', '.22.22..', '.22.22..', '..333...', '..333...', '...3....'],
    'B': ['.111111.', '.11...11', '.11...11', '.222222.', '.22...22', '.33...33', '.33...33', '.333333.'],
    'J': ['.....111', '......11', '......11', '......22', '......22', '.33...33', '.333.333', '..33333.'],
    'F': ['.1111111', '.11.....', '.11.....', '.222222.', '.22.....', '.33.....', '.33.....', '.33.....'],
    '-': ['........', '........', '........', '.222222.', '.222222.', '........', '........', '........'],
    '0': ['..11111.', '.11...11', '.11..111', '.22.2.22', '.222..22', '.33...33', '.33...33', '..33333.'],
    '2': ['..11111.', '.11...11', '......11', '....222.', '..222...', '.33.....', '.33.....', '.3333333'],
    '3': ['..11111.', '.11...11', '......11', '...2222.', '......22', '......33', '.33...33', '..33333.'],
    '4': ['....111.', '...1111.', '..11.11.', '.22..22.', '.2222222', '.....33.', '.....33.', '.....33.'],
    '5': ['.1111111', '.11.....', '.11.....', '.222222.', '......22', '......33', '.33...33', '..33333.'],
    '6': ['..11111.', '.11...11', '.11.....', '.222222.', '.22...22', '.33...33', '.33...33', '..33333.'],
    '7': ['.1111111', '.11...11', '.....11.', '....22..', '....22..', '...33...', '...33...', '...33...'],
    # centred, for 1.0 and 2026.11 (the title's own '.' sits at the left: "K. KIUCHI")
    '.': ['........', '........', '........', '........', '........', '........', '...33...', '...33...'],
}
EXISTING = {'1': 0xAC, '9': 0xAD, '8': 0xAE}


def version_info(version=None, date=None):
    """-> (row 25 text, row 27 text). With no version: DEV + commit."""
    if version:
        return ' ENGLISH VERSION ' + version.upper(), 'BY %s %s' % (AUTHOR, date)
    try:
        commit = subprocess.run(['git', 'rev-parse', '--short=7', 'HEAD'], capture_output=True,
                                text=True, check=True).stdout.strip().upper()
    except (OSError, subprocess.CalledProcessError):
        commit = ''
    return ' ENGLISH VERSION DEV', ('BY %s %s' % (AUTHOR, commit)).strip()


def _tile_bytes(rows):
    lo, hi = bytearray(8), bytearray(8)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            v = 0 if ch == '.' else int(ch)
            lo[y] |= (v & 1) << (7 - x)
            hi[y] |= (v >> 1) << (7 - x)
    return bytes(lo + hi)


def _nametable(new):
    bank, addr = title.NAMETABLE
    o = bank * 0x4000 + addr - 0x8000
    return o, new[o:o + 960]


def _row(nt, r):
    return bytes(nt[r * 32 + ROW_COL:r * 32 + 32])


def assemble(base, prog):
    extra = {('STA', 'zp'): 0x85, ('DEC', 'abs'): 0xCE, ('TYA', ''): 0x98, ('LDY', 'abs'): 0xAC}
    daygoal.OPS.update(extra)
    return daygoal.assemble(base, prog)


def routine(table):
    """Bank-11 routine, called once a frame on the title screen."""
    return [
        ('LDA', 'zp', BUTTONS), ('AND', 'imm', LEFT_RIGHT), ('TAX', ''),
        ('LDY', 'abs', PREV), ('STX', 'abs', PREV),
        ('CPY', 'imm', 0), ('BNE', None, 'pend'),       # held from before
        ('CPX', 'imm', 0), ('BEQ', None, 'pend'),       # not pressed
        ('LDA', 'abs', SHOWN), ('EOR', 'imm', 1), ('STA', 'abs', SHOWN),
        ('LDA', 'imm', len(ROWS)), ('STA', 'abs', PENDING),
        'pend', ('LDA', 'abs', PENDING), ('BEQ', None, 'done'),
        ('DEC', 'abs', PENDING),
        # Y = SHOWN * 2 * WIDTH + (PENDING == 0) * WIDTH
        ('LDY', 'imm', 0), ('LDA', 'abs', SHOWN), ('BEQ', None, 'which'),
        ('LDY', 'imm', 2 * WIDTH),
        'which', ('LDA', 'abs', PENDING), ('BNE', None, 'copy'),
        ('TYA', ''), ('CLC', ''), ('ADC', 'imm', WIDTH), ('TAY', ''),
        'copy', ('LDX', 'imm', 0),
        'c_loop', ('LDA', 'absy', 'table'), ('STA', 'absx', ROWBUF),
        ('INY', ''), ('INX', ''), ('CPX', 'imm', WIDTH), ('BNE', None, 'c_loop'),
        # PPU address: row 25 while PENDING is 1, row 27 when it is 0
        ('LDA', 'imm', (0x2000 + ROWS[1] * 32 + ROW_COL) & 0xFF),
        ('LDX', 'abs', PENDING), ('BEQ', None, 'addr'),
        ('LDA', 'imm', (0x2000 + ROWS[0] * 32 + ROW_COL) & 0xFF),
        'addr', ('STA', 'zp', 0x60), ('LDA', 'imm', 0x23), ('STA', 'zp', 0x61),
        ('LDA', 'imm', ROWBUF & 0xFF), ('STA', 'zp', 0x62),
        ('LDA', 'imm', ROWBUF >> 8), ('STA', 'zp', 0x63),
        ('LDA', 'imm', WIDTH), ('STA', 'zp', 0x1D),
        'done', ('RTS', ''),
        'table', ('.db', table),
    ]


def picture_tiles(new, bank_size=0x4000, fixed_bank=15):
    """Bank-12 tiles a scene picture uses: the Gold Emperor warehouse
    ($1E) is drawn with the title's CHR bank. (The first version of this
    file missed it and drew the glyphs over tiles $01-$0E of the
    warehouse; Stephen, 2026-11-11.) Plus the scene frame tiles."""
    f = new[fixed_bank * bank_size:]
    b1 = new[bank_size:2 * bank_size]
    used = {0x00, 0x02, 0x07, 0x2A, 0xBB, 0xFF}
    for p in range(37):
        if f[0xED2E - 0xC000 + p] == title.CHR_BANK:
            i = f[0xED53 - 0xC000 + p]
            used |= set(b1[i * 0x130:i * 0x130 + 280])
    return used


def apply(new, chr_, version=None, date=None, bank_size=0x4000, fixed_bank=15):
    """After title.apply and daygoal.apply. -> the two info lines."""
    lines = version_info(version, date)
    o, nt = _nametable(new)
    assert (0x2000 + ROWS[0] * 32) >> 8 == 0x23 == (0x2000 + ROWS[1] * 32) >> 8

    # glyphs: reuse the title's letters, draw the rest in unused tiles
    cb = title.CHR_BANK * 0x1000
    used = set(nt) | set(OTHER_SCREEN) | {0} | picture_tiles(new, bank_size, fixed_bank)
    free = [t for t in range(256) if t not in used]
    tiles = dict(title.LETTERS)
    tiles.update({ch: t for ch, (t, _) in title.NEW_TILES.items()})
    tiles.update(EXISTING)
    for ch, rows in GLYPHS.items():
        t = free.pop(0)
        chr_[cb + t * 16:cb + t * 16 + 16] = _tile_bytes(rows)
        tiles[ch] = t

    table = bytearray()
    for r in ROWS:                                   # SHOWN = 0: the original lines
        table += _row(nt, r)
    for text in lines:                               # SHOWN = 1: the info
        assert len(text) <= TEXT_MAX, text
        table += bytes(tiles[ch] for ch in text.ljust(WIDTH))

    code, _ = assemble(CODE, routine(bytes(table)))
    bo = CODE_BANK * bank_size + CODE - 0x8000
    assert new[bo:bo + len(code)] == b'\xFF' * len(code), 'bank 11 not free at $%04X' % CODE
    new[bo:bo + len(code)] = code

    tramp, tl = assemble(TRAMP, [
        'wait', ('LDA', 'zp', 0x7C), ('PHA', ''), ('LDA', 'imm', CODE_BANK), ('JSR', 'abs', C049),
        ('JSR', 'abs', CODE), ('PLA', ''), ('JSR', 'abs', C049), ('JMP', 'abs', EC22),
        'init', ('LDA', 'imm', 0), ('STA', 'zp', 0x65),
        ('STA', 'abs', SHOWN), ('STA', 'abs', PENDING),
        ('LDA', 'imm', LEFT_RIGHT), ('STA', 'abs', PREV),     # a held button doesn't toggle
        ('RTS', ''),
    ])
    assert TRAMP + len(tramp) <= TRAMP_END, hex(TRAMP + len(tramp))
    fx = fixed_bank * bank_size - 0xC000
    assert new[fx + TRAMP:fx + TRAMP + len(tramp)] == b'\xFF' * len(tramp)
    new[fx + TRAMP:fx + TRAMP + len(tramp)] = tramp
    for addr, was, now in ((TITLE_INIT, bytes([0xA9, 0x00, 0x85, 0x65]),
                            bytes([0x20, tl['init'] & 0xFF, tl['init'] >> 8, 0xEA])),
                           (TITLE_WAIT, bytes([0x20, EC22 & 0xFF, EC22 >> 8]),
                            bytes([0x20, tl['wait'] & 0xFF, tl['wait'] >> 8]))):
        assert new[fx + addr:fx + addr + len(was)] == was, hex(addr)
        new[fx + addr:fx + addr + len(now)] = now
    return lines
