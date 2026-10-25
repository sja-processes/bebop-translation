"""Read Stephen's Mesen save states (~/.config/MesenCE/SaveStates).

    python3 tools/mesenstate.py N [out.png]   summary of bebop_en_N.mss

A .mss file holds a zlib-compressed 256x240 screenshot (16-bit NES
palette indices) at byte 35, then the zlib-compressed machine state: a
series of NUL-terminated field names, each followed by a 32-bit length
and the data. Save RAM ($6000-$7FFF) is 'mapper.saveRam'; game flags are
$7100 + n, so flag n is saveRam[$1100 + n].
"""
import os
import re
import struct
import sys
import zlib

DIR = os.path.expanduser('~/.config/MesenCE/SaveStates')


def load(n):
    d = open(os.path.join(DIR, 'bebop_en_%d.mss' % n), 'rb').read()
    o = zlib.decompressobj()
    scr = o.decompress(d[35:])
    rest = o.unused_data
    for j in range(len(rest) - 1):
        if rest[j] == 0x78 and rest[j + 1] in (0x01, 0x5E, 0x9C, 0xDA):
            try:
                return scr, zlib.decompress(rest[j:])
            except zlib.error:
                pass
    raise ValueError('no machine state found')


def fields(st):
    out = {}
    for m in re.finditer(rb'([a-zA-Z][a-zA-Z0-9_.\[\]]{2,})\x00', st):
        p = m.end()
        if p + 4 <= len(st):
            n = struct.unpack('<I', st[p:p + 4])[0]
            if n < 0x20000:
                out.setdefault(m.group(1).decode(), st[p + 4:p + 4 + n])
    return out


def flags(f):
    return f['mapper.saveRam'][0x1100:0x1200]


def screenshot(scr, path):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caretaker'))
    from nespal import NES
    from PIL import Image
    im = Image.new('RGB', (256, 240))
    px = im.load()
    for i in range(256 * 240):
        px[i % 256, i // 256] = NES[(scr[2 * i] | scr[2 * i + 1] << 8) & 0x3F]
    im.save(path)


if __name__ == '__main__':
    scr, st = load(int(sys.argv[1]))
    f = fields(st)
    p = flags(f)
    print('flags set:', ' '.join('%02x' % i for i in range(0xAA) if p[i]))
    print('day %d, %02d:%02d, luck %s, nerve %d, area %d' % (
        p[0xC8], p[0xC6], p[0xC5], ['JINX', 'BAD', 'FAIR', 'GOOD', 'CHARM'][list(p[0xAD:0xB2]).index(1)]
        if 1 in p[0xAD:0xB2] else '-', p[0xB8], f['memoryManager.internalRam'][0x3F]))
    if len(sys.argv) > 2:
        screenshot(scr, sys.argv[2])
