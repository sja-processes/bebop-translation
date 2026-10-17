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
    "off. Those gutters won't\nclear themselves.\n",
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
    "That NERVE of yours.\nLose a scrap, or get\nknocked back by a girl,\nand down it goes.[page]\n"
    "A good night's sleep at\nhome puts it right. But\nrun out completely, and\nyou're done for.[page]\n"
    "Don't go wandering about\nafter dark, either. Wears\nyou out, and the police\nwill have you.[page]\n"
    "First thing each day,\npop up to the shrine and\nbuy a fortune slip. It\nsays how your LUCK is.[page]\n"
    "Luck's everything, lads.\nGood luck, and folk open\nup to you. Bad luck, and\nnothing goes right.[page]\n"
    "Oh, and you can only\nsave at home. Now clear\n[goto %02x %02x]\n" % (CARETAKER_SIGNOFF & 0xFF, CARETAKER_SIGNOFF >> 8)
)

MESSAGES = {FIRST_ID: OUT_OF_NERVE, CARETAKER_SCENE: SCENE, CARETAKER_TALK: HELP,
            CARETAKER_SIGNOFF: SIGNOFFS[0]}
MESSAGES.update({SIGNOFF_FIRST + i: t for i, t in enumerate(SIGNOFFS)})

# (CPU address in the fixed bank, original bytes, new bytes)
PATCHES = [
    (0xE8DE, bytes([0xA2, 0xC4, 0xA0, 0x01]),                 # LDX #$C4 / LDY #$01
     bytes([0xA2, FIRST_ID & 0xFF, 0xA0, FIRST_ID >> 8])),
]
