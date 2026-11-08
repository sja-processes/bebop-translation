#!/usr/bin/env python3
"""Show one message on screen in headless Nestopia, box by box.

usage: tools/showmsg.py ID [--boxes N] [--hero 0|1] [OUT.png]

Builds out/showmsg.nes with the intro (message $238) jumping straight to
message ID, starts a new game, and captures each box after it has
printed (pressing A between boxes), N boxes (default: [page] count + 1,
plus one for a [page+goto]). The frames go side by side into OUT.png
(default out/msgID.png). Faces, layout and the follow-on message show
as in the game, though the scene behind is the intro's, and game-state
codes run as they would there.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import insert  # noqa: E402

ROOT = os.path.dirname(HERE)
INTRO = 0x238
HERO = 0x71B5


def build(msg, path):
    orig = insert.english_messages

    def patched():
        m = orig()
        m[INTRO] = '[goto %02x %02x]\n' % (msg & 0xFF, msg >> 8)
        return m
    insert.english_messages = patched
    try:
        _, new, *_ = insert.build()
    finally:
        insert.english_messages = orig
    open(path, 'wb').write(new)
    return insert.english_messages()[msg]


def settle(c, quiet=130, limit=1200):
    """Run until the box has finished printing: nothing new on screen for
    `quiet` frames (letters come every 1-3 frames, [delay] pauses are up
    to 120; the waiting arrow's blink, 16 frames, doesn't count as new).
    -> that frame; if the screen starts fading first (a closing message
    with no wait moves straight on), the last frame before the fade."""
    seen = []                                   # the last two distinct frames
    shown = None
    since = 0
    for _ in range(limit):
        c.run(1)
        now = c.frame[2]
        if now.count(b"\xff\xff\xff") < 1000:    # fading out (the box is pure white)
            if shown:
                return shown
            continue
        if now in seen:
            since += 1
        else:
            seen = (seen + [now])[-2:]
            since = 0
            shown = now
        if since >= quiet:
            return now
    return shown or c.frame[2]


def main():
    from lrnes import Core
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('id')
    ap.add_argument('--boxes', type=int)
    ap.add_argument('--hero', type=int, choices=(0, 1))
    ap.add_argument('out', nargs='?')
    a = ap.parse_args()
    msg = int(a.id, 16)
    rom = os.path.join(ROOT, 'out', 'showmsg.nes')
    text = build(msg, rom)
    boxes = a.boxes or text.count('[page]') + 1 + text.count('[page+goto')
    c = Core(rom)
    c.run(600)
    c.press('start', 5)
    c.run(5)
    if a.hero is not None:
        c.poke(HERO, a.hero)
    c.run(400)                          # past the fade-in
    frame = settle(c)
    shots = []
    for i in range(boxes):
        if i:
            c.press('a', 5)
            c.run(20)                       # let the old box clear
            frame = settle(c)
        shots.append(Image.frombytes('RGB', (256, 240), frame))
    sheet = Image.new('RGB', (256 * len(shots), 240))
    for i, im in enumerate(shots):
        sheet.paste(im, (256 * i, 0))
    out = a.out or os.path.join(ROOT, 'out', 'msg%03X.png' % msg)
    sheet.resize((sheet.width * 2, 480), Image.NEAREST).save(out)
    c.close()
    print('%03X: %d box(es) -> %s' % (msg, boxes, out))


if __name__ == '__main__':
    main()
