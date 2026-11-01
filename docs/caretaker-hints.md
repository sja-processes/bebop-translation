# Caretaker hints (2026-11-01)

Agreed with Stephen after three drafts and built into the ROM. The text in
the game comes from `tools/caretaker/hints.py`; this page is the review copy.

Flatter in the caretaker's room says "Ooh, such kind words." and then the
hint for the furthest step you've reached. Each hint stays the same until
that step is done. Every box below is shown exactly as it would appear in
the game: 4 lines at most, 25 characters wide, and 23 on the last line
(before the arrow). "Here" means the caretaker's room.

"Shown after" and "Done when" give the flag (set by `[setflag]` in the
script message named) that opens and closes each hint. The chain checks
the latest step first, so flags the game clears again later (07, 4E, 7E)
are harmless.

## H01

Shown after: new game. Done when: 04 (013 Junko agrees).

```
Start around school,
lads. Junko hears all the
gossip there. Ask her
out, and nicely, mind.
```

## H02

Shown after: 04. Done when: 07 (032 Junko: Kakui roof).

```
Junko'll be waiting at
cafe Mai. Lost?

The fella just beyond the
building east of here
will point the way.

Once you're sat down, a
bit of flattery never
hurts. Then ask her what
she's heard.
```

## H03

Shown after: 07. Done when: 0D (194 Nobuo: the walkway on floor 4, after Search on the annexe roof).

```
Kakui Dept. Store,
north-east of here, is
shut for building work.

But there's always a way
in for lads like you.

Have a nose round the
building just south of
it. Take what you find
there.

Then use it at the store
to get in.

Then it's up and up, all
the way to the roof of
the annexe. Have a good
look round.
```

## H04

Shown after: 0D. Done when: 11 (19A Watch on the main roof). *the cigarette ends (1EF, flag 0F) come halfway through.*

```
Found a way across, have
you? Go down a floor from
the roof.

Then leave the annexe
from there to cross to
the main building.

Then right up to the main
building's roof.

Have a good look round,
then keep watch.
Patience, lads.
```

## H05

Shown after: 11. Done when: 13 (038 the police take the call).

```
A bomb on Minami Bridge?!
Somebody ought to tip off
the police, and
sharpish.

There's a payphone
south-west of here, under
a blue awning. Give them
a ring.

If they won't listen,
lean on them a bit.
That'll get them
moving.
```

## H06

Shown after: 13. Done when: 20 (086 Risa: Higashi in the arcade). *rival (08B) sets no lasting flag, so he and Risa go together.*

```
Got shot of the police?
Good. First things first,
though: toughen
yourselves up.

There's a soft lad in
purple north-east over
the road, near some
pipes.

Scrap with him till your
NERVE's full. You'll get
about faster after.

Next, your rival will be
hanging about south-east
of the pipes. Swallow
your pride and beg him.

He'll send you to Risa,
north-west inside the
shopping centre.

Buy her a coffee, then
flatter her. Works on me,
that does.
```

## H07

Shown after: 20. Done when: 1F (07D Misako: Mari).

```
Misako, just below the
water feature, might know
a thing or two. Offer her
a coffee.

However lucky you are,
she won't always say yes
first time. Try again,
then ask her.
```

## H08

Shown after: 1F. Done when: 19 (057 Shimazaki: dragged into a car).

```
There's a lad called
Shimazaki above the
arcade, which is the Deco
building.

Lean on him, then ask him
what he saw.
```

## H09

Shown after: 19. Done when: 1B (062 Yoshino: Gold Emperor car).

```
A black Skyline? Yoshino
might know whose it is.
Orange top, near that
soft lad in purple.

Give him a good hiding
(it may take a couple of
goes), then ask him.
```

## H10

Shown after: 1B. Done when: 1E (076 man outside: Higashi lying low).

```
A fella's turned up
outside the pachinko
place.

Can't miss it: it's the
building with the big 7s,
north of here.

Chat with him first or
leave him be for now and
go in.

Buy some balls and have a
go on the machines. Then
give him your winnings.
```

## H11

Shown after: 1E. Done when: 21 (01A tip man: Mandrill).

```
Higashi's lying low, is
he? The fella who hangs
about near cafe Mai hears
all sorts. Ask him.
```

## H12

Shown after: 21. Done when: 24 (093 Mandrill: Joto car park).

```
Mandrill, eh? Go and
shout for him in the
arcade.

Beat him (it may take a
few goes), then ask
him.
```

## H13

Shown after: 24. Done when: 26 (09A teacher: one stop to Joto).

```
Joto High? Your teacher's
by the underground
station north-east of
here.

Ask him the way. He'll
want a promise.
```

## H14

Shown after: 26. Done when: 2A (0A8 Yamada swears).

```
Buy tickets and ride one
stop. In the daytime,
call at the school north
of the station.

Their top dog's
Toshimitsu Yamada. Ask
him, then get him to
promise.
```

## H15

Shown after: 2A. Done when: 2F (210 It's the black Skyline!). *stakeout, Teru and the car in one go.*

```
There's a car park south
of Joto underground
station.

Walk right along the
bottom of it to that
car.

Search it, then keep
watch.

Next, there's a lad just
above the car park. Talk
to him, then sneak after
him.

Once you're tailing him,
follow him right up
close, then do a
search.
```

## H16

Shown after: 2F. Done when: 30 (0B1 Yamada: our Teru?).

```
The black Skyline! Yamada
swore nobody at Joto was
in a gang. Go back and
lean on him.
```

## H17

Shown after: 30. Done when: 7E (0B7 Teru: Nishiyama Building). *7E is cleared by 0C8; the chain checks later steps first.*

```
The day after you spoke
to Yamada, go to the
playground north of Joto
High.

Talk to Yamada first, as
he's nearest. Then talk
to Teru, and lean on
him.
```

## H18

Shown after: 7E. Done when: 33 (0C2 Gen: "Canny").

```
Gen, south-west of the
Joto playground,
maintains the road to the
next town.

He loves a natter. Keep
chatting till he names
his favourite tipple.
```

## H19

Shown after: 33. Done when: B2 (0C8 Gen lets you through).

```
Canny, is it? The offie
in the underground shops
sells it. Buy a bottle
and give it to him.
```

## H20

Shown after: B2. Done when: 81 (219 the gym).

```
Have a wander round the
next town.

It won't be there long,
but you'll glimpse
something you've been
looking for.

Then go into the building
to the right of where you
saw it.

That's the Nishiyama
Building. Go up and
search the top floor,
then come back down.
```

## H21

Shown after: 81. Done when: 3B (0DB Tsubota: steer clear of Mari).

```
There's a fella in purple
near the Nishiyama
Building, where you saw
the gym.

Take his sunglasses and
search him. Then lean on
him and ask. He'll sing
like a canary.
```

## H22

Shown after: 3B. Done when: 3F (0E9 the police by the bridge). *blocker (5F) and police together.*

```
West in Joto there's a
big lad blocking the way.
Don't fight him. You'll
not win.

Shout at him first, then
sneak past. The police
are further west. Have a
word.
```

## H23

Shown after: 3F. Done when: 3D (0E3 Mari: the photo). *needed for the second Tsuji fight.*

```
Mari's in the underground
shopping centre, just
above the water feature.
Talk to her.

Buy her a coffee, then
tease her a bit. Make
sure she shows you a
photo.

You may need to recognise
who's in it later.
```

## H24

Shown after: 3D. Done when: 40 (0F3 Junko: dodgy types still on the roof).

```
Been a while since you
saw Junko. Pop into cafe
Mai and ask her what's
new.
```

## H25

Shown after: 40. Done when: 42 (1C8 bomb taken).

```
Back up to the main roof
of Kakui Dept. Store,
lads, same way as
before.

Search it and take what
you find.
```

## H26

Shown after: 42. Done when: 43 (0FA Minoru: Kikunaga and cafe Gecko). *no lasting flag for handing over the bomb, so it goes with Minoru.*

```
A bomb?! Don't you dare
do anything daft with it.
Give it to the police in
Joto.

Same way as before, past
that big lad. Once
they've gone, cross the
bridge.

There's a lad south of
the fountain by the
docks. Offer him a
coffee.
```

## H27

Shown after: 43. Done when: 44 (100 Kikunaga: don't be daft).

```
Kikunaga mopes about in
cafe Gecko, just right of
the fountain, in the
daytime. Talk to him.
```

## H28

Shown after: 44. Done when: 47 (106 Iwamoto lends the camera).

```
Sweet on Junko, is he? A
photo of her might soften
him up. Iwamoto at your
school has a camera.

Search when you find him,
then lean on him.
```

## H29

Shown after: 47. Done when: 4A (114 Junko: keep the photo).

```
Take the camera to Junko
at cafe Mai. Beg her,
promise what she asks,
then use the camera.
```

## H30

Shown after: 4A. Done when: 85 (120 Kikunaga: the warehouse).

```
Now take Junko's photo to
Kikunaga at cafe Gecko.
Give it to him, then ask
him.
```

## H31

Shown after: 85. Done when: 86 (1CD Nobuo: Samejima).

```
The warehouse is
south-west by the docks.
Go after dark and search
it.

If anyone gets in your
way, thump him or shout
at him.
```

## H32

Shown after: 86. Done when: 4E (12D Misako: the fountain).

```
The day after your
scuffle at the warehouse,
find Misako.

She'll be near Minato
underground station,
north-east of cafe
Gecko.

Offer to buy her a
coffee, then ask her.
```

## H33

Shown after: 4E. Done when: 50 (224 teeth fished out). *4E is cleared by 224, which sets 50.*

```
In the fountain, eh? Off
to the park, then. Search
the fountain and take
what you find.
```

## H34

Shown after: 50. Done when: 51 (132 Tomezo: much obliged).

```
Those'll be Tomezo's
teeth. At the pachinko
place, buy balls and play
the machines first.

Then give him his teeth,
and leave quietly. Shout
in there and the
police'll nab you.
```

## H35

Shown after: 51. Done when: 53 (227 three tickets).

```
Tomezo owes you one now.
Talk at Minato station.

Then buy tickets for
Higashimachi and ride
there.
```

## H36

Shown after: 53. Done when: 56 (1D6 Samejima legs it).

```
In Higashimachi, never
mind most people. Nobuo's
old classmate is the one
at the bottom right.

Lean on him, thump him,
shout at him, chase him.
He'll run into the Safety
First building. Follow.
```

## H37

Shown after: 56. Done when: 59 (16E Samejima: Hokuto Gym).

```
Fight your way up to the
top floor. Just
south-east of the barrel,
there's a way down.

It takes you to the three
you can't reach directly
on the floor below.

Beat the two who fight.
Both take more than one
go.

Samejima will be cowering
in a barrel. Keep at him
till he talks.
```

## H38

Shown after: 59. Done when: 5D (182 Tsuji: Shingo's in my flat). *Gen kept a surprise; begging and the rematch in one go.*

```
Tsuji boxes at Hokuto
Gym, in the evenings.
Take him on.

You'll lose, mind. But
you must try at least
twice.

Then leave. A friend of
yours will be waiting
outside. Beg him for
help.

Back in to Tsuji, then,
and use your new friend
in the fight. Then ask
Tsuji where Shingo is.
```

## H39

Shown after: 5D. Done when: end.

```
Shingo's at Tsuji's flat?
It's in the block
north-east over the road
from your school.

Up to the third floor.
Search, then shout. Go
on, lads, go and get
him!
```
