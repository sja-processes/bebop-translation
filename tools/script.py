#!/usr/bin/env python3
"""Parse Be-Bop High School script messages (banks 2 and 3).

Messages are $FF-terminated and located by counting from $8000 of their
bank: message IDs < $170 are in bank 2, IDs >= $170 are in bank 3 (as
ID - $170). See PLAN.md "Text engine" for the control-code reference.

usage: script.py check          parse every message, check render/encode
                                round-trips byte-for-byte
       script.py show ID [ID..] print messages (hex IDs) in readable form
       script.py dump           write script/jp/msg_XXX.txt (gitignored)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK3_FIRST_ID = 0x170
MENU_TABLE = 0xDEB3   # fixed bank; 6 slots per menu, row 0 = slot layout

# Control codes -> (name, fixed argument byte count). Variable-length
# codes use None and are handled in parse_message().
CODES = {
    0xFF: ('end', 0), 0xF5: ('nl', 0), 0xF4: ('page', 0),
    0xF3: ('delay', 1), 0xF7: ('setflag', 1), 0xF6: ('clrflag', 1),
    0xF2: ('goto', 2), 0xF1: ('call', 2), 0xD3: ('page+goto', 2),
    0xF0: ('cmdF0', 1), 0xEF: ('cmdEF', 1), 0xEE: ('cmdEE', 1),
    0xEC: ('cmdEC', 3), 0xEA: ('cmdEA', 1), 0xDE: ('cmdDE', 1),
    0xDD: ('cmdDD', 1),
    0xED: ('cmdED', 0), 0xEB: ('flash', 0), 0xD2: ('shake', 0),
    0xD1: ('cmdD1', 0), 0xE9: ('cmdE9', 0), 0xE8: ('cmdE8', 0),
    0xE7: ('cmdE7', 0), 0xE6: ('cmdE6', 0), 0xE5: ('cmdE5', 0),
    0xE4: ('fast', 0), 0xE3: ('slow', 0), 0xE2: ('cmdE2', 0),
    0xE1: ('cmdE1', 0), 0xE0: ('cmdE0', 0), 0xDF: ('cmdDF', 0),
    0xDC: ('cmdDC', 0), 0xDB: ('cmdDB', 0), 0xDA: ('cmdDA', 0),
    # flag branches: FD/D9 flag, target-if-clear, target-if-set
    0xFD: ('ifflag', 5), 0xD9: ('ifflag-call', 5),
    # two flags -> one of four targets
    0xF9: ('if2flags', 10), 0xD5: ('if2flags-call', 10),
    # lists of (flag, target) ending FA + default target
    0xFC: ('firstset', None), 0xD8: ('firstset-call', None),
    0xFB: ('firstclear', None), 0xD7: ('firstclear-call', None),
    # menus: menu id, then one target per non-empty slot
    0xF8: ('menu', None), 0xD4: ('menu-call', None),
}
DIACRITIC = (0x5A, 0x5B, 0x9D)   # mark drawn above, then next byte printed


def load_prg():
    romdir = os.path.join(ROOT, 'rom')
    name = next(f for f in os.listdir(romdir) if f.endswith('.nes'))
    data = open(os.path.join(romdir, name), 'rb').read()
    return data[16:16 + 8 * 0x4000]


def load_table():
    tbl = {}
    with open(os.path.join(ROOT, 'tools', 'bebop.tbl'), encoding='utf-8') as fh:
        for line in fh:
            if '=' in line and not line.startswith('#'):
                k, v = line.rstrip('\n').split('=', 1)
                tbl[bytes.fromhex(k)] = v.replace('\\n', '\n')
    return tbl


def menu_slots(prg, menu_id):
    off = 7 * 0x4000 + MENU_TABLE - 0xC000 + menu_id * 6
    return sum(1 for b in prg[off:off + 6] if b)


def split_messages(prg, bank):
    """Return list of (cpu_addr, bytes_including_FF) for a bank."""
    data = prg[bank * 0x4000:(bank + 1) * 0x4000]
    out, start = [], 0
    for i, b in enumerate(data):
        if b == 0xFF:
            out.append((0x8000 + start, data[start:i + 1]))
            start = i + 1
    return out


def parse_message(prg, msg):
    """Yield ('text', bytes) and ('code', opcode, name, argbytes) items."""
    i = 0
    while i < len(msg):
        b = msg[i]
        if b in CODES:
            name, n = CODES[b]
            if n is None:
                if b in (0xF8, 0xD4):
                    # one target per slot; a trailing "leave" slot may
                    # have none (message 2F7), so never read past the FF
                    n = min(1 + 2 * menu_slots(prg, msg[i + 1]),
                            len(msg) - 2 - i)
                else:
                    j = i + 1
                    while msg[j] != 0xFA:
                        j += 3
                    n = j - i + 2
            yield ('code', b, name, msg[i + 1:i + 1 + n])
            i += 1 + n
        elif b in DIACRITIC:
            yield ('text', msg[i:i + 2])
            i += 2
        else:
            yield ('text', msg[i:i + 1])
            i += 1


def render(prg, tbl, msg):
    out = []
    for item in parse_message(prg, msg):
        if item[0] == 'text':
            raw = item[1]
            out.append(tbl.get(raw) or ''.join(
                tbl.get(bytes([c]), '<%02X>' % c) for c in raw))
        else:
            _, op, name, args = item
            if op == 0xF5:
                out.append('\n')
            elif op != 0xFF:
                out.append('[%s%s]' % (name, (' ' + args.hex(' ')) if args else ''))
                if op in PAGE_CODES:
                    out.append('\n')   # cosmetic; encode() drops it
    return ''.join(out)


PAGE_CODES = (0xF4, 0xD3)
CODE_BY_NAME = {name: op for op, (name, _) in CODES.items()}


def encode(tbl, text):
    """Inverse of render(): dump text -> message bytes (with final FF)."""
    rev = {v: k for k, v in tbl.items() if v != '\n'}
    out, i = bytearray(), 0
    while i < len(text):
        c = text[i]
        if c == '[':
            j = text.index(']', i)
            name, *args = text[i + 1:j].split()
            op = CODE_BY_NAME[name]
            out.append(op)
            out += bytes(int(a, 16) for a in args)
            i = j + 1
            if op in PAGE_CODES and text.startswith('\n', i):
                i += 1
        elif c == '<':
            out.append(int(text[i + 1:i + 3], 16))
            i += 4
        elif c == '\n':
            out.append(0xF5)
            i += 1
        elif c in rev:
            out += rev[c]
            i += 1
        else:
            raise ValueError('no encoding for %r at %d' % (c, i))
    out.append(0xFF)
    return bytes(out)


VERB_LIST = 0xBE36   # bank 3; printed by $DE6C via a fixed address
DUMP_CHUNK = 0x80    # messages per dump file


def label(mid, bank, addr):
    note = ''
    if bank == 3 and addr >= VERB_LIST:
        note = '  verb list (fixed address $BE36)'
    return '@@ %03X  bank%d $%04X%s' % (mid, bank, addr, note)


def dump(prg, tbl, outdir):
    """Write script/jp/msg_XXX.txt; EN blocks start as a copy of JP."""
    msgs = all_messages(prg)
    # drop the trailing $FF padding of bank 3 (empty messages at the end)
    while len(msgs[-1][3]) == 1:
        msgs.pop()
    os.makedirs(outdir, exist_ok=True)
    for start in range(0, msgs[-1][0] + 1, DUMP_CHUNK):
        chunk = [m for m in msgs if start <= m[0] < start + DUMP_CHUNK]
        path = os.path.join(outdir, 'msg_%03X.txt' % start)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(HEADER % (start, start + DUMP_CHUNK - 1))
            for mid, bank, addr, m in chunk:
                text = render(prg, tbl, m)
                fh.write('%s\nJP:\n%s\nEN:\n%s\n\n' % (label(mid, bank, addr), text, text))
    return msgs


HEADER = """\
# Be-Bop High School script, messages %03X-%03X.
# Each message: "@@ ID ..." line, then JP: and EN: blocks.
# Translate by replacing the Japanese text in the EN block only.
#  - Keep every [code ...] exactly, in the same order (they are game logic).
#  - A line break in the text is a real newline; [page] waits for a button
#    and clears the box (the newline after it is cosmetic).
#  - <XX> is a raw tile; leave as-is unless told otherwise.
#  - Empty blocks are empty messages; leave them empty.

"""


def roundtrip(prg, tbl):
    bad = 0
    for mid, bank, addr, m in all_messages(prg):
        if encode(tbl, render(prg, tbl, m)) != m:
            bad += 1
            if bad <= 5:
                print('mismatch %03X' % mid)
    print('round-trip mismatches: %d' % bad)


def all_messages(prg):
    """(id, bank, addr, bytes) for every reachable message."""
    msgs = [(n, 2, a, m) for n, (a, m) in enumerate(split_messages(prg, 2))
            if n < BANK3_FIRST_ID]
    msgs += [(BANK3_FIRST_ID + n, 3, a, m)
             for n, (a, m) in enumerate(split_messages(prg, 3))
             if a < 0xBFF0]   # skip the reset stub at the end of the bank
    return msgs


def check(prg, tbl):
    msgs = all_messages(prg)
    problems = 0
    for mid, bank, addr, m in msgs:
        try:
            items = list(parse_message(prg, m))
            if items[-1][:2] != ('code', 0xFF) or sum(len(x[1]) if x[0] == 'text' else 1 + len(x[3]) for x in items) != len(m):
                raise ValueError('did not end cleanly on FF')
            for x in items:
                if x[0] == 'text' and any(0xA0 <= c != 0xFE for c in x[1]):
                    raise ValueError('unknown byte %s' % x[1].hex())
        except (ValueError, IndexError) as e:
            problems += 1
            if problems <= 15:
                print('%03X b%d:%04X %s: %s' % (mid, bank, addr, e, m[:24].hex(' ')))
    b2 = sum(1 for x in msgs if x[1] == 2)
    print('messages: bank2 %d, bank3 %d; problems %d' % (b2, len(msgs) - b2, problems))


if __name__ == '__main__':
    prg, tbl = load_prg(), load_table()
    if sys.argv[1] == 'check':
        check(prg, tbl)
        roundtrip(prg, tbl)
    elif sys.argv[1] == 'dump':
        msgs = dump(prg, tbl, os.path.join(ROOT, 'script', 'jp'))
        print('dumped %d messages to script/jp/' % len(msgs))
    elif sys.argv[1] == 'show':
        byid = {m[0]: m for m in all_messages(prg)}
        for a in sys.argv[2:]:
            mid, bank, addr, m = byid[int(a, 16)]
            print('== %03X  bank %d $%04X  (%d bytes)' % (mid, bank, addr, len(m)))
            print(render(prg, tbl, m))
