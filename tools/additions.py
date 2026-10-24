"""Messages added by the translation (not in the Japanese script).

They get new IDs after the last original message ($3C1, the end of the
verb list), so original IDs are unchanged. The English files in
script/en/ mirror the Japanese dump one-to-one, so additions live here.
Each entry: ID -> (text in dump format, fixed-bank patches that use it).
"""

import re

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
# shot. Each finishes the page after "Now clear off.": lines 3-4 (<= 23).
CARETAKER_SIGNOFF = FIRST_ID + 3
SIGNOFFS = [
    "Those gutters won't\nunblock themselves.\n",
    "That boiler won't\nfix itself.\n",
    "There's a leaky tap\nwith my name on it.\n",
    "My tea's going cold.\n",
]
SIGNOFF_FIRST = FIRST_ID + 4
# Caretaker extras (PLAN.md, 2026-10-23): the scene now goes to CHOOSER,
# which shows menu $09 (Talk / Ask / Beg / Leave) until Beg sets
# FLAG_BEGGED, then menu $0A (+ Promise / Flatter).
FIRST_EXTRA = FIRST_ID + 11
(CHOOSER, MENU_SMALL, MENU_BIG, CARETAKER_ASK, BEG, BEG_FIRST, BEG_AGAIN, BEG_BEFORE,
 BEG_AFTER, PROMISE, PROMISE_FIRST, PROMISE_AGAIN, FLATTER, ASK_SIGNOFF) = range(FIRST_EXTRA, FIRST_EXTRA + 14)
# Sign-offs are split: Talk ends at CARETAKER_SIGNOFF (-> SIGNOFFS 0/1),
# Ask at ASK_SIGNOFF (-> SIGNOFFS 2/3), so one visit never repeats one.
FLAG_BEGGED, FLAG_CHEAT = 0x0B, 0x0C       # unused by script and code; saved with the game
MENU_SMALL_ID, MENU_BIG_ID = 0x09, 0x0A    # all-zero rows the script never uses
MENU_TABLE = 0xDEB3
V_TALK, V_ASK, V_LEAVE, V_FLATTER, V_PROMISE, V_BEG = 0x01, 0x02, 0x07, 0x08, 0x0B, 0x13
MENU_ROWS = {MENU_SMALL_ID: [V_TALK, V_ASK, V_BEG, V_LEAVE, 0, 0],
             MENU_BIG_ID: [V_TALK, V_ASK, V_BEG, V_PROMISE, V_FLATTER, V_LEAVE]}


def _id(n):
    return '%02x %02x' % (n & 0xFF, n >> 8)


# Each answer just ends: [menu] runs it as a nested call, and CHOOSER's
# ifflag-call then re-runs CHOOSER, so the menu reflects FLAG_BEGGED at
# once. (Ending answers with a goto back to the menu instead left a call
# frame on the 6502 stack every time round, and a long visit crashed;
# Stephen, 2026-10-23.)
BACK = ''
SCENE = "[cmdDE 22][cmdF0 25][cmdEF 38][goto %s]\n" % _id(CHOOSER)
EXTRAS = {
    CHOOSER: '[ifflag-call %02x %s %s]\n' % (FLAG_BEGGED, _id(MENU_SMALL), _id(MENU_BIG)),
    MENU_SMALL: '[menu %02x %s %s %s 09 03]\n' % (
        MENU_SMALL_ID, _id(CARETAKER_TALK), _id(CARETAKER_ASK), _id(BEG)),
    MENU_BIG: '[menu %02x %s %s %s %s %s 09 03]\n' % (
        MENU_BIG_ID, _id(CARETAKER_TALK), _id(CARETAKER_ASK), _id(BEG), _id(PROMISE), _id(FLATTER)),
    BEG: '[ifflag %02x %s %s]\n' % (FLAG_BEGGED, _id(BEG_FIRST), _id(BEG_AGAIN)),
    BEG_FIRST: ('[setflag %02x]' % FLAG_BEGGED +
                "Got yourselves into a bit\nof bother, lads? Well, I\nknow people. Comes with\nmy age, that does.[page]\n"
                "Now, this isn't how\nthings are meant to be.\nIt's an easier road than\nlads like you deserve.[page]\n"
                "First, I can see to it\nyou always draw the very\nbest fortune slip at the\nshrine.[page]\n"
                "You'll have to promise\nto use it for good deeds,\nmind. Once it's done,\nthere's no going back.[page]\n"
                "I also hear things on the\ngrapevine. Flatter me a\nbit, and I'll give you\nthe latest lowdown." + BACK),
    BEG_AGAIN: '[ifflag %02x %s %s]\n' % (FLAG_CHEAT, _id(BEG_BEFORE), _id(BEG_AFTER)),
    BEG_BEFORE: "Still thinking, lads?\nPromise me, and the best\nfortune's yours. Flatter\nme for the lowdown." + BACK,
    BEG_AFTER: "You've had your favours,\nlads. Flatter me for\nthe lowdown." + BACK,
    PROMISE: '[ifflag %02x %s %s]\n' % (FLAG_CHEAT, _id(PROMISE_FIRST), _id(PROMISE_AGAIN)),
    PROMISE_FIRST: ('[setflag %02x]' % FLAG_CHEAT +
                    "I trust you, lads. It's\ndone. The priest owes me\nfor all the odd jobs I've\ndone round the shrine." + BACK),
    PROMISE_AGAIN: "Your fortune's already\nsorted, lads. A promise\nis a promise." + BACK,
    # stage 1 placeholder; stage 2 picks a hint by story progress
    FLATTER: "Ooh, such kind words.\nYou're only just starting\nout. Have a wander round\nand talk to folk." + BACK,
}
SIGNOFFS = [t.rstrip('\n') + BACK for t in SIGNOFFS]
# Talk = how NERVE works; Ask = luck and saving (split 2026-10-23)
HELP = (
    "[cmdEE 00]Hm? Oh, it's you lot.\nBeen keeping this place\ngoing as caretaker since\nbefore your time.[page]\n"
    "I've seen plenty of\nlads like you come\nthrough. Here's some\nadvice for nothing.[page]\n"
    "Win a scrap, and your\nNERVE goes up. Lose one,\nor get knocked back by a\ngirl, and down it goes.[page]\n"
    "Run out completely, and\nyou're done for. And\nsleep won't top it up,\nmind.[page]\n"
    "Get home to bed in\nthe evening before\nnightfall.[page]\n"
    "Stay out late and it\nwears you down, or the\npolice nab you.[page]\n"
    "Right, that's your lot.\nNow clear off.\n[goto %s]\n" % _id(CARETAKER_SIGNOFF)
)
ASK_TEXT = (
    "[cmdEE 00]I turn a blind eye to\nwhat the students get up\nto, but I'll tell you\nthis...[page]\n"
    "First thing each day,\npop up to the shrine and\nbuy a fortune slip. It\nsays how your LUCK is.[page]\n"
    "Luck's everything, lads.\nGood luck, and folk open\nup to you. Bad luck, and\nnothing goes right.[page]\n"
    "Oh, and you can only save\nat home. Now clear off.\n[goto %s]\n" % _id(ASK_SIGNOFF)
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

# 1AE (Nobuo: "don't just use me as your dogsbody") answers Watch on the
# roof, Search at the station and Use at the car (2E9/2EA). At the car the
# JP is a pun: Use (つかう) sounds like using *him*, and his complaint
# つかいっぱしり (errand boy) starts with つかい. The car gets its own copy
# that says so (Stephen, 2026-10-22).
NOBUO_USED = FIRST_ID + 10
NOBUO_USED_TEXT = ("[cmdEF 34][cmdEE 0f]Using me again, Guv? I'm\n"
                   "not just your dogsbody.\nLet me prove I'm a man.\n")


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

    used = '%02x %02x' % (NOBUO_USED & 0xFF, NOBUO_USED >> 8)
    for scene in (0x2E9, 0x2EA):
        menu = re.search(r'\[menu 4f 97 01 ae 01 ([0-9a-f]{2} [0-9a-f]{2}) 36 02 09 03\]', msgs[scene])
        assert menu, msgs[scene]
        msgs[scene] = msgs[scene].replace(menu.group(0), '[menu 4f 97 01 %s %s 36 02 09 03]'
                                          % (used, menu.group(1)))


MESSAGES = {FIRST_ID: OUT_OF_NERVE, CARETAKER_SCENE: SCENE, CARETAKER_TALK: HELP,
            CARETAKER_SIGNOFF: SIGNOFFS[0]}
MESSAGES.update({SIGNOFF_FIRST + i: t for i, t in enumerate(SIGNOFFS)})
MESSAGES[NOBUO_USE] = ''          # filled in by retarget() from 1B3
MESSAGES[NOBUO_STEADY] = ''       # filled in by retarget() from 1B6
MESSAGES[NOBUO_USED] = NOBUO_USED_TEXT
MESSAGES.update(EXTRAS)
MESSAGES[CARETAKER_ASK] = ASK_TEXT
MESSAGES[ASK_SIGNOFF] = SIGNOFFS[2]   # replaced at run time, like CARETAKER_SIGNOFF

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
for _mid, _row in MENU_ROWS.items():
    PATCHES.append((MENU_TABLE + _mid * 6, bytes(6), bytes(_row)))

# Luck cheat: the fortune slip roll ($E382) starts JSR $EE37 (clear the
# luck flags $71AD-$71B1), then rolls Y = 0..4 and sets $71AD,Y at $E391.
# The helper clears as before; with FLAG_CHEAT set it drops the return
# address and jumps to $E391 with Y = 4 (CHARM).
CHEAT_HELPER = 0xFFB0
_cheat = bytes([0x20, 0x37, 0xEE,                        # JSR $EE37
                0xAD, FLAG_CHEAT, 0x71,                  # LDA $71xx (cheat flag)
                0xF0, 0x07,                              # BEQ rts
                0x68, 0x68,                              # PLA / PLA
                0xA0, 0x04,                              # LDY #4 (CHARM)
                0x4C, 0x91, 0xE3,                        # JMP $E391
                0x60])                                   # rts: RTS
assert len(_cheat) == 16
# Original bug (found by Stephen, 2026-10-24): the clock tick ($C411) adds
# a minute ($71C5) and moves to the next hour only when it EQUALS $38. The
# new-day routines (sleep, Nobuo's overnight stakeout: $C3F5, $C3D1) set
# 7:00 but INC the minutes instead of clearing them, so from minute
# $36/$37 they skip past $38; the minutes then run round to 0 (~3.5 real
# minutes) with the hour still 7, and the 7:00 reset fires again: luck
# back to JINX, today's slip forgotten. BNE -> BCC: roll over at >= $38.
PATCHES.append((0xC41F, bytes([0xD0, 0x23]), bytes([0x90, 0x23])))

PATCHES += [
    (CHEAT_HELPER, b'\xFF' * len(_cheat), _cheat),
    (0xE382, bytes([0x20, 0x37, 0xEE]), bytes([0x20, CHEAT_HELPER & 0xFF, CHEAT_HELPER >> 8])),
]
