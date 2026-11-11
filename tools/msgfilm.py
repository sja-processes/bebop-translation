#!/usr/bin/env python3
"""Film one message in headless Nestopia: a frame every STEP frames.

usage: tools/msgfilm.py ID [--frames N] [--step S] [--cols C] [OUT.png]

Like showmsg.py (the intro, message $238, jumps straight to ID), but
for messages that are sequences rather than text: a train ride, a scene
change. Starts a new game and grabs a frame every S frames (default 30)
for N frames (default 900), pressing A every second so boxes move on,
and lays them out C to a row (default 10) in OUT.png (default
out/filmID.png). Each frame is labelled with its frame count.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import showmsg  # noqa: E402

ROOT = os.path.dirname(HERE)


def main():
    from lrnes import Core
    from PIL import Image, ImageDraw
    ap = argparse.ArgumentParser()
    ap.add_argument('id')
    ap.add_argument('--frames', type=int, default=900)
    ap.add_argument('--step', type=int, default=30)
    ap.add_argument('--cols', type=int, default=10)
    ap.add_argument('out', nargs='?')
    a = ap.parse_args()
    msg = int(a.id, 16)
    rom = os.path.join(ROOT, 'out', 'showmsg.nes')
    showmsg.build(msg, rom)
    c = Core(rom)
    c.run(600)
    c.press('start', 5)
    shots = []
    for f in range(0, a.frames, a.step):
        if f and f % 60 == 0:
            c.press('a', 5)
            c.run(a.step - 5)
        else:
            c.run(a.step)
        im = Image.frombytes('RGB', (256, 240), c.frame[2])
        ImageDraw.Draw(im).text((4, 4), str(f + a.step), fill=(255, 0, 0))
        shots.append(im)
    c.close()
    cols = min(a.cols, len(shots))
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (256 * cols, 240 * rows))
    for i, im in enumerate(shots):
        sheet.paste(im, (256 * (i % cols), 240 * (i // cols)))
    out = a.out or os.path.join(ROOT, 'out', 'film%03X.png' % msg)
    sheet.save(out)
    print('%03X: %d frames -> %s' % (msg, len(shots), out))


if __name__ == '__main__':
    main()
