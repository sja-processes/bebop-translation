# Be-Bop Highschool - Legend of High-School Paradise

English translation patch for the Famicom/NES game *Be-Bop Highschool - Koukousei Gokuraku Densetsu*.

Download the BPS patch from [Releases](https://github.com/sja-processes/bebop-translation/releases).

## Intro

*Be-Bop Highschool - Legend of High-School Paradise* is an adventure game where you and two of your schoolfriends try to find your missing classmate. This mainly involves walking around and talking to people, with fighting and dating girls also crucial parts of your adventures. You begin by choosing your hero: Toru Nakama or Hiroshi Kato.

This patch is a British English translation of the Japanese original, along with many bug fixes and quality-of-life improvements.

Please note that AI was used to assist with this project, but many human hours of work were involved throughout.

This patch is fully open source: this repository holds everything used to build it (see [Building from source](#building-from-source)).

## Emulation notes

This has been thoroughly tested in two emulators, Mesen and Nestopia (the latter through RetroArch), but not on original hardware.

**Important:** if your emulator has an overclock option, make sure it is set to 1x rather than 2x, etc. The main map view can often show blocks that shouldn't be there due to timing issues if not running at 1x. This issue exists with the original ROM too; it is not a problem with this patch.

To set it in RetroArch: Quick Menu → Core Options → Emulation Hacks → CPU Speed (Overclock) → 1x, then Manage Core Options → Save Game Options to apply it to this game only.

## Translation notes

The original Japanese meaning and spirit has been kept throughout where possible, but inevitably there are some things that could not be meaningfully translated directly. For example, some jokes simply do not work in English, most notably a few puns relating to one character's name sounding similar to "up". Different lines or phrases have been used instead in these situations.

Many action commands had reactions that would make more sense in Japanese culture, but not necessarily to others. To handle these, bridging lines have been added to naturally lead the player's understanding into what is meant.

The action choices in a particular coffee date (with Misako) offered Ride as an option. In the original this could be taken as a double entendre (riding a train, etc. / riding her), but in English it can only be taken one way given the situation. So it has been changed to Give to keep the double entendre: "give her a gift" / "give her one".

A particular character had a regional Japanese accent. To reflect that in this English version, a well-known regional English accent has been used for the character: Geordie, as used by people from Newcastle and surrounding areas of north-east England.

## Bug fixes (contains some spoilers!)

- Some situations, such as overnight stakeouts, could lead to the new-day routine happening twice (causing days to be skipped and incorrect luck resets, and at least in Toru's case even preventing the happiest ending being achievable).
- After taking an item from a roof in a particular situation, departing originally took three presses of "Go down" instead of one.
- A particular item can no longer be used at the pylon location when it's already been given to the police.
- Added the actual working happiest ending for Toru. It's almost identical to Hiroshi's anyway, but one of the visual assets didn't exist.
  - This ending was probably never reachable before due to this bug and the new-day bug mentioned above.
- The best luck level had an incorrect win chance in fights, meaning it was worse than some lower luck levels.
- The underground train journey from Higashimachi to Minato (that direction only) did not show the normal train ride sequence.

## Quality-of-life improvements (contains some spoilers!)

- The patch version info is viewable on the game's title screen using D-pad left/right.
- School caretaker:
  - The biggest change in this patch, apart from the translation itself, is the addition of a new character: the school caretaker.
  - He is available in a previously unused building immediately south-west of your starting position.
  - He's there to explain some of the less obvious aspects of the gameplay, such as luck and nerve, which can be very confusing without understanding them.
  - The caretaker can also provide a couple of cheats if desired:
    - Instructions on what to do next in your current situation, which should avoid resorting to a walkthrough if you're stuck.
    - Always get the best luck from the shrine, which will avoid some non-productive in-game days and frustrations.
- In the stats panel, the luck level now has the same colour as the nerve level (it was originally black).
- Some messages didn't wait for a button press to dismiss and didn't give time to read them.
- Three locations in the game have different floors/levels. In the original, these all used the same image within a building, but they now have different images (mostly subtle) to avoid confusion.
- Cars have been added to the Joto car park on the main map view to improve how a couple of gameplay elements work/look.
- Pressing the Select button within a scene now shows a day counter for achieving the happiest ending. Note that this does not refresh while being shown; toggle it off/on to update it if required.

## How to patch

You will need a copy of the original ROM, `Be-Bop-Highschool - Koukousei Gokuraku Densetsu (Japan).nes`:

| | |
|---|---|
| MD5 | `d868b94084160470e3e265906b05477f` |
| SHA-1 | `68373685e2facefc23c5622ed3b7957b8d8c6500` |
| CRC32 | `17d50605` |

This is a standard BPS patch, so it can be applied to the ROM using a common tool like [Flips](https://github.com/Alcaro/Flips).

## Building from source

The repository contains no game data: you need your own copy of the original ROM (above).

1. Put the ROM in `rom/`.
2. Run `python3 tools/insert.py`. It writes `out/bebop_en.nes` and `out/bebop_en.bps`.

The build needs Python 3 and Pillow. To run the text checks (`tools/encheck.py`, `tools/pagecheck.py`), first extract the Japanese script with `python3 tools/script.py dump`. The English script is in `script/en/`, the tools are in `tools/`, and `PLAN.md` holds the working notes and findings behind every change.

## Full walkthrough (major spoilers!)

If you're stuck somewhere, an alternative to following this walkthrough is to flatter the caretaker to get told what to do next. The caretaker's instructions are also a little more detailed in many cases than the very brief steps below.

<details>
<summary>Show the walkthrough (major spoilers!)</summary>

### Get rid of the police to leave the initial area

- Ask out Junko
- Restaurant (cafe Mai) directions from tip man just north-east of the cafe. The man is only there if luck is sufficient.
- Junko - flatter and ask
- Search building just south of Kakui Dept. Store
- Take sign and go just north to Kakui Dept. Store
- Use sign and go up all the way to roof of annexe
- Search roof of annexe
- Go down one floor and Leave to main building
- Go up to roof of main building
- Search roof then Watch
- Will find out about bomb and Minami Bridge
- Go down one floor, leave, go all the way to the ground and leave
- Go to payphone, south-west under blue covering
- Use phone and Lean on
- Police will leave to deal with bomb

### The search for Higashi, the Gold Emperor and Samejima

- Fight easy person (he has no name; purple top; black top with red stripes on map) repeatedly until max nerve (will move faster after this)
- Man (our rival) near Shingo's angry girlfriend - beg him
- Risa in shopping centre (north-west inside), coffee date - flatter - "Higashi hangs out in arcade"
- Misako (just below water feature) - coffee - ask her for coffee twice
- Ask Misako - "Mari knows about Gold Emperor"
- Shimazaki above arcade ("Deco" building) - Lean on "black Skyline" and Ask "dragged into"
- Beat man in orange top (red trousers), Yoshino, near man beaten before (possibly more than one attempt) and Ask him - "Skyline probably one of Gold Emperor biker gang's cars"
- Both people you fight here then disappear
- A man will now be outside pachinko place - no need to talk to him, go straight into the pachinko place
- Buy and Use balls in pachinko place to win more (proprietor is Tomezo)
- Give balls to man outside pachinko place - "Higashi lying low somewhere"
- The tip man in street near cafe Mai will give "Mandrill" info
- Shout in arcade ("Deco" building) once you know the above info
- Beat Mandrill guy (possibly more than one attempt) and Ask him - "hang out in car park near Joto High"
- Talk to teacher who will be near underground station, Ask then Promise him, who will give directions to Joto High
- Buy underground tickets and ride train
- During daytime only, Talk to guy in school just north of underground station (Toshimitsu Yamada) and Ask him and Promise (he says "no one at the school is in a gang")
- Walk right at bottom in car park to the car
- Search and Watch to stake out the car
- Talk to man just above the car park (Teru) and Sneak and Leave
- Follow him and go right up to him, then Search car
- Talk to guy in school again (Toshimitsu Yamada) and Lean on - he says "come to the playground up north tomorrow"
- Next day go to the playground near Joto school, talk to boss (Toshimitsu Yamada) first, who's closest, and then Teru
- Lean on Teru, will say "the black Skyline'll be parked by the Nishiyama Building in the next town"
- Geordie man (Gen) will be south-west of the playground; talk to him a lot until he says his favourite is "Canny"
- Go to offie in underground shopping centre and buy Canny
- Gen will then allow route to next town
- Wander around town, car will depart, go up floors of building to the right of where the car was (this is the Nishiyama Building) and see gym and Search it and then go all the way back down and Leave
- Man dressed in purple will be in street
- Take his sunglasses and search him, will find his real identity (Sarukichi Tsubota)
- Lean on him and Ask him - he will say "steer clear of Mari from Girls' Commercial", "her fella's high up in Gold Emperor"
- Then go to man blocking way to the west in Joto
- Don't do anything but Shout and then Sneak to get past him (he would win any fight attempts)
- Police are further west - talk to them
- Talk to Mari in the underground shopping centre (just above water feature if luck is sufficient) - her boyfriend is high up in Gold Emperor and boxes. Also ask for Coffee and then Tease her so she shows photo of her boyfriend (cannot do second fight with Tsuji without this step)
- Ask Junko again in cafe Mai, "dodgy types are still hanging about on the roof of Kakui Dept. Store"
- Back to roof and Search - finds bomb
- Then go back to the police in Joto using the same method as before, or for a shortcut go below the caretaker's building after nightfall and Promise Gen, and he will blow a hole in the hedge
- Give bomb to police - do not use it on the pylon to avoid game over!
- Police will leave, so can go over the bridge
- Talk to person (Minoru) south of the fountain / hedges area by the dock and pick Coffee - "our boss Kikunaga's gone and fallen for Junko at your school. He's always moping in that cafe Gecko, sighing all day."
- Gecko is the cafe in this area to the right of the fountain, go there (daytime only) and talk to Kikunaga
- Go to our own school and Search and Lean on the boy Iwamoto to get camera
- Then go to cafe Mai then Beg, Promise, and Use (the camera) - Junko should then say we can keep the photo and she will return the camera
- Give photo to Kikunaga in the Gecko cafe then Ask, who will say "the Gold Emperor lot meet every night in the warehouse at the docks"
- Go into the warehouse (after nightfall), located south-west in this area, and Search
- Man in warehouse - Thump or Shout - Nobuo says "one of them was my old classmate, Samejima. He went to school in a town on the train from Minato station [...] He's at Kyokuto High"
- Next day, talk to Misako in the new area near the new underground station (north-east), choosing Coffee - "false teeth" and Ask - "chucked them in the fountain in the park"
- Go to the fountain and Search - false teeth found, then Take
- Go to pachinko place - need to Buy and Use the machines again, then can Give
- Leave pachinko place without doing Shout, otherwise police will get you
- Go into Minato station. The pachinko man will tell Ken the Slasher to let us through.
- Travel on underground to Higashimachi area

### Higashimachi area

- Tanaka is the person at the top - high school president
- Middle-right person is our rival
- Bottom-left person beats us if fighting (but probably beatable with enough luck)
- Bottom-middle person can be beaten if fighting
- Can ignore the above people
- Bottom-right is the person Nobuo knows (Samejima), and he can be leaned on, punched, shouted at, and chased - he will go into the "Safety First" building, which we can follow him into

### Inside the "Safety First" building

- Person kind of straight up on 1F can be beaten but may need more than one try
- First and second people on 2F can be beaten
- Person top-right on 3F can be beaten
- Three people on the left of 3F can't be reached directly from this level
- All four people on 4F can be beaten
- On 4F you need to go into one of the areas just south-east of the barrel (looks like a grey short column or stairs) to go down to the three people on 3F
- The three people are Big Four nos. 2-4
- Encountered in this order, so lowest rank encountered first:
  1. Rank no. 4 - Samejima (the person Nobuo knows) - runs off without fighting
  2. Rank no. 3 - Kudo - needs more than one attempt to beat depending on luck
  3. Rank no. 2 - Kitamura - needs even more attempts to beat depending on luck
  4. (Rank no. 1 is Tsuji, not faced here)
- Go to Samejima, who's hiding in a barrel right there, who will eventually say Tsuji boxes at Hokuto Gym in the Nishiyama Building, in the evenings

### The end

- Go to the gym in the evening
- Fight Tsuji once, will lose, speak to him again, fight him a second time, will lose again, leave, and Gen will be outside
- Beg Gen, and he says he will beat the bully himself
- Choosing Leave goes right back to the encounter with Tsuji
- Can then Use Gen in the fight, which leads to Tsuji saying Shingo is in his flat when choosing Ask
- Go to 3F of the flat, Search, and Shout
- End of game sequence

</details>

## Licence

The tools, the English script, the new artwork and the documentation in this repository are released under the [MIT License](LICENSE), so you're welcome to use, change and share them.

This covers only the work in this repository. *Be-Bop Highschool - Koukousei Gokuraku Densetsu* itself (the game, its ROM and its original Japanese text and graphics) belongs to its rights holders and is not included or licensed here.
