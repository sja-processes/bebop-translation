# Glossary & style guide (Stage 5)

Decisions agreed 2026-10-10. Keep every file consistent with this list;
add new names as they turn up.

## Style
- UK English spelling, vocabulary and slang (mate, bloke, chancer;
  money stays in yen because the game uses it).
- **No honorifics**: drop -san/-kun/-sama. アニキ (Nobuo → hero) → **"Guv"**. Senpai → "the older girls/lads".
- **Place/school names romanised**, not translated.
- Never "Now then, now then" / "Now then" as a greeting for anyone (Savile).
- Raw tiles like `<41>` inside words may be dropped (checker only warns).
- Ellipsis ‥‥ → `...` (keep the `[cmdED]` before it). 〜 → drawn-out
  letters ("Eeek", "Hello-o"), but never where the stretched word looks
  like another word or an accent ("looot" read as "loot"). ♥ kept.
- Stammers kept ("I-I-I d-don't"), hyphen style.
- うんせい (game stat) → **luck**; status panel labels are **NERVE** (きりょく)
  and **LUCK**; luck grades worst→best **JINX / BAD / FAIR / GOOD / CHARM**
  (どつぼ / 凶 / 中吉 / 大吉 / ばりきち) — set in `tools/status.py`.
- **Self-reference by name**: cutesy name-for-"I" (e.g. Megumi, 02B) →
  plain "I" with the cuteness carried by wording ("I'm ever so scared!").
  Boastful third person stays: tough guys ("Picking a fight with
  Toshimitsu Yamada?", "the great Kikunaga") and Nobuo's running gag of
  always using his full name ("Nobuo Kaneko'll prove he's a real man").
- やくそくする (Promise) can mean "arrange to meet" with girls; where a
  response treats it as a date, bridge it in the reply ("Promise to meet
  up? A date?!"), since no 7-letter verb covers both senses.
- Plain ASCII plus ♥ only (no é, curly quotes) so the stage 6 font stays small.
- こんじょう (根性) = grit / determination, not courage (Stephen 2026-10-18).
  Pick by context:
  - 193 the wardrobe on his back: "takes grit";
  - 180/190 Nobuo after heaving the sign: "did you see how tough I was?";
  - 191 carrying the sign: "You'll see my mettle";
  - 1F1 the night in the bin: "What determination!";
  - 1DF Sleep at the wrong time: "show a bit more grit";
  - "guts" only where it's daring (0E4, 375).
  Keep the on-his-back joke for the wardrobe only.
- Avoid UK slang that reads as a slur or obscenity elsewhere: no "fag"
  for cigarette (1EF: タバコのすいがら → "cigarette ends", Stephen 2026-10-18).

## Name codes
| Code | Expands to | Notes |
|---|---|---|
| `[cmdE1]` | hero's given name (Toru / Hiroshi) | |
| `[cmdE2]` | hero's surname (Nakama / Kato) | used where JP has 〜さん/〜くん |
| `[cmdDF]` / `[cmdE0]` | partner's name | |
Width checker counts each as 7 letters.

## Heroes
- 中間徹 Toru Nakama (トオル / ナカマ)
- 加藤浩志 Hiroshi Kato (ヒロシ / カトウ)

## Schools & groups
| JP | EN |
|---|---|
| アイトク | Aitoku (High) — the heroes' school |
| キタコウ | Kita High |
| ニチュウ | Nichu (middle school; ちゅうがく = "middle school", not American "junior high", Stephen 2026-10-30) |
| チュウオウじょしこうこう | Chuo Girls' High |
| キョクトウこうこう | Kyokuto High |
| してんのう | the Big Four (Kyokuto) |
| ゴールドエンペラー | Gold Emperor (biker gang; ゾク → biker gang; かんぶ → "high up in") |
| ジョウトウこうこう | Joto High |
| ジョシショウ | Girls' Commercial (Mari's school) |
| タチバナ | Tachibana (Minoru's school) |

## People
- 黒田晋平 **Shinpei Kuroda** (Toru's tag-along) and 大前均太郎 **Kintaro Omae** (Hiroshi's tag-along; goes berserk if called "Pig") — names from the manual.
| JP | EN | Who |
|---|---|---|
| シンゴ | Shingo | Kita High womaniser, kidnapped |
| レミ | Remi | Chuo Girls', Shingo's girlfriend |
| カネコ ノブオ | Nobuo Kaneko | self-appointed sidekick; あっし/〜やす speech → light Cockney wide boy ("Guv", me = my, Cor, Blimey, "a big name" round here; but not two "me"s in one sentence: 1A3 is "fussy about my coffee, me", Stephen 2026-10-18). The JP "Noboru" name gag (see below) is replaced in English |
| (EF32 companion) | | polite junior, calls hero by name, "Nobuo"; the voice of reason |
| イナガキ | Inagaki | Nichu No.2 |
| ハヤシ | Hayashi | Nichu top dog |
| ユウジ | Yuji | informant (luck-based) |
| ヒガシ / マントヒガシ | Higashi / "Mandrill Higashi" | ex-Gold Emperor |
| ゲン | Gen | boozy dynamite expert from Kyushu |
| ハラダ | Harada | Gold Emperor's minder |
| ひときりケン | Ken the Slasher | just out of prison; the honour-bound guard Tomezo calls off (231) |
| ツジ・キタムラ・クドウ・サメジマ | Tsuji, Kitamura, Kudo, Samejima | Big Four No.1-4 |
| イワモト | Iwamoto | Aitoku pupil with camera |
| シマザキ | Shimazaki | Kita High |
| ヨシノ | Yoshino | local hard man |
| シナガワ | Shinagawa | pachinko addict |
| メグミ, ジュンコ, ミサコ, マリ | Megumi, Junko, Misako, Mari | girls |
| リサ | Risa | 17, underground shopping centre (Hepburn R; was "Lisa") |
| ヤマダ トシミツ | Toshimitsu Yamada | Joto top dog; straight-dealing |
| テル | Teru | Joto lad secretly in Gold Emperor |
| かなしみのカズヒロ | Kazuhiro the Heartbroken | lost his girl Rie to Shingo |
| ゲン (ひやといにんぷ) | Gen, navvy | **Kyushu dialect → light Geordie** (howay, reet, cannit, toon, me = my). Tease (0C4) そげんな (Kyushu そんな, hurt "aw, come on") = "Aw, howay, man... Don't wind us up." ("divvent" too obscure; was "Is that reet."; Stephen, 2026-10-29). "gan" only where natural ("Ah'll gan and sort out"); いくば〜い is "Reet, here goes!" (230) and "Reet, let's go!" (178), not "gan" (Stephen, 2026-10-26) |
| ツボタ サルキチ | Sarukichi Tsubota | fake yakuza in sunglasses; シャバぞう → "drip" |
| マリ | Mari | Girls' Commercial, Joji Tsuji's girlfriend |
| ツジ ジョージ | Joji Tsuji | Big Four No.1, Gold Emperor, boxer, Skyline owner. Hepburn like every other name; was "George" (Stephen, 2026-10-24) |
| オニジマ | Onijima | police officer (Kansai speech, kept plain UK copper: "You're nicked!") |
| タチバナのミノル | Minoru of Tachibana | |
| キクナガ | Kikunaga | Minoru's boss, lovesick for Junko |
| (rival) | the *other* hero ([cmdDF]); EF14 portrait | competes for Remi: "whoever rescues Shingo first gets Remi" |
| (old man) = トメゾウ | Tomezo, "Grand Boss" (おおおやぶん) | lisps s → sh while his false teeth are lost; speaks normally once they're back (132). ニイヒャン(たち) = lisped ニイチャン → "Young lads" (06A), "Lads" (06E); not "Shonny", which read as a mystery word |
| イワモト | Iwamoto | timid Aitoku camera nerd, blurts history dates |
| ジュンコ | Junko | refers to herself as "Junko"; Kikunaga is smitten |
| タナカ | Tanaka | Kyokuto's only swot; every committee |
| (Kazuhiro) | | 13E-140 by the sea, wants to jump; keep it plain |
| (drunk schoolboy, EF $13) | | 141 "Whassh you lot doin'?": JP なんばしようと〜 is Hakata (Kyushu) dialect, but he isn't Gen, so a drunk slur, not Geordie (Stephen, 2026-10-24); 142/143 are drunk noises |
| トツカ (teacher) | Mr Totsuka; "Not good... Mm." catchphrase (イカんなぁ) | |
| (policeman) | "Right, let's be 'avin' you" — NOT "Now then, now then" (Savile association) | |
| (priest) | かしこみ → "O spirits, hear us!" | luck-raising ritual |

## Places & things
- おみくじ (omikuji) → **fortune slip**, never bare "fortune" (reads as money). Shrine: Buy draws one (results 189-18D, "Guv, your fortune slip says..."); Take (1F7) is getting one without paying, which brings バチ (divine punishment). Buy/Take can't be renamed: both are used in many scenes.
- のぼる/Noboru pun (Go up on a roof, 195 and 199): Go up = のぼる, also the name Noboru, close to Nobuo, so Nobuo protests he isn't Noboru. Untranslatable; replaced with English jokes: 195 "Any higher and we'd be dodging aeroplanes", and the repeat 199 gets a fresh line, "There's nothing up there but sky" (an English joke repeated falls flat where the Japanese name gag repeated well). JP 195 also answers Go up at the warehouse at the docks (325/326) and at the pylon once you have the bomb (316); the docks get their own line, "Climb the warehouse, Guv? I'm no cat burglar. I might fall in the dock!", and the pylon reuses its "climb that pylon? ... fried" line (Stephen, 2026-10-25). No drug double meanings: the original never alludes to drugs.
- おんなのてき (女の敵, "enemy of women") → **womaniser** in general talk (031), **love rat** from a girl who's been wronged (09C) (Stephen, 2026-10-24).
- シンゴじるし (1A9, after Search gets you slapped) → **one of Shingo's love bites**: じるし is a brand/mark, not a tattoo (いれずみ), so "Shingo's mark" read wrongly as a gang tattoo (Stephen, 2026-10-24).
- こうえん (公園): a small Japanese neighbourhood park is usually swings and a slide, so the meeting place "up north" in 0B1 is the **playground** (it looks like one on the map; Stephen, 2026-10-24). 12D's "fountain in the park" stays "park" (checked on the map: a paved garden with hedges and a fountain pavilion; Stephen, 2026-10-25).
- おまえら (plural "you", no number) → **you lot**, not "you two": the player's party is three (hero, tag-along, Nobuo).
- 口車に乗る (be taken in by smooth talk) → **sweet talk**, not "patter" (to Stephen's British ear, patter is a salesman's or market trader's spiel) — 02A.
- かげきは (過激派) → **extremists** (1980s militant radical groups; the Minami Bridge bomb plot, 03B/0F6/10C/19A). Kept over "radicals" (Stephen, 2026-10-16).
| JP | EN |
|---|---|
| さてん「マイ」 | cafe "Mai" |
| カクイデパート | Kakui Dept. Store (full name); casually "Kakui's" or "the shop" — never "the store" alone |
| みなみおおはし | Minami Bridge |
| シカイライン | Skyline (car; JP alters one kana of スカイライン, which reads instantly in Japanese but not in English, so we use the real name. No 'Nissan', no 'GT-R' (badge unused 1973–89). First mention, 057, says 'a black car, a Skyline' as the JP does with という くるま) |
| パトカー | police car / panda car |
| たま (パチンコ) | pachinko balls |
| 19ばんだい (パチンコ) | machines 190 to 199 (番台 = a block of machine numbers; was "the 19s"; 225, Stephen, 2026-10-25) |
| イイバイ (sake brand; Hakata "it's good") | "Canny" (Geordie "good") — pun reused in 0C6 |
| イカンバイ (2nd sake; Hakata "no good / can't") | "Cannit" (Geordie "can't") — "ah cannit give ye... a bottle of Cannit" |
| ブロマイド | glamorous shot (a star's glossy portrait photo; "pin-up" read as risqué. 10F: Junko's third-person ジュンコさん → "me": "a glamorous shot of me"; Stephen, 2026-10-25) |
| どすこい | "Hup!" (Nobuo's sumo-style chant) |
| かお (well-known) / かおパス | Nobuo in the store: "a big name" (194/196/198); at stations: "they all know me" / "nobody knows me" (1AA/1D4), Toru: "they all know you" (203/206). Was "a face" (Cockney, but obscure; Stephen, 2026-10-28) |
| さけぶ (verb) | "Shout" — 1BA refers to the command by name; keep in sync with verb list |
| ヤングマガジン | Young Magazine (real magazine that ran the manga; kept) |
| てんごくの やかた | the House of Heaven (Tsuji's flat, ending) |
| てんごくに いちばん ちかい マンション (242) | "this place is close to heaven" (parodies the 1984 film 天国にいちばん近い島; English keeps the place, not the title; Stephen, 2026-10-26) |
| エスケープ (skip class) | skive off |
| N かい (floors) | "floor N" — Japanese numbering kept, avoids UK ground-floor mismatch |
| おどりうち (pachinko) | trick shot |
| きりょく (stat) | "run out of steam" / steam |
| ヘンシ〜ン | "Transfoooorm!!" (Nobuo, 388/38A) |
| やったろうジャン | "Let's 'ave it!!" |
| ズガガガ ドピューン (kiddie ride) | "Vroom vroom... Neeeeow!" (1A5 / 1FC) |
| ひがしまちえき / みなとえき | Higashimachi / Minato station |
| みなとの そうこ | warehouse at the docks |
| ホクトジム | Hokuto Gym (Nishiyama Building) |
| おおボケ 3にんぐみ | the three wallies |
| さけ / ABC "B" (147) | "more than a snog" (80s ABC of romance: A kiss, B petting; the rival's Promise answer: "All right, I'll keep my promise. But when I win Remi, it'll be more than a snog……", naming Remi as the JP leaves her implied; Stephen, 2026-10-25) |
| さかや | offie (off-licence) |
| ちかがい | underground shopping centre (地下街; was "underground arcade", clashed with the games arcade) |
| ゲームセンター | arcade (video games; plain "arcade" = amusement arcade in the UK) |
| カベチョロ (cafe) | cafe "Gecko" |
| ニシヤマビル | Nishiyama Building |
| フルーツパフェ | knickerbocker glory |
| ほけんじょ (catches strays) | 0F2: "Bet he's been rounded up with the other strays" (jibe calling Shingo a stray mutt; "dog warden" didn't land; Stephen, 2026-10-25) |

## Progress
- [x] msg_000 (2026-10-10)
- [x] msg_080 (2026-10-10)
- [x] msg_100 (2026-10-10)
- [x] msg_180 (2026-10-10)
- [x] msg_200 (2026-10-10) — 254-257 hero names; 258-27F are menu scripts (codes only, copied)
- [x] msg_280 (2026-10-10) — scene/menu scripts only, copied
- [x] msg_300 (2026-10-10) — only 338/339/33B/36F/370/375 have text
- [x] msg_380 (2026-10-10) — first pass of the whole script complete

## Verb menu ($3AA-$3C1, max 7 letters — measured in stage 6b)
| ID | JP | EN | Notes |
|---|---|---|---|
| 3AA | はなす | Talk | |
| 3AB | きく | Ask | |
| 3AC | おどす | Lean on | intimidate with threats/attitude (verbal, not physical: that is 3AD Thump). Changed from Menace 2026-10-15 ("Threaten" is 8 letters). Responses checked: most fear/defiance; several say "threaten" (072, 03D, 0D6, 0EB); 293 is a bomb-threat phone call |
| 3AD | なぐる | Thump | "Thump me all you like" (073) |
| 3AE | とる | Take | |
| 3AF | ねる | Sleep | (menu word stays plain; dialogue can still say "kip") |
| 3B0 | いどうする | Leave | "move/relocate": the command that takes you out of the current location; "Move" read like moving an object (changed 2026-10-14) |
| 3B1 | ごまする | Flatter | "grind sesame" = butter someone up; distinct from 3BC おがみたおす (Beg = plead until they give in). Changed from Grovel 2026-10-15; in 298 it leads to 044 (same as Beg). In Risa's scene 2C6 you butter up *Nobuo*, who charges off (1B3), so 1B3 opens "Oh, you flatter me, Guv. That's got me all psyched up!"; Use in 2EB shares 1B3 in JP, so it gets its own copy opening "Leave it to me, Guv." (additions.retarget). Misako's scene 2C3: Flatter also buttering up Nobuo, who asks her along (1A0), bridged with "Cor, you flatter me, Guv!" (2026-10-20) |
| 3B2 | おちゃする | Coffee | お茶する = go for a drink at a cafe (chat-up line); drink served is coffee, so related lines say coffee too (083, 0D1, 0FA, 0C7). Not Misako's Tomezo story (127): there it is コブちゃ (kelp tea, an old man's drink), so 'offered me diamonds if I went for a "nice cuppa".' (quoting him; Stephen 2026-10-30) |
| 3B3 | つかう | Use | |
| 3B4 | やくそくする | Promise | |
| 3B5 | しらべる | Search | |
| 3B6 | セーブする | Save | |
| 3B7 | のぼる | Go up | |
| 3B8 | おりる | Go down | |
| 3B9 | ひやかす | Tease | |
| 3BA | はりこませる | Watch | Nobuo stakes a place out; "Stakeout" was 8 letters (menu max 7), "Case" judged unclear as a bare command |
| 3BB | かう | Buy | 買う also means paying for a woman (女を買う); a girl answers Buy on a date with that reading (035: "Buy what? I'm not on the menu, you know.") |
| 3BC | おがみたおす | Beg | "pray at them till they give in": persistent pleading. After beating Kitamura (1D8) the JP has Nobuo put his palms together (おがむ) as for the dead: "キタムラも 成仏"; English: "Make him beg for mercy? Too late, Guv. He's a goner... Kitamura, rest in peace." (Stephen, 2026-10-25). 0F1 ("Mm, nice grovelling.") is the reaction to Beg in 367 (JP: "I like how humble you are") |
| 3BD | わたす | Give | |
| 3BE | さけぶ | Shout | named in dialogue (1BA) |
| 3BF | のる | Ride | kiddie ride, trains. Tanaka (1D5): のる = "be up for it" and Nobuo gets むしゃぶるい (pre-fight shivers); English ties it to Ride: "Ride roughshod over a swot, Guv? Ooh, I'm shaking with excitement!" (Stephen, 2026-10-25). Not in Misako's coffee-shop date (menu $20): there the JP のる is a cheeky option that reads as an outright request in English, so that one slot shows Give instead ("give her a present" / "give her one"); she answers "Wh-what?!" (07F) and Nobuo "Cor, Guv! Steady on!" (additions.NOBUO_STEADY, also after Sleep). Stephen, 2026-10-21 |
| 3C0 | かくれあるく | Sneak | |
| 3C1 | おいかける | Chase | |
Menu slot width is unknown (JP max 6 kana): confirm in stage 6 before finalising.
