#!/usr/bin/env python3
"""Build the English ROM and IPS patch.

usage: tools/insert.py            -> out/bebop_en.nes, out/bebop_en.bps

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
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import encheck  # noqa: E402
import font     # noqa: E402
import title    # noqa: E402
import status   # noqa: E402
import credits  # noqa: E402
import sceneart # noqa: E402
import additions # noqa: E402
sys.path.insert(0, os.path.join(HERE, 'caretaker'))
import build as caretaker  # noqa: E402
import storepics  # noqa: E402
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
    # luck grades are drawn in the status panel's own glyph tiles; their
    # words live in tools/status.py (the EN file keeps the JP raw tiles)
    msgs.update(status.grade_texts())
    assert min(additions.MESSAGES) == len(ids), 'additions must follow the script'
    msgs.update(additions.MESSAGES)
    storepics.retarget(msgs)        # department store picture variants
    return [msgs[i] for i in sorted(msgs)]


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
    # Menu highlight (8 sprites behind the text, $EA0D): the JP layout put
    # 2 on the dakuten row and 6 on the text row, so a 7-letter English
    # verb lost its last letter's highlight. Move one sprite down to give
    # 7 on the text row; the spare stays on the row above (hidden behind
    # the opaque background), keeping the per-scanline sprite count.
    for addr, was, now in ((0xEA80, '00 00 08 08 08 08 08 08', '00 08 08 08 08 08 08 08'),
                           (0xEA88, '08 10 00 08 10 18 20 28', '00 00 08 10 18 20 28 30')):
        assert fixed[f(addr):f(addr) + 8] == bytes.fromhex(was)
        fixed[f(addr):f(addr) + 8] = bytes.fromhex(now)
    for addr, was, now in additions.PATCHES:
        assert fixed[f(addr):f(addr) + len(was)] == was
        fixed[f(addr):f(addr) + len(now)] = now
    new += fixed

    for ch, (tile, rows) in font.build().items():
        for cb in FONT_CHR_BANKS:
            o = cb * 0x1000 + tile * 16
            chr_[o:o + 16] = font.tile_bytes(rows)

    title.apply(new, chr_)
    status.apply(new, chr_)
    sceneart.apply(new, chr_)
    # credits reuse the English font just written to CHR bank 30
    fx = bytearray(new[FIXED * BANK:(FIXED + 1) * BANK])
    credits.apply(fx, chr_)
    new[FIXED * BANK:(FIXED + 1) * BANK] = fx
    # department store variants ($26-$29, CHR bank 10's free tiles), then
    # the caretaker's room ($25, the bank-29 tiles the credits leave free),
    # which also builds the hooks for all the new pictures
    used10 = caretaker._picture_tiles_used(new, storepics.CHR_BANK)
    free10 = [t for t in range(256) if t not in used10 and t not in caretaker.SCENE_FRAME]
    store, store_tiles = storepics.build(read_rom(), used10, free10)
    for t, data in store_tiles.items():
        o = storepics.CHR_BANK * 0x1000 + t * 16
        chr_[o:o + 16] = data
    caretaker.apply(new, chr_, additions.CARETAKER_SCENE,
                    [(n, storepics.CHR_BANK, lay, pal) for n, lay, pal in store])

    header[4] = NEW_PRG_BANKS
    out = bytes(header + new + chr_)
    report = {b: len(d) for b, d in banks.items()}
    return bytes(rom), out, starts, verb_addr, report


def _bps_num(n):
    out = bytearray()
    while True:
        x, n = n & 0x7F, n >> 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def _bps_literal(out, new, i, j, tgt_rel, min_run=16):
    """Emit new[i:j] as TargetRead, turning runs of one byte value into
    TargetRead(1) + TargetCopy (overlapping copy = run-length fill)."""
    k = i
    while k < j:
        r = k
        while r < j and new[r] == new[k]:
            r += 1
        if r - k >= min_run:
            out += _bps_num(1) + new[k:k + 1]                  # TargetRead 1
            d = k - tgt_rel
            out += _bps_num(((r - k - 2) << 2) | 3) + _bps_num((abs(d) << 1) | (d < 0))
            tgt_rel = r - 1
            k = r
            continue
        # literal up to the next long run
        e = k
        while e < j and not all(new[x] == new[e] for x in range(e, min(e + min_run, j))) or e == k:
            e += 1
            if e >= j:
                break
        e = min(e, j)
        out += _bps_num(((e - k - 1) << 2) | 1) + new[k:e]
        k = e
    return tgt_rel


def bps(old, new, key=16):
    """BPS patch old -> new. SourceRead where bytes are unchanged in place,
    SourceCopy for any run of `key`+ bytes found elsewhere in the original
    (the CHR ROM and fixed bank moved by the expansion, and message bytes
    that are pure control codes), TargetRead (with run-length fills) for
    the rest. The patch therefore carries no original ROM data."""
    index = {}
    for k in range(len(old) - key + 1):
        index.setdefault(old[k:k + key], k)
    out = bytearray(b'BPS1' + _bps_num(len(old)) + _bps_num(len(new)) + _bps_num(0))
    same = lambda i: i < len(old) and old[i] == new[i]

    def source_at(i):
        """Best source offset for new[i:], or None."""
        chunk = new[i:i + key]
        if len(chunk) < key:
            return None
        for cand in (src_rel,):
            if old[cand:cand + key] == chunk:
                return cand
        return index.get(chunk)

    src_rel = tgt_rel = 0
    i = 0
    while i < len(new):
        j = i
        if all(same(k) for k in range(i, min(i + 4, len(new)))):
            while j < len(new) and same(j):
                j += 1
            out += _bps_num(((j - i - 1) << 2) | 0)
        elif source_at(i) is not None:
            src = source_at(i)
            while j < len(new) and src + (j - i) < len(old) and old[src + j - i] == new[j]:
                j += 1
            d = src - src_rel
            out += _bps_num(((j - i - 1) << 2) | 2) + _bps_num((abs(d) << 1) | (d < 0))
            src_rel = src + (j - i)
        else:
            j += 1
            while j < len(new) and not (
                    all(same(k) for k in range(j, min(j + 4, len(new))))
                    or source_at(j) is not None):
                j += 1
            tgt_rel = _bps_literal(out, new, i, j, tgt_rel)
        i = j
    out += zlib.crc32(old).to_bytes(4, 'little') + zlib.crc32(new).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out)


def apply_bps(old, patch):
    pos = 4

    def num():
        nonlocal pos
        n, shift = 0, 1
        while True:
            x = patch[pos]
            pos += 1
            n += (x & 0x7F) * shift
            if x & 0x80:
                return n
            shift <<= 7
            n += shift

    assert patch[:4] == b'BPS1'
    assert zlib.crc32(old) == int.from_bytes(patch[-12:-8], 'little'), 'wrong source ROM'
    num()
    size = num()
    meta = num()
    pos += meta
    out = bytearray()
    src_rel = tgt_rel = 0
    while pos < len(patch) - 12:
        d = num()
        kind, length = d & 3, (d >> 2) + 1
        if kind == 0:
            out += old[len(out):len(out) + length]
        elif kind == 1:
            out += patch[pos:pos + length]
            pos += length
        else:
            o = num()
            o = -(o >> 1) if o & 1 else o >> 1
            if kind == 2:
                src_rel += o
                out += old[src_rel:src_rel + length]
                src_rel += length
            else:
                tgt_rel += o
                for _ in range(length):
                    out.append(out[tgt_rel])
                    tgt_rel += 1
    assert len(out) == size
    assert zlib.crc32(out) == int.from_bytes(patch[-8:-4], 'little')
    return bytes(out)


def check_no_rom_data(old, patch, limit=64):
    """Fail if any TargetRead literal of `limit`+ bytes appears verbatim in
    the original ROM (the patch must not redistribute game data)."""
    pos = 4

    def num():
        nonlocal pos
        n, shift = 0, 1
        while True:
            x = patch[pos]
            pos += 1
            n += (x & 0x7F) * shift
            if x & 0x80:
                return n
            shift <<= 7
            n += shift

    num()
    num()
    meta = num()
    pos += meta
    while pos < len(patch) - 12:
        d = num()
        kind, length = d & 3, (d >> 2) + 1
        if kind == 1:
            lit = patch[pos:pos + length]
            pos += length
            if length >= limit and len(set(lit)) > 1:
                for k in range(0, length - limit + 1, limit // 2):
                    assert lit[k:k + limit] not in old, \
                        'patch literal contains original ROM bytes'
        elif kind >= 2:
            num()


def main():
    old, new, starts, verb_addr, report = build()
    outdir = os.path.join(ROOT, 'out')
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'bebop_en.nes'), 'wb').write(new)
    # BPS only: an IPS cannot copy the CHR ROM that the expansion moves,
    # so it would have to contain the original graphics verbatim.
    bpatch = bps(old, new)
    assert apply_bps(old, bpatch) == new
    check_no_rom_data(old, bpatch)
    open(os.path.join(outdir, 'bebop_en.bps'), 'wb').write(bpatch)
    for b, used in sorted(report.items()):
        print('bank %2d: %5d bytes used, %5d free' % (b, used, TEXT_LIMIT - 0x8000 - used))
    print('bank start IDs:', ', '.join('%03X@%d' % s for s in starts))
    print('verb list: bank %d $%04X' % verb_addr)
    print('wrote out/bebop_en.nes (%d bytes), out/bebop_en.bps (%d bytes)'
          % (len(new), len(bpatch)))


if __name__ == '__main__':
    main()
