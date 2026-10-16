#!/usr/bin/env python3
"""Simulate the dialogue box for every message and report layout problems
the English has that the Japanese did not (stage 8a).

usage: tools/pagecheck.py [--all]   (--all also lists issues shared with JP)

Engine facts (PLAN.md "Text engine"): text starts at PPU $2084 (row 4,
col 4); newline F5 = two rows down, back to col 4; page F4 / D3 waits
with a blinking cursor drawn one space after the last character
($E155), then clears the box and starts again at $2084. The box
interior is cols 3-28 with its right border at col 29, and four text
lines (rows 4, 6, 8, 10) fit above the bottom border.
Name codes print messages $254-$257: surnames Nakama/Kato (<= 6),
given names Toru/Hiroshi (<= 7).
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
LEFT, RIGHT_BORDER = 4, 29
FIRST_ROW, LAST_ROW = 4, 10
NAME_WIDTH = {0xE1: 7, 0xDF: 7, 0xE2: 6, 0xE0: 6}
PAGE = (0xF4, 0xD3)
JUMPS = (0xF2, 0xF1)          # goto / call continue at the cursor
# messages that are not drawn in the dialogue box
NOT_DIALOGUE = set(range(0x3AA, 0x3C2)) | set(range(0x254, 0x258)) | \
    set(range(0x37A, 0x37F))


def simulate(prg, data):
    """-> list of (kind, page_no, detail) for one encoded message."""
    issues = []
    row, col, page = FIRST_ROW, LEFT, 1
    line = 0
    for item in script.parse_message(prg, data):
        if item[0] == 'text':
            col += 1
            line += 1
            if col - 1 >= RIGHT_BORDER:
                issues.append(('line past box edge', page, line))
            if row > LAST_ROW:
                issues.append(('text below the box', page, row))
            continue
        op = item[1]
        if op in NAME_WIDTH:
            col += NAME_WIDTH[op]
            line += NAME_WIDTH[op]
            if col - 1 >= RIGHT_BORDER:
                issues.append(('line past box edge', page, line))
            if row > LAST_ROW:
                issues.append(('text below the box', page, row))
        elif op == 0xF5:
            row, col, line = row + 2, LEFT, 0
        elif op in PAGE:
            if row > LAST_ROW:
                issues.append(('page cursor below the box', page, row))
            elif col + 1 >= RIGHT_BORDER:
                issues.append(('page cursor on box border', page, col + 1))
            row, col, line, page = FIRST_ROW, LEFT, 0, page + 1
        elif op in JUMPS and row > LAST_ROW:
            issues.append(('jumps on with cursor below the box', page, row))
    # collapse duplicates (one report per kind and page)
    seen, out = set(), []
    for k, p, d in issues:
        if (k, p) not in seen:
            seen.add((k, p))
            out.append((k, p, d))
    return out


def main():
    show_all = '--all' in sys.argv
    prg = script.load_prg()
    tbl = {bytes([t]): ch for ch, t in font.char_map().items()}
    en, jp = {}, {}
    for f in glob.glob(os.path.join(ROOT, 'script/en/*.txt')):
        en.update(encheck.parse(f, 'EN'))
    msgs = {mid: m for mid, _, _, m in script.all_messages(prg)}
    total = 0
    for mid in sorted(en):
        if mid in NOT_DIALOGUE or mid not in msgs:
            continue
        try:
            data = script.encode(tbl, en[mid][1])
        except (ValueError, KeyError) as e:
            print('%03X: cannot encode: %s' % (mid, e))
            total += 1
            continue
        mine = simulate(prg, data)
        orig = {(k, p) for k, p, _ in simulate(prg, msgs[mid])}
        for k, p, d in mine:
            shared = (k, p) in orig
            if shared and not show_all:
                continue
            total += 1
            print('%03X page %d: %s%s' % (mid, p, k, ' (also in JP)' if shared else ''))
    print('%d issue(s)' % total)


if __name__ == '__main__':
    main()
