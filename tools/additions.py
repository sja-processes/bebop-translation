"""Messages added by the translation (not in the Japanese script).

They get new IDs after the last original message ($3C1, the end of the
verb list), so original IDs are unchanged. The English files in
script/en/ mirror the Japanese dump one-to-one, so additions live here.
Each entry: ID -> (text in dump format, fixed-bank patches that use it).
"""

FIRST_ID = 0x3C2

# QoL (Stephen, 2026-10-17): running out of NERVE ($E8 handler, $E8D7)
# jumped straight to the shared ending 1C4 ("Guv..." / "Youthful folly,
# eh."), also used by the arrest and car-charge endings, so the player
# couldn't tell why the game ended. This copy of 1C4 replaces its first
# page with the reason; the out-of-NERVE code is pointed at it.
OUT_OF_NERVE = (
    "[cmdDE 26][cmdEF 34][cmdEE 07]Guv, you've lost your\n"
    "nerve. We're finished![page]\n"
    "[cmdEE 11]Youthful folly, eh.\n"
    "[page+goto 1b 02]\n"
)

# Caretaker's room (optional help, PLAN.md): the scene opened by the new
# door (tools/caretaker/build.py) and his help pages. Picture $25 and
# character $38 are new. Menu $41 = Talk / Leave; $0309 is the game's own
# empty Leave target.
CARETAKER_SCENE = FIRST_ID + 1
CARETAKER_TALK = FIRST_ID + 2
# The last page ends by going to CARETAKER_SIGNOFF; tools/caretaker/build.py
# makes the message lookup swap that ID for one of the four SIGNOFFS,
# picked by the frame counter, so repeat visits get a different parting
# shot. Each finishes the page: line 3 (<= 25) and line 4 (<= 23).
CARETAKER_SIGNOFF = FIRST_ID + 3
SIGNOFFS = [
    "off. Those gutters won't\nunblock themselves.\n",
    "off. That boiler won't\nfix itself.\n",
    "off. There's a leaky tap\nwith my name on it.\n",
    "off. My tea's going\ncold.\n",
]
SIGNOFF_FIRST = FIRST_ID + 4
SCENE = "[cmdDE 22][cmdF0 25][cmdEF 38][menu-call 41 %02x %02x 09 03]\n" % (
    CARETAKER_TALK & 0xFF, CARETAKER_TALK >> 8)
HELP = (
    "[cmdEE 00]Hm? Oh, it's you lot.\nBeen keeping this place\ngoing as caretaker since\nbefore your time.[page]\n"
    "I've seen plenty of\nlads like you come\nthrough. Here's some\nadvice for nothing.[page]\n"
    "Win a scrap, and your\nNERVE goes up. Lose one,\nor get knocked back by a\ngirl, and down it goes.[page]\n"
    "Run out completely, and\nyou're done for. And\nsleep won't top it up,\nmind.[page]\n"
    "Get home to bed in\nthe evening before\nnightfall.[page]\n"
    "Stay out late and it\nwears you down, or the\npolice nab you.[page]\n"
    "First thing each day,\npop up to the shrine and\nbuy a fortune slip. It\nsays how your LUCK is.[page]\n"
    "Luck's everything, lads.\nGood luck, and folk open\nup to you. Bad luck, and\nnothing goes right.[page]\n"
    "Oh, and you can only\nsave at home. Now clear\n[goto %02x %02x]\n" % (CARETAKER_SIGNOFF & 0xFF, CARETAKER_SIGNOFF >> 8)
)

# 1B3 (Nobuo charges off) answers two verbs: Flatter (ごまする, butter
# up) in the Risa scene 2C6 -- you butter Nobuo up and he gets carried
# away -- and Use (つかう) in scene 2EB. The English 1B3 bridges the
# flattery ("Oh, you flatter me, Guv..."), so Use gets a copy
# that keeps the original opening; 2EB's menu is pointed at it at build
# time (the script files keep the Japanese-matching targets).
NOBUO_USE = FIRST_ID + 8
NOBUO_USE_OPENING = "[cmdEF 34][cmdEE 14]Leave it to me, Guv.[page]\n"

# Misako's coffee-shop date (scene 2C5, menu $20, used nowhere else): the
# JP menu offers のる (Ride) as a cheeky option, but English "Ride" reads
# as an outright request. Stephen (2026-10-21): use Give instead ("give
# her a present" / "give her one"), one byte in the menu table. Her reply
# 07F becomes "Wh-what?!", and Nobuo's yelp after Give and Sleep gets its
# own copy of 1B6, which the sake shop girl's scene still shares as a
# lovestruck "Guuuv!".
NOBUO_STEADY = FIRST_ID + 9
MISAKO_MENU_GIVE = 0xDEB3 + 0x20 * 6 + 4          # menu $20, slot 5
VERB_RIDE, VERB_GIVE = 0x16, 0x14


def retarget(msgs):
    """Build-time script changes that would break encheck's JP match."""
    flatter = msgs[0x1B3]
    first, rest = flatter.split('[page]\n', 1)
    assert 'flatter' in first, first
    msgs[NOBUO_USE] = NOBUO_USE_OPENING + rest
    menu = '[menu 63 e1 01 b3 01 b0 01 b1 01 b2 01 09 03]'
    assert msgs[0x2EB].count(menu) == 1, msgs[0x2EB]
    msgs[0x2EB] = msgs[0x2EB].replace(menu, '[menu 63 e1 01 %02x %02x b0 01 b1 01 b2 01 09 03]'
                                      % (NOBUO_USE & 0xFF, NOBUO_USE >> 8))

    assert msgs[0x1B6].count('Guuuv!') == 1, msgs[0x1B6]
    msgs[NOBUO_STEADY] = msgs[0x1B6].replace('Guuuv!', 'Cor, Guv! Steady on!')
    steady = '%02x %02x' % (NOBUO_STEADY & 0xFF, NOBUO_STEADY >> 8)
    menu = '[menu-call 20 7c 00 7d 00 b6 01 7e 00 7f 00 09 03]'
    assert msgs[0x2C5].count(menu) == 1, msgs[0x2C5]
    msgs[0x2C5] = msgs[0x2C5].replace(menu, '[menu-call 20 7c 00 7d 00 %s 7e 00 7f 00 09 03]' % steady)
    assert msgs[0x07F].count('[page+goto b6 01]') == 1, msgs[0x07F]
    msgs[0x07F] = msgs[0x07F].replace('[page+goto b6 01]', '[page+goto %s]' % steady)


MESSAGES = {FIRST_ID: OUT_OF_NERVE, CARETAKER_SCENE: SCENE, CARETAKER_TALK: HELP,
            CARETAKER_SIGNOFF: SIGNOFFS[0]}
MESSAGES.update({SIGNOFF_FIRST + i: t for i, t in enumerate(SIGNOFFS)})
MESSAGES[NOBUO_USE] = ''          # filled in by retarget() from 1B3
MESSAGES[NOBUO_STEADY] = ''       # filled in by retarget() from 1B6

# The out-of-NERVE path ($E8D7) doesn't reset the text cursor, so the
# message starts wherever the last line left off; the original's one-line
# first page fitted, but ours has two. A helper at $FFC0 runs the
# original box routine then $E9AC (cursor back to the top-left).
NERVE_HELPER = 0xFFC0

# (CPU address in the fixed bank, original bytes, new bytes)
PATCHES = [
    (NERVE_HELPER, b'\xFF' * 6,
     bytes([0x20, 0xF5, 0xEA,                                 # JSR $EAF5
            0x4C, 0xAC, 0xE9])),                              # JMP $E9AC
    (0xE8DB, bytes([0x20, 0xF5, 0xEA]),                       # JSR $EAF5
     bytes([0x20, NERVE_HELPER & 0xFF, NERVE_HELPER >> 8])),
    (0xE8DE, bytes([0xA2, 0xC4, 0xA0, 0x01]),                 # LDX #$C4 / LDY #$01
     bytes([0xA2, FIRST_ID & 0xFF, 0xA0, FIRST_ID >> 8])),
    (MISAKO_MENU_GIVE, bytes([VERB_RIDE]), bytes([VERB_GIVE])),
]
