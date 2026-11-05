#!/usr/bin/env python3
"""Measure fight win rates from a save state at a fight menu.

usage: tools/fightodds.py STATE [--rom ROM] [--n N] [--menu KEYS]

  STATE  a RetroArch Nestopia save state (e.g. handheldsavestates/
         bebop_en.state3), standing at a fight scene's menu
  --rom  ROM to run it on (default out/bebop_en.nes)
  --n    timings per luck grade (default 128)
  --menu buttons from the menu to the fight verb (default "down,a":
         Talk / Thump / Leave)

For each luck grade (JINX..CHARM, flags $71AD-$71B1) it loads the state,
waits k frames (k = 0..N-1, so the $70 counter differs), picks the fight
and reads the outcome $037E (0/1 win, 2/3 loss; set by $E2FF just after
the roll). See PLAN.md "Fights" for the odds table.
"""
import argparse
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lrnes import Core  # noqa: E402

ROOT = os.path.dirname(HERE)
GRADES = ['JINX', 'BAD', 'NORMAL', 'GOOD', 'CHARM']
LUCK, OUTCOME = 0x71AD, 0x37E
SETTLE = 60                     # frames after the button for the roll to happen


def read_state(path):
    """RetroArch state (RZIP-compressed or not) -> the core's own blob."""
    raw = open(path, 'rb').read()
    if raw[:8] == b'#RZIPv\x01#':
        total = struct.unpack('<Q', raw[12:20])[0]
        o, out = 20, b''
        while o < len(raw):
            n = struct.unpack('<I', raw[o:o + 4])[0]
            out += zlib.decompress(raw[o + 4:o + 4 + n])
            o += 4 + n
        assert len(out) == total
        raw = out
    if raw[:8] == b'RASTATE\x01':           # RetroArch wrapper: MEM block
        assert raw[8:12] == b'MEM '
        n = struct.unpack('<I', raw[12:16])[0]
        raw = raw[16:16 + n]
    return raw


def fight(c, state, grade, wait, keys, settle=SETTLE):
    c.load(state)
    for i in range(5):
        c.poke(LUCK + i, 1 if i == grade else 0)
    c.run(1 + wait)
    for k in keys[:-1]:
        c.press(k, 5)
        c.run(20)
    c.press(keys[-1], 5)
    c.run(settle)
    return c.ram()[OUTCOME]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('state')
    ap.add_argument('--rom', default=os.path.join(ROOT, 'out', 'bebop_en.nes'))
    ap.add_argument('--n', type=int, default=128)
    ap.add_argument('--menu', default='down,a')
    a = ap.parse_args()
    keys = a.menu.split(',')
    state = read_state(a.state)
    c = Core(a.rom)
    c.run(60)
    for g, name in enumerate(GRADES):
        outs = [0] * 4
        for k in range(a.n):
            outs[fight(c, state, g, k, keys)] += 1
        wins = outs[0] + outs[1]
        print('%-6s win %3d/%d = %5.1f%%  outcomes 0-3: %s' % (name, wins, a.n, 100 * wins / a.n, outs),
              flush=True)


if __name__ == '__main__':
    main()
