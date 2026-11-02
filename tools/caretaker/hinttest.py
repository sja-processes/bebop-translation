#!/usr/bin/env python3
"""Test the caretaker's Flatter hints (hints.py) in headless Nestopia.

usage: tools/caretaker/hinttest.py [OUT.png]

  1. Static check: every [clrflag] in the script that clears a hint's
     opening flag must set a later hint's flag in the same message, or
     Flatter falls back a hint (as taking the sign did, 2026-11-02).
     Known-harmless clears are listed in SAFE_CLEARS with the reason.
  2. Builds out/hinttest.nes: the intro (message $238) jumps straight to
     the caretaker's room, so a new game starts there.
  3. For each hint: new game, Beg flag + every opening flag up to that
     hint set, Flatter, first box captured. Then the fallback cases in
     CLEARED (flags the game clears mid-story). All frames go into one
     grid (default out/hinttest.png) to check by eye.

The test ROM is a build product (out/ is gitignored); never commit it.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import hints  # noqa: E402

TEST_ROM = os.path.join(ROOT, 'out', 'hinttest.nes')
INTRO = 0x238
FLAG_BASE = 0x7100

# message: why clearing a hint flag there can't send Flatter back
SAFE_CLEARS = {
    0x14D: 'Higashimachi lad clears 1B; only reachable after 51, never cleared',
}
# fallback cases: (every opening flag up to this one set, flags then
# cleared as the game does); each must still show that flag's hint
CLEARED = [
    (0x09, [0x07]),                            # sign taken (191 clears 07) -> H04
    (0x84, [0x44]),                            # Misako's coffee (127 clears 44) -> H29
    (0x51, [0x53, 0x54]),                      # after the ride (3A3/3A4) -> H36
]


def opening_flags():
    return [f for f, _ in hints.HINTS]


def script_messages():
    msgs = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'script/en/msg_*.txt'))):
        cur = None
        for line in open(path):
            m = re.match(r'@@ (\w+)', line)
            if m:
                cur = int(m.group(1), 16)
                msgs[cur] = ''
            elif cur is not None and not line.startswith('EN:'):
                msgs[cur] += line
    return msgs


def check_clears():
    """-> list of problems (empty when every clear is covered)."""
    flags = opening_flags()
    problems = []
    for mid, text in script_messages().items():
        sets = {int(x, 16) for x in re.findall(r'\[setflag (\w+)\]', text)}
        for x in re.findall(r'\[clrflag (\w+)\]', text):
            f = int(x, 16)
            if f not in flags or mid in SAFE_CLEARS:
                continue
            i = flags.index(f)
            if not any(g in sets for g in flags[i + 1:]):
                problems.append('%03X clears %02X (H%02d) and sets no later hint flag' % (mid, f, i + 1))
    return problems


def build_rom(path=TEST_ROM):
    import insert
    import additions
    orig = insert.english_messages

    def patched():
        m = orig()
        sc = additions.CARETAKER_SCENE
        m[INTRO] = '[goto %02x %02x]\n' % (sc & 0xFF, sc >> 8)
        return m
    insert.english_messages = patched
    try:
        _, new, *_ = insert.build()
    finally:
        insert.english_messages = orig
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(new)
    return path


def flatter(rom, set_flags, clear_flags=()):
    """New game in the caretaker's room, flags poked, Flatter, then the
    first hint box. -> PIL image of the text box."""
    import additions
    from lrnes import Core
    from PIL import Image
    c = Core(rom)
    c.run(600)
    c.press('start', 5)
    c.run(5)
    c.poke(FLAG_BASE + additions.FLAG_BEGGED, 1)
    for f in set_flags:
        c.poke(FLAG_BASE + f, 1)
    for f in clear_flags:
        c.poke(FLAG_BASE + f, 0)
    c.run(300)
    # big menu: Talk Ask Coffee / Promise Flatter Leave, cursor on Talk
    for k in ('down', 'right', 'a'):
        c.press(k, 5)
        c.run(30)
    c.run(150)                      # "Ooh, such kind words."
    c.press('a', 5)
    c.run(400)                      # long enough for a full box to print
    w, h, rgb = c.frame
    im = Image.frombytes('RGB', (w, h), rgb).crop((0, 0, w, 55))
    c.close()
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'hinttest.png')
    problems = check_clears()
    for p in problems:
        print('PROBLEM', p)
    print('clear check: %d problem(s)' % len(problems))

    from PIL import Image
    rom = build_rom()
    flags = opening_flags()
    shots = [flatter(rom, flags[1:i + 1]) for i in range(len(flags))]
    for last, clr in CLEARED:
        shots.append(flatter(rom, flags[1:flags.index(last) + 1], clr))
    w, h = shots[0].size
    cols = 3
    sheet = Image.new('RGB', (w * cols, h * -(-len(shots) // cols)), 'white')
    for i, im in enumerate(shots):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)
    print('%d hints + %d fallback cases -> %s' % (len(flags), len(CLEARED), out))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
