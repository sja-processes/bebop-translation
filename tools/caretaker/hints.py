"""The caretaker's Flatter hints (Stephen, 2026-11-01; draft and review in
docs/caretaker-hints.md).

Flatter says "Ooh, such kind words." and then the hint for the furthest
story step reached. Each hint is opened by a story flag (set by
[setflag] in the script message named) and stays until the next hint's
flag is set. additions.py checks the flags latest first, so a flag the game clears
again doesn't matter as long as a later hint's flag is set by then (4E,
7E, 85). Check new hints with every [clrflag] in the script: 07 (taking
the sign), 44 (Misako's coffee) and 53 (the tickets) each sent the hint
back a step (Stephen, 2026-11-02).

Each paragraph is one text box: wrap() fills lines of 25 characters (23
on the last, which shares its row with the arrow) and the assert keeps it
to 4 lines.
"""

WIDTH, LAST_WIDTH, LINES = 25, 23, 4

# (flag that opens the hint, None for a new game; paragraphs)
HINTS = [
    # H01, until 04 (013 Junko agrees)
    (None, [
        'Start north-west of school, lads. Junko hears all the gossip there.',
        'Ask her out, and nicely, mind.',
        "By the way, search your place (north of here) on your first day, or you can't go to bed.",
    ]),
    # H02, until 07 (032 Junko: Kakui roof)
    (0x04, [
        "Junko'll be waiting at cafe Mai. Lost?",
        'The fella just beyond the building east of here will point the way.',
        "If he's not there, you'll need better luck.",
        "Once you're sat down, a bit of flattery never hurts. Then ask her what she's heard.",
        "By the way, search your place (north of here) on your first day, or you can't go to bed.",
    ]),
    # H03, until 09 (191 Nobuo takes the sign; it also clears 07)
    (0x07, [
        'Kakui Dept. Store, north-east of here, is shut for building work.',
        "But there's always a way in for lads like you.",
        'Have a nose round the building just south of the store.',
        'Take whatever you find there, then see how you get on.',
    ]),
    # H04, until 0D (194 Nobuo: the walkway on floor 4, after Search on the annexe roof)
    (0x09, [
        'Got yourselves a sign, eh? Use it at the store to get in.',
        "Then it's up and up, all the way to the roof of the annexe. Have a good look round.",
    ]),
    # H05, until 11 (19A Watch on the main roof); the cigarette ends (1EF, flag 0F) come halfway through
    (0x0D, [
        'Found a way across, have you? Go down a floor from the roof.',
        'Then leave the annexe from there to cross to the main building.',
        "Then right up to the main building's roof.",
        'Have a good look round, then keep watch. Patience, lads.',
    ]),
    # H06, until 13 (038 the police take the call)
    (0x11, [
        'Extremists have planted a bomb?! Somebody ought to tip off the police, and sharpish.',
        "There's a payphone south-west of here, beyond a little blue area. Give them a ring.",
        "If they won't listen, lean on them a bit. That'll get them moving.",
    ]),
    # H07, until 20 (086 Risa: Higashi in the arcade); rival (08B) sets no lasting flag, so he and Risa go together
    (0x13, [
        'Got shot of the police? Good. First things first, though: toughen yourselves up.',
        "There's a soft lad in purple north-east over the road, near some pipes.",
        "Scrap with him till your NERVE's full. You'll get about faster after.",
        "Luck affects every scrap, mind, but he's a soft touch. A bit of luck and he's yours.",
        'Next, your rival will be hanging about south-east of the pipes. Swallow your pride and beg him.',
        "He'll send you to Risa, north-west inside the underground shopping centre.",
        'Buy her a coffee, then flatter her. Works on me, that does.',
    ]),
    # H08, until 1F (07D Misako: Mari)
    (0x20, [
        'Misako, just below the water feature, might know a thing or two. Offer her a coffee.',
        "However lucky you are, she won't always say yes first time. Try again, then ask her.",
    ]),
    # H09, until 19 (057 Shimazaki: dragged into a car)
    (0x1F, [
        "There's a lad called Shimazaki above the arcade, which is the Deco building.",
        'Lean on him, then ask him what he saw.',
    ]),
    # H10, until 1B (062 Yoshino: Gold Emperor car)
    (0x19, [
        'A black Skyline? Yoshino might know whose it is. Orange top, near that soft lad in purple.',
        "He's tougher than the lad in purple. The luckier you are, the better your chances.",
        'Give him a good hiding, then ask him what he knows.',
    ]),
    # H11, until 1E (076 man outside: Higashi lying low)
    (0x1B, [
        "A fella's turned up outside the pachinko place.",
        "Can't miss it: it's the building with the big 7s, north of here.",
        'Chat with him first or leave him be for now and go in.',
        'Buy some balls and have a go on the machines. Then give him your winnings.',
    ]),
    # H12, until 21 (01A tip man: Mandrill)
    (0x1E, [
        "Higashi's lying low, is he? The fella who hangs about near cafe Mai hears all sorts. Ask him.",
        "If he's not there, you'll need better luck.",
    ]),
    # H13, until 24 (093 Mandrill: Joto car park)
    (0x21, [
        'Mandrill, eh? Go and shout for him in the arcade.',
        'Beat him, then ask him what he knows.',
        'If he gets the better of you, try again. Luck helps decide it.',
    ]),
    # H14, until 26 (09A teacher: one stop to Joto)
    (0x24, [
        "Joto High? Your teacher's by the underground station north-east of here.",
        "Ask him the way. He'll want a promise.",
    ]),
    # H15, until 2A (0A8 Yamada swears)
    (0x26, [
        'Buy tickets and ride one stop. In the daytime, call at the school north of the station.',
        "Their top dog's Toshimitsu Yamada. Ask him, then get him to promise.",
    ]),
    # H16, until 2F (210 It's the black Skyline!); stakeout, Teru and the car in one go
    (0x2A, [
        "There's a car park south of Joto underground station.",
        'Walk right along the bottom of it to that car.',
        'Search it, then keep watch.',
        "Next, there's a lad just above the car park. Talk to him, then sneak after him.",
        "Once you're tailing him, follow him right up close, then do a search.",
    ]),
    # H17, until 30 (0B1 Yamada: our Teru?)
    (0x2F, [
        'The black Skyline! Yamada swore nobody at Joto was in a gang. Go back and lean on him.',
    ]),
    # H18, until 7E (0B7 Teru: Nishiyama Building); 7E is cleared by 0C8; the chain checks later steps first
    (0x30, [
        'The day after you spoke to Yamada, go to the playground north of Joto High.',
        "Talk to Yamada first, as he's nearest. Then talk to Teru, and lean on him.",
    ]),
    # H19, until 33 (0C2 Gen: "Canny")
    (0x7E, [
        'Gen, south-west of the Joto playground, maintains the road to the next town.',
        'He loves a natter. Keep chatting till he names his favourite tipple.',
    ]),
    # H20, until B2 (0C8 Gen lets you through)
    (0x33, [
        'Canny, is it? The offie in the underground shops sells it. Buy a bottle and give it to him.',
    ]),
    # H21, until 81 (219 the gym)
    (0xB2, [
        'Have a wander round the next town.',
        "It won't be there long, but you'll glimpse something you've been looking for.",
        'Then go into the building to the east of where you saw it.',
        "That's the Nishiyama Building. Go up and search the top floor, then come back down.",
    ]),
    # H22, until 3B (0DB Tsubota: steer clear of Mari)
    (0x81, [
        "There's a fella in purple near the Nishiyama Building, where you saw the gym.",
        "Take his sunglasses and search him. Then lean on him and ask. He'll sing like a canary.",
    ]),
    # H23, until 3F (0E9 the police by the bridge); blocker (5F) and police together
    (0x3B, [
        "West in Joto there's a big lad blocking the way. Don't fight him. You'll not win.",
        'Shout at him first, then sneak past. The police are further west. Have a word.',
    ]),
    # H24, until 3D (0E3 Mari: the photo); needed for the second Tsuji fight
    (0x3F, [
        "Mari's in the underground shopping centre, just above the water feature. Talk to her.",
        'Buy her a coffee, then tease her a bit. Make sure she shows you a photo.',
        "You may need to recognise who's in it later.",
    ]),
    # H25, until 40 (0F3 Junko: dodgy types still on the roof)
    (0x3D, [
        "Been a while since you saw Junko. Pop into cafe Mai and ask her what's new.",
    ]),
    # H26, until 42 (1C8 bomb taken)
    (0x40, [
        'Back up to the main roof of Kakui Dept. Store, lads, same way as before.',
        'Search it and take what you find.',
    ]),
    # H27, until 43 (0FA Minoru: Kikunaga and cafe Gecko); no lasting flag for handing over the bomb, so it goes with Minoru
    (0x42, [
        "A bomb?! Don't you dare do anything daft with it. Give it to the police in Joto.",
        "Same way as before, past that big lad. Once they've gone, cross the bridge.",
        "There's a lad south of the fountain by the docks. Offer him a coffee.",
    ]),
    # H28, until 44 (100 Kikunaga: don't be daft)
    (0x43, [
        'Kikunaga mopes about in cafe Gecko, just east of the fountain, in the daytime. Talk to him.',
    ]),
    # H29, until 47 (106 Iwamoto lends the camera); 100 sets 44 and 84, and Misako's
    # coffee (127) can clear 44 early, so 84 opens it (cleared by 114, which sets 4A)
    (0x84, [
        'Sweet on Junko, is he? A photo of her might soften him up. Iwamoto at your school has a camera.',
        'Search when you find him, then lean on him.',
    ]),
    # H30, until 4A (114 Junko: keep the photo)
    (0x47, [
        'Take the camera to Junko at cafe Mai. Beg her, promise what she asks, then use the camera.',
    ]),
    # H31, until 85 (120 Kikunaga: the warehouse)
    (0x4A, [
        "Now take Junko's photo to Kikunaga at cafe Gecko. Give it to him, then ask him what he knows.",
    ]),
    # H32, until 86 (1CD Nobuo: Samejima)
    (0x85, [
        'The warehouse is south-west by the docks. Go after dark and search it.',
        'If anyone gets in your way, thump him or shout at him.',
    ]),
    # H33, until 4E (12D Misako: the fountain)
    (0x86, [
        'The day after your scuffle at the warehouse, find Misako.',
        "She'll be near Minato underground station, north-east of cafe Gecko.",
        'Offer to buy her a coffee, then ask her a follow-up question.',
    ]),
    # H34, until 50 (224 teeth fished out); 4E is cleared by 224, which sets 50
    (0x4E, [
        'In the fountain, eh? Off to the park, then. Search the fountain and take what you find.',
    ]),
    # H35, until 51 (132 Tomezo: much obliged)
    (0x50, [
        "Those'll be Tomezo's teeth. At the pachinko place, buy balls and play the machines first.",
        "Then give him his teeth, and leave quietly. Shout in there and the police'll nab you.",
    ]),
    # H36, until 56 (1D6 Samejima legs it); the tickets (53, 227) are cleared by
    # the ride (3A3/3A4) and nothing lasting marks the arrival, so it's one hint
    (0x51, [
        "Tomezo owes you one now. He'll help you at Minato station.",
        'Then buy tickets for Higashimachi and ride there.',
        "In Higashimachi, never mind most people. Nobuo's old classmate is the one in the south-east.",
        "Lean on him, thump him, shout at him, chase him. He'll run into the Safety First building. Follow.",
    ]),
    # H37, until 59 (16E Samejima: Hokuto Gym)
    (0x56, [
        "Fight your way up to the top floor. Just south-east of the barrel, there's a way down.",
        "It takes you to the three you can't reach directly on the floor below.",
        'Beat the two who fight, Kudo and Kitamura. They\'re tough, so expect to lose a few.',
        'Like any scrap, a lot comes down to luck. Try them on your luckiest days.',
        'Samejima will be cowering in a barrel. Keep at him till he mentions the gym.',
    ]),
    # H38, until 5D (182 Tsuji: Shingo's in my flat); Gen kept a surprise; begging and the rematch in one go
    (0x59, [
        'Tsuji boxes at Hokuto Gym in the Nishiyama Building during the evenings.',
        "Take him on. You'll lose, mind. But you must try at least twice.",
        'Then leave. A friend of yours will be waiting outside. Beg him for help.',
        'Back in to Tsuji, then, and use your new friend in the fight. Then ask Tsuji where Shingo is.',
    ]),
    # H39, until end
    (0x5D, [
        "Shingo's at Tsuji's flat? It's in the block north-east over the road from your school.",
        'Up to the third floor. Search, then shout. Go on, lads, go and get him!',
    ]),
]


def wrap(par):
    """One paragraph -> one box (lines joined by newlines)."""
    lines, cur = [], ''
    for w in par.split():
        t = (cur + ' ' + w).strip()
        if len(t) <= WIDTH:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines[-1]) > LAST_WIDTH:
        head, w = lines[-1].rsplit(' ', 1)
        lines[-1:] = [head, w]
    assert len(lines) <= LINES, par
    return '\n'.join(lines)


def text(paragraphs):
    return '[page]\n'.join(wrap(p) for p in paragraphs)
