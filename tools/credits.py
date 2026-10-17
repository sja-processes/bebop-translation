"""Ending staff credits (stage 7d).

$EE42 (ending) switches the BG CHR bank to 29 and draws 12 layout streams
from fixed-bank $F941 with $EEED: first byte = low byte of a $20xx PPU
address, then tile numbers; $F5 = next row (same start column), $F6 n =
move the start column right by n, $FF = end of stream. CHR bank 29 is
used only by these screens, so it is rebuilt here from scratch:
  - tiles $00-$4B, $FE: the dialogue font (same char map as script text),
    ink colour 0 on colour 1 like the original name lettering;
  - role titles: white-on-black copies of the capitals (the original
    role kanji are colour 1 on colour 0);
  - big 16x16 letters (the font doubled) for the opening exclamation and
    THE END, which were large glyphs in the original.
"""
import font

CHR_BANK = 29
STREAMS = (0xF941, 0xFCFD)       # fixed-bank range the original streams use

# Tiles the original credit streams never use. $81/$BB/$FF belong to the
# ending's frame graphics -- one of them is under sprite 0, and the NMI's
# mid-screen CHR switch hangs if that sprite-0 hit never happens -- so
# they (and the blanks) are left exactly as they are.
KEEP = (0x81, 0xBB, 0xE6, 0xF0, 0xF1, 0xF5, 0xF6, 0xFF)

# Scene-picture frame tiles ($02/$07/$2A, drawn from the picture's own CHR
# bank; $BB/$FF are in KEEP). The caretaker's room picture uses this bank,
# so tools/caretaker/build.py puts the frame graphics on these tiles.
SCENE_FRAME = (0x02, 0x07, 0x2A)

# (PPU low byte, big text) for the opening line and the closing screen.
OPENING = (0xAA, 'ARGH!')        # original: a large exclamation at $20AC
CLOSING = (0x89, 'THE END')      # original: a large 終 at $208D

ROLE_COL = 4                     # screens start at $2044 (row 2, col 4)
NAME_INDENT = 2
SCREENS = [
    ('ORIGINAL STORY', ['KAZUHIRO KIUCHI']),
    ('PLANNING', ['KOICHI OTA']),
    ('GRAPHICS', ['TEPPEI TERASHITA', 'SHIRO HATAKEYAMA', 'KEIYU SHINKYU']),
    ('GRAPHICS', ['TAKASHI WATANABE', 'YOSHIKO ASANO']),
    ('MUSIC', ['HIROMICHI NAKAMOTO', 'SHOGO SAKAI']),
    ('MUSIC', ['TAKASHI MIURA', 'SHINICHI KAMIZONO']),
    ('PROGRAMMING', ['JICHO NAKAMURA', 'YASUHIRO GUMON', 'SEIICHI ISHII']),
    ('PROGRAMMING', ['MASAHIKO FUKUMOTO', 'TAKANOBU KANAYAMA']),
    ('SPECIAL THANKS', ['KAZUHIRO KIUCHI', 'KAZUMASA KIUCHI', 'YUKARI KIUCHI']),
    ('SPECIAL THANKS', ['TAKAYUKI', 'KAZUSHIGE']),
]
NEWROW, SHIFT, END = 0xF5, 0xF6, 0xFF


def _bytes(rows, colours):
    """8 row strings ('#' ink) -> CHR bytes with (ink, background) colours."""
    ink, bg = colours
    pix = [[ink if r.ljust(8, '.')[x] == '#' else bg for x in range(8)] for r in rows]
    lo = bytes(sum((p[x] & 1) << (7 - x) for x in range(8)) for p in pix)
    hi = bytes(sum((p[x] >> 1) << (7 - x) for x in range(8)) for p in pix)
    return lo + hi


def _big(rows):
    """8x8 glyph -> four 8x8 quarters of the pixel-doubled 16x16 glyph."""
    rows = [r.ljust(8, '.') for r in rows]
    big = [''.join(c * 2 for c in r) for r in rows for _ in range(2)]
    return [[big[y][x0:x0 + 8] for y in range(y0, y0 + 8)]
            for y0 in (0, 8) for x0 in (0, 8)]


def build(chr_font_bank, original):
    """-> (bank29 bytes, stream bytes). chr_font_bank = CHR bank 30 data
    (already holding the English font), used for the name lettering;
    original = the original CHR bank 29."""
    glyphs = {ch: rows for ch, (_, rows) in font.build().items()}
    font_map = font.char_map()
    bank = bytearray(original)
    # name lettering: only the characters the names use, at their font
    # tile numbers -- except those on SCENE_FRAME tiles, which move to
    # free tiles so the caretaker's room picture can use this bank
    name_chars = sorted(set(''.join(''.join(n) for _, n in SCREENS)))
    free = [t for t in range(0x00, 0x100)
            if t not in KEEP and t not in SCENE_FRAME
            and t not in [font_map[c] for c in name_chars]]
    cmap = {}

    def put(rows, colours):
        t = free.pop(0)
        bank[t * 16:t * 16 + 16] = _bytes(rows, colours)
        return t

    for ch in name_chars:
        src = font_map[ch]
        tile = free.pop(0) if src in SCENE_FRAME else src
        bank[tile * 16:tile * 16 + 16] = chr_font_bank[src * 16:src * 16 + 16]
        cmap[ch] = tile

    # role letters sit one pixel right so the black strip has a left
    # margin (the glyphs are at most 7 px wide, so a 1 px gap remains)
    role_map = {ch: put(['.' + r[:7] for r in glyphs[ch]], (1, 0))
                for ch in sorted(set(''.join(r for r, _ in SCREENS)) - {' '})}
    role_map[' '] = put(['.'] * 8, (1, 0))               # colour-0 blank

    big_map = {}                                         # char -> 4 tiles
    for ch in sorted(set(OPENING[1] + CLOSING[1]) - {' '}):
        big_map[ch] = [put(q, (0, 1)) for q in _big(glyphs[ch])]

    out = bytearray()

    def big_stream(pos, text):
        out.append(pos)
        for half in (0, 2):
            if half:
                out.append(NEWROW)
            for ch in text:
                if ch == ' ':
                    out.extend([0xFE, 0xFE])
                else:
                    out.extend(big_map[ch][half:half + 2])
        out.append(END)

    big_stream(*OPENING)
    for role, names in SCREENS:
        out.append(0x40 + ROLE_COL)                      # $2044
        out += bytes(role_map[c] for c in role)
        out += bytes([NEWROW, NEWROW, SHIFT, NAME_INDENT])
        for i, name in enumerate(names):
            if i:
                out += bytes([NEWROW, NEWROW])
            assert ROLE_COL + NAME_INDENT + len(name) <= 30, name
            out += bytes(cmap[c] for c in name)
        out.append(END)
    big_stream(*CLOSING)
    room = STREAMS[1] - STREAMS[0]
    assert len(out) <= room, (len(out), room)
    global USED
    USED = set(KEEP) | set(cmap.values()) | set(t for t in range(256) if t not in free)
    return bytes(bank), bytes(out) + b'\xFF' * (room - len(out))


USED = None    # tiles of CHR bank 29 the credits need (set by build())


def apply(fixed, chr_):
    """fixed = fixed-bank bytearray ($C000-), chr_ = CHR ROM bytearray."""
    bank, streams = build(chr_[30 * 0x1000:31 * 0x1000],
                          chr_[CHR_BANK * 0x1000:(CHR_BANK + 1) * 0x1000])
    chr_[CHR_BANK * 0x1000:(CHR_BANK + 1) * 0x1000] = bank
    a, b = (x - 0xC000 for x in STREAMS)
    fixed[a:b] = streams
