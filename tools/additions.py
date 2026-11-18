"""Messages added by the translation (not in the Japanese script).

They get new IDs after the last original message ($3C1, the end of the
verb list), so original IDs are unchanged. The English files in
script/en/ mirror the Japanese dump one-to-one, so additions live here.
Each entry: ID -> (text in dump format, fixed-bank patches that use it).
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caretaker'))
import hints  # noqa: E402

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
# which shows menu $09 (Talk / Ask / Coffee / Beg / Leave) until Beg sets
# FLAG_BEGGED, then menu $0A (Beg gone; + Promise / Flatter). Beg can only
# be chosen once, so it has no repeat answers (removed 2026-10-31).
FIRST_EXTRA = FIRST_ID + 11
(CHOOSER, MENU_SMALL, MENU_BIG, CARETAKER_ASK, BEG, PROMISE, PROMISE_FIRST, PROMISE_AGAIN,
 FLATTER, ASK_SIGNOFF) = range(FIRST_EXTRA, FIRST_EXTRA + 10)
# Sign-offs are split: Talk ends at CARETAKER_SIGNOFF (-> SIGNOFFS 0/1),
# Ask at ASK_SIGNOFF (-> SIGNOFFS 2/3), so one visit never repeats one.
FLAG_BEGGED, FLAG_CHEAT = 0x0B, 0x0C       # unused by script and code; saved with the game
MENU_SMALL_ID, MENU_BIG_ID = 0x09, 0x0A    # all-zero rows the script never uses
MENU_TABLE = 0xDEB3
V_TALK, V_ASK, V_LEAVE, V_FLATTER, V_COFFEE, V_PROMISE, V_BEG = 0x01, 0x02, 0x07, 0x08, 0x09, 0x0B, 0x13
# Coffee (day goal hint, 2026-10-31) joins both menus; Beg goes once used
MENU_ROWS = {MENU_SMALL_ID: [V_TALK, V_ASK, V_COFFEE, V_BEG, V_LEAVE, 0],
             MENU_BIG_ID: [V_TALK, V_ASK, V_COFFEE, V_PROMISE, V_FLATTER, V_LEAVE]}


def _id(n):
    return '%02x %02x' % (n & 0xFF, n >> 8)


# Each answer just ends: [menu] runs it as a nested call, and CHOOSER's
# ifflag-call then re-runs CHOOSER, so the menu reflects FLAG_BEGGED at
# once. (Ending answers with a goto back to the menu instead left a call
# frame on the 6502 stack every time round, and a long visit crashed;
# Stephen, 2026-10-23.)
BACK = ''
# Day goal (PLAN.md "Day goal", Stephen 2026-10-31): Coffee tells the day
# limit for the quicker ending ($E745: 9 days for Hiroshi, 8 for Toru;
# hero = $71B5, readable as flag $B5) and points at Select (daygoal.py).
COFFEE, COFFEE_HIROSHI, COFFEE_TORU = FIRST_ID + 25, FIRST_ID + 26, FIRST_ID + 27
FLAG_HERO = 0xB5                           # 0 Hiroshi, 1 Toru
COFFEE_TEXT = ("Coffee? I'll stick to my\nown tea, lads. But since\nyou offered, here's a\n"
               "tip: don't waste time.[page]\n"
               "[cmdE1], as it's you,\nsort things out within\n%d days and you'll get\n"
               "the happiest ending.[page]\n"
               "Press Select in a chat\nto see how you're doing\nfor time.")
# Flatter hints (Stephen, 2026-11-01): one message each; FLATTER goes to
# the first whose flag is set, checking the latest step first.
# ID $3FF is skipped (left empty): its low byte would put $FF, the end
# of a message, inside the chain's arguments.
HINT_FIRST = FIRST_ID + 28
HINT_IDS = [mid for mid in range(HINT_FIRST, HINT_FIRST + len(hints.HINTS) + 1) if mid & 0xFF != 0xFF]


def _hint_chain():
    steps = [(f, mid) for (f, _), mid in zip(hints.HINTS, HINT_IDS) if f is not None]
    assert hints.HINTS[0][0] is None
    return '[firstset %s fa %s]\n' % (' '.join('%02x %s' % (f, _id(mid)) for f, mid in reversed(steps)),
                                       _id(HINT_IDS[0]))


SCENE = "[cmdDE 22][cmdF0 25][cmdEF 38][goto %s]\n" % _id(CHOOSER)
EXTRAS = {
    CHOOSER: '[ifflag-call %02x %s %s]\n' % (FLAG_BEGGED, _id(MENU_SMALL), _id(MENU_BIG)),
    MENU_SMALL: '[menu %02x %s %s %s %s 09 03]\n' % (
        MENU_SMALL_ID, _id(CARETAKER_TALK), _id(CARETAKER_ASK), _id(COFFEE), _id(BEG)),
    MENU_BIG: '[menu %02x %s %s %s %s %s 09 03]\n' % (
        MENU_BIG_ID, _id(CARETAKER_TALK), _id(CARETAKER_ASK), _id(COFFEE), _id(PROMISE), _id(FLATTER)),
    BEG: ('[setflag %02x]' % FLAG_BEGGED +
          "Got yourselves into a bit\nof bother, lads? Well, I\nknow people. Comes with\nmy age, that does.[page]\n"
          "Now, this isn't how\nthings are meant to be.\nIt's an easier road than\nlads like you deserve.[page]\n"
          "First, I can see to it\nyou always draw the very\nbest fortune slip at the\nshrine.[page]\n"
          "You'll have to promise\nto use it for good deeds,\nmind. Once it's done,\nthere's no going back.[page]\n"
          "I also hear things on the\ngrapevine. Flatter me a\nbit, and I'll give you\nthe latest lowdown." + BACK),
    PROMISE: '[ifflag %02x %s %s]\n' % (FLAG_CHEAT, _id(PROMISE_FIRST), _id(PROMISE_AGAIN)),
    PROMISE_FIRST: ('[setflag %02x]' % FLAG_CHEAT +
                    "I trust you, lads. It's\ndone. The priest owes me\nfor all the odd jobs I've\ndone round the shrine." + BACK),
    PROMISE_AGAIN: "Your fortune's already\nsorted, lads. A promise\nis a promise." + BACK,
    # the hint for the furthest story step (tools/caretaker/hints.py)
    FLATTER: "Ooh, such kind words.[page]\n" + _hint_chain(),
}
SIGNOFFS = [t.rstrip('\n') + BACK for t in SIGNOFFS]
# Talk = how NERVE works; Ask = luck and saving (split 2026-10-23)
HELP = (
    "[cmdEE 00]Hm? Oh, it's you lot.\nBeen keeping this place\ngoing as caretaker since\nbefore your time.[page]\n"
    "I've seen plenty of\nlads like you come\nthrough. Here's some\nadvice for nothing.[page]\n"
    "Win a scrap, and your\nNERVE goes up. Lose one,\nor get knocked back by a\ngirl, and down it goes.[page]\n"
    "Run out completely, and\nyou're done for. And\nsleep won't top it up,\nmind.[page]\n"
    "Get home to bed in\nthe evening before\nnightfall.[page]\n"
    "Stay out late, and you'll\nend up back home\nexhausted.[page]\n"
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
# 199 (Nobuo: "Guv, not again! There's nothing up there but sky") answers
# Go up on the school roof and at the pylon (scene 315). The sky joke only
# works on the roof; the pylon gets its own copy (Stephen, 2026-10-24).
# (JP 199 is just "Oh, come on! Even No-bu-o's had enough".)
NOBUO_PYLON = FIRST_ID + 21
NOBUO_PYLON_TEXT = ("[cmdEF 34][cmdEE 12]Guv, climb that pylon?\n"
                    "[cmdEE 05]You're having me on!\nI'd get fried up there!")
# 195 (Nobuo: "we're already on the roof!") also answers Go up at the
# warehouse at the docks (325/326) and at the pylon once you have the bomb
# (316): JP 195 is a Noboru name pun that fits anywhere. The docks get their
# own line, the pylon its other Go up line (Stephen, 2026-10-25).
NOBUO_DOCK = FIRST_ID + 22
NOBUO_DOCK_TEXT = ("[cmdEF 34][cmdEE 01]Climb the warehouse, Guv?\n"
                   "I'm no cat burglar.\nI might fall in the dock!")
# Use at the pylon with the bomb (316 -> 1C3, blow it up) still worked after
# the bomb went to Onijima (0F6): that clears flag $9A (set by a new game,
# cleared nowhere else) but leaves $42 (carrying the bomb). Clearing $42
# instead would bring back Take on the Kakui roof (288), so Use checks $9A
# (Stephen, 2026-10-31; the original has the same hole).
FLAG_BOMB_HELD = 0x9A                      # clear once Onijima has the bomb
NOBUO_BOMB_CHECK = FIRST_ID + 23
NOBUO_BOMB_GONE = FIRST_ID + 24
NOBUO_BOMB_GONE_TEXT = ("[cmdEF 34][cmdEE 06]Guv, we already gave the\n"
                        "bomb to the police.\nProbably for the best.")
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

    menu = '[menu-call 47 c0 01 e1 01 c1 01 99 01 c2 01 09 03]'
    assert msgs[0x315].count(menu) == 1, msgs[0x315]
    msgs[0x315] = msgs[0x315].replace(menu, '[menu-call 47 c0 01 e1 01 c1 01 %s c2 01 09 03]'
                                      % _id(NOBUO_PYLON))

    menu = '[menu-call 46 c0 01 e1 01 c3 01 c1 01 95 01 09 03]'
    assert msgs[0x316].count(menu) == 1, msgs[0x316]
    msgs[0x316] = msgs[0x316].replace(menu, '[menu-call 46 c0 01 e1 01 %s c1 01 %s 09 03]'
                                      % (_id(NOBUO_BOMB_CHECK), _id(NOBUO_PYLON)))
    for scene, verb in ((0x325, 'fb'), (0x326, 'cc')):
        menu = '[menu-call 49 e4 01 %s 01 95 01 b5 01 b7 01 09 03]' % verb
        assert msgs[scene].count(menu) == 1, msgs[scene]
        msgs[scene] = msgs[scene].replace(menu, '[menu-call 49 e4 01 %s 01 %s b5 01 b7 01 09 03]'
                                          % (verb, _id(NOBUO_DOCK)))

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
MESSAGES[NOBUO_PYLON] = NOBUO_PYLON_TEXT
MESSAGES[NOBUO_DOCK] = NOBUO_DOCK_TEXT
# [ifflag f clear set]: $9A clear (bomb handed in) -> Nobuo's line, else 1C3
MESSAGES[NOBUO_BOMB_CHECK] = '[ifflag %02x %s c3 01]\n' % (FLAG_BOMB_HELD, _id(NOBUO_BOMB_GONE))
MESSAGES[NOBUO_BOMB_GONE] = NOBUO_BOMB_GONE_TEXT
MESSAGES[COFFEE] = '[ifflag %02x %s %s]\n' % (FLAG_HERO, _id(COFFEE_HIROSHI), _id(COFFEE_TORU))
MESSAGES[COFFEE_HIROSHI] = COFFEE_TEXT % 9 + BACK
MESSAGES[COFFEE_TORU] = COFFEE_TEXT % 8 + BACK
MESSAGES.update({mid: hints.text(pars, gen=False, mari=False) + BACK
                 for (_, pars), mid in zip(hints.HINTS, HINT_IDS)})
MESSAGES.update({mid: '' for mid in range(HINT_FIRST, HINT_IDS[-1]) if mid not in HINT_IDS})
# Hints with Gen's shortcut tip (hints.Gen): the hint's message checks flag
# 97 ([ifflag f clear set]) and goes to the version without the tip (once
# he has blasted the hedge) or with it (Stephen, 2026-11-09).
_gen_hints = [(pars, mid) for (_, pars), mid in zip(hints.HINTS, HINT_IDS) if hints.has_gen(pars)]
GEN_IDS = [mid for mid in range(HINT_IDS[-1] + 1, HINT_IDS[-1] + 2 + 2 * len(_gen_hints) + 2)
           if mid & 0xFF != 0xFF][:2 * len(_gen_hints)]
for (pars, mid), plain, tip in zip(_gen_hints, GEN_IDS[::2], GEN_IDS[1::2]):
    MESSAGES[plain] = hints.text(pars, gen=False) + BACK
    MESSAGES[tip] = hints.text(pars, gen=True) + BACK
    MESSAGES[mid] = '[ifflag %02x %s %s]\n' % (hints.FLAG_GEN_WAITING, _id(plain), _id(tip))
# Hints with a Mari() reminder (H38, Stephen 2026-11-18): the message checks
# flag 3D and goes to the version with the reminder while it's clear.
_mari_hints = [(pars, mid) for (_, pars), mid in zip(hints.HINTS, HINT_IDS) if hints.has_mari(pars)]
assert not any(hints.has_gen(p) for p, _ in _mari_hints)
MARI_IDS = [mid for mid in range(GEN_IDS[-1] + 1, GEN_IDS[-1] + 2 + 2 * len(_mari_hints) + 2)
            if mid & 0xFF != 0xFF][:2 * len(_mari_hints)]
for (pars, mid), plain, remind in zip(_mari_hints, MARI_IDS[::2], MARI_IDS[1::2]):
    MESSAGES[plain] = hints.text(pars, mari=False) + BACK
    MESSAGES[remind] = hints.text(pars, mari=True) + BACK
    MESSAGES[mid] = '[ifflag %02x %s %s]\n' % (hints.FLAG_MARI_PHOTO, _id(remind), _id(plain))
MESSAGES[ASK_SIGNOFF] = SIGNOFFS[2]   # replaced at run time, like CARETAKER_SIGNOFF

# The out-of-NERVE path ($E8D7) doesn't reset the text cursor, so the
# message starts wherever the last line left off; the original's one-line
# first page fitted, but ours has two. A helper at $FFC0 runs the
# original box routine then $E9AC (cursor back to the top-left).
NERVE_HELPER = 0xFFC0
FIGHT_ROW5 = 0xE351                        # fight odds table row 5 (see PATCHES)

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
    # Fight odds (original bug, found 2026-11-05 after Stephen lost to
    # Kitamura again and again): $E2FF rolls $70 against a row of three
    # rising thresholds at $E342 + 3 * (luck grade + 3 - strength); you lose
    # if the roll is <= the second. Row 5 is stored backwards (99 4D 1A), so
    # CHARM v strength 2 (Kudo, Kitamura, Harada, Mandrill), GOOD v 1 and
    # NORMAL v 0 won 40% instead of 70%, worse than one grade lower.
    (FIGHT_ROW5, bytes([0x99, 0x4D, 0x1A]), bytes([0x1A, 0x4D, 0x99])),
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

# Original bug (found by Stephen, 2026-10-31): Nobuo's stakeouts (cmdEA 01
# at $F0FA, cmdEA 03 at $F16A: the roof Watch, the car) set time-skip mode
# 1 ($02C0 = 1: run on to night, then the new-day routine $C3E5, day + 1)
# and then mode $80 (next morning via $C3B1, day + 1 again). Started in the
# morning or evening that is two days; at night mode 1 does nothing, so
# one. Mode 1 is only ever followed by mode $80, so its new day ($C3A8)
# now gives the day back: one day per stakeout, whenever it starts.
# (Also used by the midnight trip home below.)
DAYFIX_HELPER = 0xFFC6                   # free bytes after NERVE_HELPER, up to $FFD0
_dayfix = bytes([0x20, 0xE5, 0xC3,       # JSR $C3E5 (new day)
                 0xCE, 0xC8, 0x71,       # DEC $71C8
                 0x60])                  # RTS
PATCHES += [
    (DAYFIX_HELPER, b'\xFF' * len(_dayfix), _dayfix),
    (0xC3A8, bytes([0x20, 0xE5, 0xC3]), bytes([0x20, DAYFIX_HELPER & 0xFF, DAYFIX_HELPER >> 8])),
    # Same double count when out at midnight (Stephen, 2026-10-31): the
    # clock adds the day at 0:00 ($C435), then the trip home ($C352) runs
    # the new-day routine again. Out past midnight now wakes on the next
    # day, as going to bed in the evening does.
    (0xC361, bytes([0x20, 0xE5, 0xC3]), bytes([0x20, DAYFIX_HELPER & 0xFF, DAYFIX_HELPER >> 8])),
]
