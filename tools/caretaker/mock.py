"""Mock-up: room + caretaker pasted into a real scene screenshot.

    python3 tools/caretaker/mock.py SCREENSHOT.png OUT.png
(the screenshot is a 512x480 frame of a scene with the menu up; not committed)"""
import sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from PIL import Image
import room as ct_room, char as ct_char
pc = ct_room.draw()
room = ct_room.render(pc)
base = Image.open(sys.argv[1]).resize((256, 240), 0)        # real screen with the menu
shots = []
for talking in (False, True):
    scr = base.copy()
    scr.paste(room, (48, 112))
    # menu 41 = Talk / Leave: blank the other verbs and move Leave to slot 2 (row 2, col 0)
    leave = base.crop((136, 61, 184, 73))
    for box in ((136, 44, 184, 57), (136, 61, 184, 73), (72, 61, 128, 73), (72, 78, 128, 90)):
        scr.paste((255, 255, 255), box)
    scr.paste(leave, (72, 61))
    ch = ct_char.image(ct_char.cells(ct_char.build(talking)), bg=None)
    scr.paste(ch, (96, 160), ch)
    shots.append(scr)
out = Image.new('RGB', (520, 240), (255, 255, 255))
out.paste(shots[0], (0, 0)); out.paste(shots[1], (264, 0))
out.resize((1040, 480), 0).save(sys.argv[2])
