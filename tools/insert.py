#!/usr/bin/env python3
"""Build the English ROM and IPS patch.

usage: tools/insert.py            -> out/bebop_en.nes, out/bebop_en.ips

Steps (see PLAN.md stage 6):
  1. Expand PRG 128 KB -> 256 KB: banks 0-6 unchanged, banks 7-14 free for
     text (each gets the $BFF0 reset stub + vectors), bank 15 = the old
     fixed bank 7.
  2. Encode script/en/*.txt (all 962 messages, in ID order) with the
     English font map and pack them into banks 8.. (bank 7 kept spare).
  3. Patch the fixed bank: message lookup $DBEE -> new routine that picks
     the bank from a start-ID table, and the verb list pointer at $DE88.
  4. Write the English font into CHR banks 30 and 31.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import encheck  # noqa: E402
import font     # noqa: E402
import script   # noqa: E402

ROOT = os.path.dirname(HERE)
BANK = 0x4000
OLD_PRG_BANKS, NEW_PRG_BANKS = 8, 16
FIXED = NEW_PRG_BANKS - 1
FIRST_TEXT_BANK = 8
TEXT_LIMIT = 0xBFF0           # keep the reset stub at $BFF0-$BFFF
VERB_FIRST, VERB_LAST = 0x3AA, 0x3C1
NEW_CODE = 0xFD00             # free $FF run in the fixed bank ($FCFC-$FFCF)
FONT_CHR_BANKS = (30, 31)


def read_rom():
    romdir = os.path.join(ROOT, 'rom')
    name = next(f for f in os.listdir(romdir) if f.endswith('.nes'))
    return open(os.path.join(romdir, name), 'rb').read()


def english_messages():
    msgs = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'script/en/*.txt'))):
        for mid, (_, text) in encheck.parse(path, 'EN').items():
            msgs[mid] = text
    ids = sorted(msgs)
    assert ids == list(range(len(ids))), 'missing message IDs'
    return [msgs[i] for i in ids]


def encode_all(texts):
    tbl = {bytes([t]): ch for ch, t in font.char_map().items()}
    out = []
    for mid, text in enumerate(texts):
        try:
            data = script.encode(tbl, text)
        except (ValueError, KeyError) as e:
            sys.exit('message %03X: %s' % (mid, e))
        assert 0xFF not in data[:-1], 'message %03X has $FF inside' % mid
        out.append(data)
    return out


def pack(encoded):
    """-> (banks {bank: bytearray}, starts [(first_id, bank)], verb_addr)"""
    banks, starts = {}, []
    bank, buf, verb_addr = FIRST_TEXT_BANK, bytearray(), None
    starts.append((0, bank))
    verb_block = sum(len(m) for m in encoded[VERB_FIRST:VERB_LAST + 1])
    for mid, data in enumerate(encoded):
        need = verb_block if mid == VERB_FIRST else len(data)
        if 0x8000 + len(buf) + need > TEXT_LIMIT:
            banks[bank] = buf
            bank, buf = bank + 1, bytearray()
            assert bank < FIXED, 'out of text banks'
            starts.append((mid, bank))
        if mid == VERB_FIRST:
            verb_addr = (bank, 0x8000 + len(buf))
        buf += data
    banks[bank] = buf
    return banks, starts, verb_addr


def asm_lookup(starts, base):
    """Message lookup: X/Y = ID -> select bank, X/Y = index, JMP $DC05."""
    n = len(starts)
    tab_lo = base + 0x40
    tab_hi, tab_bank = tab_lo + n, tab_lo + 2 * n
    lo = lambda a: a & 0xFF
    hi = lambda a: a >> 8
    code = bytearray()
    code += bytes([0x86, 0x12, 0x84, 0x13,          # STX $12 / STY $13
                   0xA2, n - 1])                     # LDX #n-1
    loop = base + len(code)
    code += bytes([0xA5, 0x13,                       # LDA $13
                   0xDD, lo(tab_hi), hi(tab_hi),     # CMP tab_hi,X
                   0x90, 0x09,                       # BCC next
                   0xD0, 0x0C,                       # BNE found
                   0xA5, 0x12,                       # LDA $12
                   0xDD, lo(tab_lo), hi(tab_lo),     # CMP tab_lo,X
                   0xB0, 0x05])                      # BCS found
    # next:
    code += bytes([0xCA,                             # DEX
                   0x10, (loop - (base + len(code) + 3)) & 0xFF,  # BPL loop
                   0xA2, 0x00])                      # LDX #0 (safety)
    # found:
    found = base + len(code)
    assert found == base + 27, hex(found)
    code += bytes([0x38,                             # SEC
                   0xA5, 0x12,                       # LDA $12
                   0xFD, lo(tab_lo), hi(tab_lo),     # SBC tab_lo,X
                   0x48,                             # PHA
                   0xA5, 0x13,                       # LDA $13
                   0xFD, lo(tab_hi), hi(tab_hi),     # SBC tab_hi,X
                   0x48,                             # PHA
                   0xBD, lo(tab_bank), hi(tab_bank), # LDA tab_bank,X
                   0x20, 0x49, 0xC0,                 # JSR $C049 (select)
                   0x68, 0xA8,                       # PLA / TAY
                   0x68, 0xAA,                       # PLA / TAX
                   0x4C, 0x05, 0xDC])                # JMP $DC05 (skip loop)
    assert len(code) <= 0x40
    code = code.ljust(0x40, b'\xFF')
    code += bytes(lo(s) for s, _ in starts)
    code += bytes(hi(s) for s, _ in starts)
    code += bytes(b for _, b in starts)
    return bytes(code)


def fix_branches(code, base):
    """Check the hand-placed branch offsets in asm_lookup land correctly."""
    # BCC next at +11 -> next; BNE found at +13 -> found; BCS at +20 -> found
    nxt, found = base + 22, base + 27
    for at, target in ((11, nxt), (13, found), (20, found), (23, base + 6)):
        off = code[at + 1]
        dest = base + at + 2 + (off - 256 if off > 127 else off)
        assert dest == target, ('branch at +%d -> %04X, want %04X'
                                % (at, dest, target))


def build():
    rom = bytearray(read_rom())
    header, prg = rom[:16], rom[16:16 + OLD_PRG_BANKS * BANK]
    chr_ = bytearray(rom[16 + OLD_PRG_BANKS * BANK:])
    stub = prg[BANK - 16:BANK]                        # bank 0 $BFF0-$BFFF

    new = bytearray(prg[:7 * BANK])
    for _ in range(7, FIXED):
        new += b'\xFF' * (BANK - 16) + stub
    fixed = bytearray(prg[7 * BANK:8 * BANK])

    banks, starts, verb_addr = pack(encode_all(english_messages()))
    for b, data in banks.items():
        new[b * BANK:b * BANK + len(data)] = data

    f = lambda addr: addr - 0xC000
    code = asm_lookup(starts, NEW_CODE)
    fix_branches(code, NEW_CODE)
    fixed[f(NEW_CODE):f(NEW_CODE) + len(code)] = code
    fixed[f(0xDBEE):f(0xDBEE) + 3] = bytes([0x4C, NEW_CODE & 0xFF, NEW_CODE >> 8])
    # verb list: JSR $C087 -> JSR verbsel (LDA #bank / JMP $C049)
    vsel = NEW_CODE + len(code)
    fixed[f(vsel):f(vsel) + 5] = bytes([0xA9, verb_addr[0], 0x4C, 0x49, 0xC0])
    assert fixed[f(0xDE88):f(0xDE8B)] == bytes([0x20, 0x87, 0xC0])
    fixed[f(0xDE88):f(0xDE8B)] = bytes([0x20, vsel & 0xFF, vsel >> 8])
    assert fixed[f(0xDE8B)] == 0xA9 and fixed[f(0xDE8F)] == 0xA9
    fixed[f(0xDE8C)] = verb_addr[1] & 0xFF
    fixed[f(0xDE90)] = verb_addr[1] >> 8
    new += fixed

    for ch, (tile, rows) in font.build().items():
        for cb in FONT_CHR_BANKS:
            o = cb * 0x1000 + tile * 16
            chr_[o:o + 16] = font.tile_bytes(rows)

    header[4] = NEW_PRG_BANKS
    out = bytes(header + new + chr_)
    report = {b: len(d) for b, d in banks.items()}
    return bytes(rom), out, starts, verb_addr, report


def ips(old, new):
    """IPS patch old -> new (new may be longer)."""
    out = bytearray(b'PATCH')
    i = 0
    while i < len(new):
        if i < len(old) and old[i] == new[i]:
            i += 1
            continue
        j = i
        while j < len(new) and j - i < 0xFFFF and not (
                j < len(old) and old[j:j + 6] == new[j:j + 6]):
            j += 1
        chunk = new[i:j]
        assert i != 0x454F46
        if len(set(chunk)) == 1 and len(chunk) > 8:
            out += i.to_bytes(3, 'big') + b'\0\0' + len(chunk).to_bytes(2, 'big') + chunk[:1]
        else:
            out += i.to_bytes(3, 'big') + len(chunk).to_bytes(2, 'big') + chunk
        i = j
    out += b'EOF'
    return bytes(out)


def apply_ips(old, patch):
    data = bytearray(old)
    i = 5
    while patch[i:i + 3] != b'EOF':
        off = int.from_bytes(patch[i:i + 3], 'big')
        size = int.from_bytes(patch[i + 3:i + 5], 'big')
        i += 5
        if size == 0:
            size = int.from_bytes(patch[i:i + 2], 'big')
            chunk = patch[i + 2:i + 3] * size
            i += 3
        else:
            chunk = patch[i:i + size]
            i += size
        if len(data) < off + size:
            data += bytes(off + size - len(data))
        data[off:off + size] = chunk
    return bytes(data)


def main():
    old, new, starts, verb_addr, report = build()
    outdir = os.path.join(ROOT, 'out')
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'bebop_en.nes'), 'wb').write(new)
    patch = ips(old, new)
    assert apply_ips(old, patch) == new
    open(os.path.join(outdir, 'bebop_en.ips'), 'wb').write(patch)
    for b, used in sorted(report.items()):
        print('bank %2d: %5d bytes used, %5d free' % (b, used, TEXT_LIMIT - 0x8000 - used))
    print('bank start IDs:', ', '.join('%03X@%d' % s for s in starts))
    print('verb list: bank %d $%04X' % verb_addr)
    print('wrote out/bebop_en.nes (%d bytes), out/bebop_en.ips (%d bytes)'
          % (len(new), len(patch)))


if __name__ == '__main__':
    main()
