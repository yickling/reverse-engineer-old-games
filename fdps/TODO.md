# Work log

Part of the [FDPS notes](README.md). This is the remaining work to play a battle from [extract](extract/). It is not a finding about the program. A finished item is checked here. Findings stay in the topic files.

Map pictures, fight frames, text, named waves, `SAF` samples, the stat tables, and the scenario packs are already in [extract](extract/). `ui/FIGBAR` is already colored from `Fight.pal`. `extract/` stays on disk and is not committed. The local copy of the program is only read. Do not create or change files there, and do not name that directory in a note.

The files for a battle share one shape. Indexes 0 through 64, except 30, are packed as JSON, and the rules that differ per scenario are still the programs in [Turns](turns.md), [Scenario files](scenario.md), and [Session](session.md).

## Open

### A 1:1 of the play

The campaign page is the battle, the chain, the village, and the discs. The study is the gameplay. The gift selector, the studio files, the sample driver, the Miles bodies, the CD device calls, and the heap walk are discarded. The title plays `intro/video.mp4`. The page plays the extracted waves and the disc tracks as files. The save sum and the byte walk are in [Save](save.md).

The later indexes were checked against the campaign tables. Nibble 11 brings back every gone unit of characters 85 and 106 before the spell. Handler 0 spawns scenario 2's groups. A buy waits for accept, and the trade-in credit applies only when the class may wear the bought type. A sale picks a roster member, waits for accept, and plays the income wave. From scenario `0x17` on, roster index 3 does not confirm.

Checked against the page, and matching: every unfrozen side-2 unit can be ordered. A move blocks the walker's own side and the other sides' neighbours. Gather walks those units, and a step pair on the way can run. Rest, the level roll, a blow's experience, the bag of eight, and the spell bits match. After a win the living return healed and a dead member stays out. The village, the bar load, and a skipped village's slot prompt match. Blessing changes each count on its own, and a counter requires the inner byte to be 1. Items `0xa6`, `0xa7`, `0xb1`, and `0xb3` add 15 to the second pool. A spell and an item apply over the area, with the kind table and the spell formula. The battle bag is use, give, equip, and discard. Opcode 99 shows scenario strings `0x10`, `0x11`, `0x13`, `0x14`, and `0x15`. A give shows string `0x1fd`. The enemy's long ranking uses a budget-100 fill. A death record walks every copy, returns only when the passed unit is not side 2 or is already gone, and string `0x1e6` names the item. A tied spell is cast when its id is below `0x12` and its power is at least attack minus defense, and when its id is `0x12` or more unless bit `0x40` is set. A heal spell counts only a pool below a third or a half. Kind `0x21` on character 9 learns spell 29. The quake redraws 25 times. Key `0x3b` opens the scaled section through seven frames and closes through six. The status sheet opens through steps 0 through 8 and closes through steps 5 down through 0, and the spell rectangle is filled from each block's centre. The shop window plays its nine steps. The roster shows six cells and steps by one and by three. Maps 5, 7, and 29 draw their second plate, and the walk stays on section 0. The fight bars, the status-sheet hit slots, the chapter fade, the frozen sprite, and the cursor slide match. Menus keep the system font.

The gameplay in [Gaps](gaps.md) is complete. The page against the program is the second list in that file. That list is complete.

### A higher-resolution picture

The plan is [reconstruction/REMASTER_VISUALS.md](../reconstruction/REMASTER_VISUALS.md). It waits until index 1 can be won and lost. The buffer goes to 960×600 through one constant in `demo/src`. Pictures are replaced only for this visit, after that constant is in and the page still plays. The rules stay in tiles.

### What the chapter-1 recording still shows

This section is the chapter-1 recording from before the later checks. It is not the current list. The battle in [reconstruction/demo](../reconstruction/demo) can be finished. A play of the chapter-1 recording, and the notes, still show the pieces below. The pictures are already in [extract](extract/) unless a row says they are absent. Do not invent a file the archives do not hold.

The command squares are `COMMAND` pictures 26 and 27, drawn behind the glyph. Picture 26 is the open square. Picture 27 is the filled square, used while that corner is selected. The demo draws the glyph only. No new extract.

The dialogues are opcode 3 of `ICON00`, including the scenes it loads before it stores index 0. The walk is in [Opening](opening.md). The strings, the portraits, the message box, and the `ICON####` clips are already extracted. Opcode 8 asks for `Icon%04d.wav`. No member of that name is in the archive, in [File formats](formats.md). Leave it silent. The message box stamps the cells in `extract/text/glyphs/`. The indexes are `extract/text/indexed/`.

The win and loss window is `ui/WINFAIL`. The empty-tile menu's first corner opens it, in [Text](text.md). It draws scenario strings 2 and 3, the scenario number, the turn, the money dword, and the living counts of sides 0, 2, and 1. The demo draws the words "win" and "loss" instead. A loss of the visit plays `videos/title/gameover`. A win plays the `Win00` script, which loads further scenes before the next index, in [Scenario files](scenario.md). Both are already extracted.

The intro is the title, then `ICON00`, then `videos/title/chapter`, in [Opening](opening.md). `ui/STBOARD` and `ui/STSEL` are the title. `videos/title/logo` is the studio mark before the title. `FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud` are absent. Do not extract a substitute.

The phase change plays `videos/title/enyphase` before the enemy walk and `videos/title/plyphase` when the cursor returns. Both are already extracted. The turn card before the player clip is `object 1 + 0xe810`, in [Turns](turns.md). The page draws that slide from `extract/effects/TURN/`.

The poison mark is `ui/ICONSTS` picture 3, the skull. The five pictures follow bytes `+0x23`, `+0x22`, `+0x24`, `+0x25`, and `+0x27`, and picture 3 is `+0x25`. Its top sits 12 rows below the sprite's top, in [Pictures](pictures.md). The opener stores 11 in slot 2's `+0x25` and 100 in its hit points before the visit, in [Opening](opening.md). While `+0x25` is nonzero the phase tick subtracts a tenth of the maximum. The demo skips that store and does not draw the mark.

Items are the right-hand corner of the unit menu, in [Turns](turns.md). Character 0 carries two copies of item 180, kind `0x0b`, which adds hit points and is consumed, and item 222, kind `0x16`, which clears `+0x25`. That is the cure for the ally's starting count. The kind table is in [Combat](combat.md). `ui/ITEM`, `ui/SELBAR`, `ui/NUMBER`, and the cure and heal clips are already extracted.

The same recording shows three more panels the demo does not open. None of them needs a new extract.

- The status sheet, `ui/STATUS`, when the cursor confirms a unit that is not waiting for an order. The pixels are in [Pictures](pictures.md).
- The terrain panel, `ui/ADWIN`. A new game stores the byte that shows it, in [Opening](opening.md) and [Turns](turns.md). It draws the tile and that terrain's attack and defense percents.
- The search on the fourth command corner. Scenario 0 has two cells whose attribute byte 0 has bit `0x20` set and two with bit `0x40` set. Two of those cells have a zero detail byte, and that byte is find index 0, in [Turns](turns.md).

Music stays the absent CD tracks. Do not synthesize them.

The battle loop stays. New screens call the clip player, the message box, and the diamond it already has. Each step below is playable on its own, and the visit still starts.

1. Draw, in `game.js`. Behind each command glyph, picture 26, or picture 27 while that corner is selected. After each sprite, the `ICONSTS` picture for the first nonzero byte among `+0x23`, `+0x22`, `+0x24`, `+0x25`, `+0x27`, top 12 rows below the sprite. While the terrain byte is set, `ADWIN` at the corner the notes give, with the tile and that terrain's two percents. Digits come from `NUMBER`.

2. The two stores the opener makes on slot 2, in `rules.js`: poison count 11, hit points 100. The phase change already heals side 2. In that same change, a nonzero `+0x25` subtracts a tenth of the maximum from hit points, then the count drops by one. The skull is then visible on the ally from the first frame, and it ticks down.

3. A clip player. It reads a `clips.json` or a `videos/` frame list, holds each frame for its `hold`, and returns. Call it with `enyphase` before the side-0 walk and `plyphase` when the cursor returns. The turn card is already in [Turns](turns.md). The page draws that slide from `extract/effects/TURN/`.

4. Panels on the cursor the demo already has. Confirm on a unit that is not taking an order opens `STATUS` and stamps the sheet in [Pictures](pictures.md). Enter waits, and the close can be the picture cut back in one step. The empty-tile diamond's first corner opens `WINFAIL` and stamps strings 2 and 3, the scenario number, the turn, the money, and the three side counts at the pixels in [Text](text.md). The right corner of the unit diamond opens the carried list. Kind `0x0b` adds hit points and consumes the pair. Kind `0x16` clears `+0x25` and consumes the pair. Both play the clip named in [Combat](combat.md). Spell stays disabled. The fourth corner searches a tile whose attribute byte masked with `0x60` is `0x20` or `0x40`. The detail byte, including 0, is the find index, and a flag per index starts clear. The give and the gold are in [Turns](turns.md).

5. One script walker over `extract/icon/icon00.json`, then the same walker over `extract/icon/win00.json` when the outcome is a win. An opcode 17 loads that index's pack and rebuilds the map. Opcode 3 uses the message box the loss line already uses. Opcodes 1 and 2 walk and face with the path player the battle uses. Opcodes 5, 13, and 16 move the camera. Opcodes 10, 11, and 12 place, hide, and show. Opcode 4 spawns, which `buildState` already knows how to do. Opcode 6 plays an `videos/icon` clip through the clip player. Opcodes 7 and 8 are silent. Opcodes 14 and 15 fade the canvas to black and back. The walker runs to opcode 0, then `CHAPTER` plays, the slot-2 stores from step 2 are applied if the script has not already done them, and the visit starts. A loss plays `gameover` instead of the win script. The title, `STBOARD` and `STSEL`, is the screen before the walker. New game is the only row this demo needs.

The decoded strings are the lines. A shadow one pixel down and to the right is enough. The 16×16 font is not required for this pass.

### A playable scenario-0 battle

One visit, in JavaScript, from the moment the cursor moves until outcome 1 or 2. The picture is the 320×200 screen in [Pictures](pictures.md), scaled nearest-neighbor. The battle reads [extract](extract/) and the notes, and does not open the data files.

The map is one 30×24 section. The player is side 2, the roster prefix of one, character 0 from `tables/friaprda.json`. The ally is side 1 and moves itself. The other 21 units are side 0. Losing the player or the ally loses the visit. Every side-0 unit gone wins it. Phase nibbles on this map are 0, 1, and 3. Nobody has a learned spell. Weapons reach the next tile.

Start at the icon instruction that stores index 0. Apply the spawns and the one tile placement. Skip the walks, the faces, the icon clips, and the music. The enemy phase is the swing path of those three nibbles, including the flood fill and the tile where a unit stops, in [Turns](turns.md). The player gets move, attack, and wait. The loss line is scenario string 15, with portrait 12. The cues are `BEEP`, `MISS`, `REST`, and the `EXPLO` sample.

A player attack always plays the fight. The menu does not read the animation byte. The backdrop is `backdrops/`, chosen from the defender's terrain. The standing body is `stands/` and the swing is `attacks/`, both by character id. The bars are `ui/FIGBAR`, and the fill widths are the ones in [Pictures](pictures.md). The motion is the slide, the strike, and the shake in that file. A frame whose hit mark is set is when the fill changes. The pool math is the same either way, in [Combat](combat.md). Draw the decoded frames as they are. A chunk the fight blends is already expanded as a solid pixel. The blend tables are in `extract/blend/`, and a remake can use alpha `strength / 16` instead, in [Pictures](pictures.md). The seventeen empty effect clips are not on this map.

The enemy swing does read the animation byte. Clear, it applies the pools on the map. Set, it plays the same fight. The settings corner flips the byte. The byte in the image is 1, and a new game has not stored it, so the visit begins with the fight, in [Combat](combat.md). The corner is present so the map path can be turned on. A death returns to the map and plays `effects/EXPLO` on that tile.

The item corner, the opening script, and the panels around the cursor are the chapter-1 item above. Music stays the absent tracks. The seed at the first command depends on how many ticks have fired, so the rolls will not repeat one DOS session.

One person, with these notes, about 14 days. The range is 12 to 16. Drawing the map and placing the units is 3. The player's move, attack, and wait is 2. The fight, including the slide and the bars, is 4. The enemy walk for nibbles 0, 1, and 3 is 3. Win, loss, the death clip, the settings corner, and playing both outcomes is 2.

Done when a player can win the visit and can lose it, and both outcomes follow the index-0 checks.

### A roster for the index being played

The order after this visit is [reconstruction/CAMPAIGN.md](../reconstruction/CAMPAIGN.md). The roster is step 3 there. The disc player is already in the page. Indexes below 18 are disc 1, and the same track number on disc 2 is a different recording.

The battle copies a prefix of the campaign roster. The prefix length is byte 1 of the map. Who stands in it is the append list in [Session](session.md): scenario 0 adds character 0, and later openers add the others. The map file does not store that list.

One person, after the scenario-0 visit exists, about 1 day.

Done when starting at an index later than 0 places the roster those earlier openers would have built.

### The programs that differ per scenario

The map file stores a handler number, a phase nibble, and a scenario index. The behavior is the disassembly in [Turns](turns.md) and [Scenario files](scenario.md). A loader that only draws the JSON will miss reinforcements and the win rule. The order for the page is [reconstruction/CAMPAIGN.md](../reconstruction/CAMPAIGN.md): the flood uses the loaded map, then the win table, the roster, and the chain. The village is part of that chain, because winning index 0 opens it.

Turn those programs into a table the engine runs:

- Win and loss. The shared test is that every side-0 unit is gone, and most indexes then lose if slot 0 is gone. The other indexes add a turn limit, a set of slots, or one of the two campaign flags. Scenario 0 adds the ally.
- Turn rows and detail-byte steps. Eighteen battles name a handler. A handler spawns a group, shows a string, rewrites a phase nibble, gives an item, or sets an outcome. The handlers on maps 7, 15, and 24 also branch on a confirm and on what the unit carries.
- The phase scripts this map does not use. Scenario 0 uses nibbles 0, 1, and 3. The other nine are in the same table, including the walk to a detail byte and the ones that cast or use an item.
- Spells and item use, on the player menu and on the enemy scorer. Scenario 0 has neither learned spell.
- Openers and endings. An opener is the same four calls, plus an append or a pool write on some indexes. An ending plays its script and stores the next index. Index 26 can quit. Index 29 ends the game.

One person, after the scenario-0 visit exists, about 18 days. The range is 15 to 20. The win and loss table is 2. The eighteen handlers are 5. The other phase nibbles, spells, and item use are 6. The opener and ending walker is 3. Playing a few indexes past 0 is 2. Scenario 0's own opener, the one the first visit skips, is this walker.

Done when loading a packed index runs that index's win rule and its handlers, and a phase nibble the unit stores resolves with the row in [Turns](turns.md).

## Done

- [x] The sale, the equipment table, and roster index 3

Checked in `demo/src/flow/campaign.js`, `demo/src/ui/keys.js`, and `demo/src/assets.js`. A sale shows interface string `0x1fc` and removes the pair only on accept. A buy shows interface string `0x1f6` before any money moves. The credit is subtracted only when the class row in `tables/proequ.json` contains the bought type and an equipped item in that type group was found. Equipping a type that is not in the row leaves the item in the bag. The row is the class id. When the scenario index is at least `0x17`, Enter and Space on roster index 3 leave the member list open. The goods list and the rank list still confirm.

- [x] A buy price below 0 draws the minus glyph

Checked in `demo/src/view/screen.js`. A shop buy row whose net price is below 0 draws NUMBER glyph 11, then five digits of the absolute value. A price of 0 and a price above 0 stay on the five-digit drawer, with no plus. Sale rows and the money total still use that drawer. The pay in `demo/src/flow/campaign.js` is unchanged: a price above 0 comes out of the money, and a price at or below 0 is added to it.

- [x] The rescue, handler 0, and the buy credit match the program

Checked in `demo/src/flow/turns.js`, `demo/src/flow/handlers.js`, and `demo/src/flow/campaign.js`. Nibble 11, for a mover whose character id is 60 through 62, moves every unit of character 85 or 106 whose gone bit is already set, before the spell is scored. A unit of those ids that is still present stays. Handler 0 reads scenario 2's actors and coordinates, places them on the current map, and leaves the loaded map in place. A buy credits the first equipped item of types 1 through `0x15` when the bought type is at most `0x15`, and of types `0x16` through `0x27` otherwise. A price above 0 is paid from the money. A price at or below 0 is added to the money. The sale price is unchanged.

- [x] Nibble 11 brings the two units back before the spell

Checked in `demo/src/flow/turns.js`. When the phase nibble is 11 and the mover's character id is 60 through 62, character 85 is placed from `(5, 12)` and character 106 from `(15, 13)` before `chooseEnemyAction`. Each lands on the nearest open tile of terrain below 5, the heal clip plays, the gone bit is cleared, and hit points are filled. The spell is scored after that. Any other nibble leaves them where they are.

- [x] The later indexes match the campaign tables

Checked against [CAMPAIGN.md](../reconstruction/CAMPAIGN.md) in `demo/src/rules/combat.js`, `demo/src/rules/orders.js`, `demo/src/flow/handlers.js`, `demo/src/flow/campaign.js`, and `demo/src/field/world.js`. The win and loss tests, the death bytes 4 and 5, the roster appends, the village skips, and the turn-row and detail handlers match those tables. Handler 21 is not called. Item kinds `0x05`, `0x06`, `0x0d`, and `0x1b` are still unused. Nibble 11 still scores the spell before the rescue. That order is the next item.

- [x] The title plays the studio movie

Checked in `demo/src/main.js`, `demo/src/flow/presentation.js`, `demo/src/view/screen.js`, and `server/index.js`. `intro/video.mp4` is served at `/intro/` as `video/mp4`. After `LOGO.SAF`, and again after the menu sits for 1500 frames, that file is drawn fitted inside the 320×200 canvas on black. The title track is stopped while it plays and started again for the menu. A key skips it. A menu choice cancels the idle wait. There is no second file. A browser that blocks `play()` before a click drops the movie and opens the menu.

- [x] The bonus closing lines do not wait

Checked in `demo/src/flow/campaign.js`. After the second playback loop, interface string `0x225` plus the closing-table value is stamped at (20, 131) over the last frame, then string `0x229` at the same pen. Neither wait is a key. The flag is stored after the second line. The mid-clip key wait, the date test, and the refusal to give a gift are unchanged.

- [x] The turn card, the glyph stamps, and the bonus clip

Checked against [TURN_CARD.md](../reconstruction/TURN_CARD.md), [GLYPHS.md](../reconstruction/GLYPHS.md), and [BAR_BONUS.md](../reconstruction/BAR_BONUS.md). `playPhaseCard("PLYPHASE.SAF")` draws the thirteen inbound steps, holds 13 frames, then the outbound steps from 92 back through −60, over a frozen copy of the map, and `ENYPHASE.SAF` does not. The digits are the turn counter with no padding, frame `character - 0x2f`, 28 pixels apart, at y 72. The message box stamps `extract/text/glyphs/` from `extract/text/indexed/`, pen 138 and `messageTop + 11`, advance 16, line 18, with no wrap. The bonus corner plays `BONUS-1.SAF` at (0, 0) only when the local date is 28 January 1998 and `bonusSeen` is 0, then stores 1. It gives no item and no money, and it does not load `BONUS.WAV`. The two closing lines each wait for a key. That wait is the next item.

- [x] The four stops stay empty

Checked against [TURN_CARD.md](../reconstruction/TURN_CARD.md), [BAR_BONUS.md](../reconstruction/BAR_BONUS.md), [STUDIO_MOVIE.md](../reconstruction/STUDIO_MOVIE.md), and [GLYPHS.md](../reconstruction/GLYPHS.md). `ENYPHASE.SAF` still plays before the enemy walk and `PLYPHASE.SAF` still plays after the turn increment, with no card between them. The bonus corner still returns null. The title still plays `LOGO.SAF` and then stays on the menu, and `extract/videos/movie/missing.json` still names `FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud`. Dialogue is still the decoded line in the system font.

- [x] The spell list closes with its rows

Checked in `demo/src/view/screen.js` and `demo/src/ui/commands.js`. The open still grows the 151×149 rectangle through margins 2, 4, 6, 8, and 10 before the rows are drawn. Escape and a confirmed spell set the keep flag, then run 10, 8, 6, 4, and 2. The rows are drawn inside the same clip as the panel for each of those steps, and the flag is cleared when the steps end. The page turn at selectors 1, 3, 5, 7, 9, 11, 13, and 15 is unchanged.

- [x] Weapon chance, level-card numbers, and the spell-list open

Checked in `demo/src/rules/combat.js`, `demo/src/view/screen.js`, and `demo/src/ui/commands.js`. Inside `rollHit`, before the landed roll, swing 4 writes status index 3 to `rand % 4 + 2` when `rand % 100` is below `at_0x0a`, and swing 1 writes status index 4 to `rand % 2 + 2`. Both writes are skipped for class `0x19`, `0x21`, `0x22`, `0x24`, `0x25`, or `0x26`, and for character id `0x3c` through `0x44`. Swing 3 adds `at_0x0a` to the crit chance of that roll. Swing 2 is still the second blow. The level card, already at screen `(78, 68)`, stamps the new level and the five amounts from NUMBER row 0 with no padding and no sign, at the six card pixels in [Pictures](pictures.md). A learned spell is interface string `learned id + 0x1be` at card `(72, 45)`. The map frame at screen `(148, 81)` steps frames 0, 1, 2, 1, and the card holds for 250 ticks or a key. The spell list is the 151×149 rectangle at `(152, 47)`. It opens through margins 2, 4, 6, 8, and 10, then draws the rows. More than eight spells turns the page at selectors 1, 3, 5, 7, 9, 11, 13, and 15. The close is the next item.

- [x] A sold equipped item comes off

Checked in `demo/src/flow/campaign.js`. `sellHeld` pays, clears that bag slot, and `clearEquipped` writes the empty id over every equipped slot that held it. `giveCorner` uses the same clear. `equipHeld` still leaves the id in the bag, and that row is the mark until the sale or the gift.

- [x] The campaign page

Checked against [CAMPAIGN.md](../reconstruction/CAMPAIGN.md). A walk calls a detail pair with argument 0, and a finished action calls it with argument 1, including the player's. The handler runs only when `match` equals that argument. Map 7 turn 3 runs `icon/icon7-1.json`, and the detail clip runs `icon/icon7-3.json`. The five village doors keep their own corners. The bar saves, loads, and quits. The church changes rank, gives, and opens the status sheet. The item shop buys from group 0. The weapon shop buys from group 1 and equips. The secret shop buys from group 2, equips, and opens the sheet. The sale price and the buy price were left as they were. The bonus clip stays unplayed.

- [x] Play the disc tracks

Checked against [FIXES.md](../reconstruction/FIXES.md) in `reconstruction/demo/game.js`. One looping element plays `/audio/cd1` or `/audio/cd2` as `track-NN.flac`. The short-wave decoder is unchanged. The title starts track 2 after the logo and stops it on quit. Opcode 7 plays the byte plus 1, and 255 stops. Opcode 8 stays silent. An index below 18 selects disc 1, 18 through 29 select disc 2, and 30 or more leaves the disc. Argument 1 starts just before `sidePhase(0)`, and argument 0 starts just after each `PLYPHASE`, including Continue. A new game's first turn keeps the opening's last track. The same track is not restarted. The node server, the type map, nginx, and the image copy all serve `/audio/`. `extract/` and the picture URL were left as they were.

- [x] Skip the opening

Checked against [FIXES.md](../reconstruction/FIXES.md) in `reconstruction/demo/game.js`. Escape sets the flag only while a new game is between the icon script and `visit`, and that press releases the current redraw waits and the current key wait. A walk still commits each pass once, a dialogue closes its box, and a fade ends on the value it was going to. The map load, the spawns, and the placements still run, and the checks after the script are still there. `visit` clears the flag before the first turn and still applies the ally's poison. The logo, Continue, the enemy walk, and the chest question do not use the flag.

- [x] The yes and no on a chest

Checked in `reconstruction/demo/game.js`. Frames 4 through 13 of `ui/SHADOW` are loaded beside the unit shadow. While a question is showing, choice 0 cycles frames 4–7 at `(229, 103)` and holds frame 13 at `(255, 103)`, and choice 1 holds frame 8 and cycles frames 9–12. The y moves with the message box. Left and right change the choice. Enter and Space accept only choice 0. Escape and Delete refuse. Save, load, and quit use that same choice.

- [x] Search a chest from the down corner

Checked against the search in [Turns](turns.md), in `reconstruction/demo/game.js`. A detail byte of 0 is find index 0. The down corner shows the line, plays `Chess.wav`, gives the item or the gold, and adds 1 to a picture whose mask is `0x20` or `0x60`. A full bag can drop a pair, and that swap leaves the flag clear. The sixteen flags and the picture indexes are in the snapshot. The yes and no pair is the item above.

- [x] Pause while the page is hidden

Checked against [FIXES.md](../reconstruction/FIXES.md) in `reconstruction/demo/game.js`. `pump` does not call `tick` while `document.hidden` is set, and a callback in that time stores the timestamp in `lastTick`. The first visible frame sets `lastTick` to that timestamp before the tick loop. The cap of 3 ticks remains. `waitRedraws` was left as it was, and audio is not paused.

- [x] Dialogue as strings

Checked in `reconstruction/demo/game.js`. `drawMessage` draws each stored line with the font's advance, wraps inside the column that ends at x 302, and starts the next row 18 pixels down. A line whose top passes the bottom of the message box is not drawn. The portrait and the page split were left as they were.

- [x] Continue, and the terrain panel during a script

Checked against [FIXES.md](../reconstruction/FIXES.md) in `reconstruction/demo/game.js`. `applyBattle` copies the saved detail with `slice`. Title Continue sets the mode to `ai` before the player clip, and `playerPhase` then takes the cursor when the side-2 unit can still act. The panel is drawn only while both gates are set. A new game sets the first. The second is set when `playerPhase` takes the cursor and cleared when that phase returns and when a script starts. `rules.js` and the asset URL were left as they were.

- [x] Item rows, the heal number, and the dialogue pen

The status sheet and the battle list both call the row drawer in [Turns](turns.md). Each carried pair draws its mark, its name, and the attack, defense, or amount picture with four digits. The selection bar is the list's current row. A kind `0x0b` use adds the spread and draws it with digit row `0x27` before `Posion.saf`. The phase tick runs at the start of that side: side 1 before its walk, side 0 before its walk, and side 2 after the player clip. A page keeps the portrait from the previous page of the same string until a new mark replaces it, in [Text](text.md). Dialogue ink is palette `0xd0` and the shadow is `0x6d`. A line still breaks on the stored newline, and a line longer than ten cells continues on the next row inside the box.

- [x] Save and load the visit

The empty-tile diamond is the system menu in [Turns](turns.md): up opens the chapter panel, left saves, right loads, down quits. The record is the front of `FDE.SAV` in [Save](save.md), written to local storage under `fdps.fde.sav` instead of the file. Title row 2 resumes it and skips the opener. Title row 1 opens `Load.cel`. Its three bars are the campaign slots, which this visit does not write, so a bar with no slot refuses. The sum and the byte walk are in [Save](save.md).

- [x] What the chapter-1 playtest still breaks

Checked against [FIXES.md](../reconstruction/FIXES.md) in `reconstruction/demo/game.js`. The bag draws a 151×17 panel and opens on the first kind `0x0b` or `0x16`. A heal that does not raise hit points, and a cure on a poison count of 0, beep and stay in aim. F2 and Home open the sheet for the unit under the cursor, Escape closes it, and the eight bag names sit at (152, 55). Dialogue draws a 16px cell from (138, `messageY + 11`) with the stored breaks and a 10-cell wrap, and it does not clip. `loop` keeps leftover milliseconds, applies at most 3 ticks, and draws once. `playIcon` loads the clip before the waits. `[slot:N]` resolves to that unit's character, a page with no mark clears the face, and face 40 stays blank. `rules.js` and the asset URL were left as they were.

- [x] What an identical scenario 0 still has to read

The message blend, the section sort, the unit pass, the rising strip, the palette channels, the animation byte, the timer's one call of `rand`, index 0's two track bytes, and the glyph cells are in the topic files named in the item. `object 1 + 0x1fbd0` is the block-centre fill in [Pictures](pictures.md).

- [x] Blend tables, and the files the archives do not hold

Copy four files, unchanged, into `extract/blend/`. They are the mode 9 tables in [Pictures](pictures.md). Do not interpret them and do not give them a new role.

| File | Bytes |
| --- | --- |
| `Mer1.tmp` | 18432 |
| `Mer2.tmp` | 4096 |
| `FMer1.tmp` | 18432 |
| `FMer2.tmp` | 4096 |

`FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud` are paths the title passes on, in [Opening](opening.md). They are not members of an archive. When one of those files is present, copy it unchanged into `extract/videos/movie/`. When it is absent, name it in `extract/videos/movie/missing.json`. Do not download a copy and do not invent a decoder.

Tracks 2 through 19 are CD audio, in [File formats](formats.md). The recording is not a file in the data directory. Write `extract/music/missing.json` naming those tracks. Do not synthesize audio and do not read a drive.

The opener, the unread blitters, the animation byte, and the roll sequence are not files. Leave them.

Done when the four blend files match the source bytes, the movie list names only files that are absent, and the music list names tracks 2 through 19. Then check this item.

- [x] Fight frames, effect clips, and the index-31 tail

`scripts/extract_fight_sprites.py` already decodes a `SAF` frame. Run it with the data directory as its argument and `--out` as [extract](extract/). It writes four folders there, colored from `Fight.pal`:

| Folder | Members |
| --- | --- |
| `backdrops/` | Every `Back##.saf` in `BACKGRND.VFS`. One frame each. |
| `stands/` | Every `Stand###.saf` in `FIGHT.VFS`. |
| `attacks/` | Every `Act###.saf` in `FIGACT.VFS`. |
| `effects/` | Every `Magic###.saf` in `FIGHT.VFS`, and the effect `.saf` members of `MISC.VFS` the script already selects. |

The same decoder then opens `BaseAni.vfs`, the archive stored inside `MISC.VFS`, and writes `EasyAni.saf`, `Explo.saf`, and `Turn.saf` into `effects/`. Those three are the map explosion and the two clips beside it. Title clips are already in `extract/videos/`. Samples are already in `extract/sounds/`. Do not write either again. Leave the music out.

`M310.CEL` does not expand with mode 0. Do not write a new decoder for it. The skip already recorded for that section stays.

`M31.DTL` is 6545 bytes. The 51×64 tiles are already in `extract/scenario/31/dtl.json`. The 3265 bytes after those tiles have no reader. Write them, unchanged, to `extract/scenario/31/dtl-tail.bin`. Do not give them a role.

Done when the four folders are on disk, `effects/` contains `EasyAni`, `Explo`, and `Turn`, and the tail file is 3265 bytes. Then check this item.

- [x] Content packs for every index

Generalize `scripts/extract_scenario_records.py`. It takes the data directory as an argument. It writes every index from 0 through 64 into `extract/scenario/NN/`, in the same JSON shape as scenario 0. The structs are in [File formats](formats.md). A field the struct marks unread stays in the JSON with no role added. Text, pictures, samples, and the stat tables are already extracted. Do not write them again. Leave the music out. Include the shop file.

One index names these members. `NN` is the index as two digits.

| JSON | Member | Archive |
| --- | --- | --- |
| `map.json` | `MAPNN.DAT` | `FIELD.VFS` |
| `cod.json` | `MAPNN.COD` | `FIELD.VFS` |
| `dtl.json` | `MNN.DTL` | `FIELD1.VFS` |
| `dsc.json` | `DSCNN.DAT` | `FIELD2.VFS` |
| `sections/S/grid.json` | `M` + `NN` + `S` + `.MPL` | `FIELD1.VFS` |
| `sections/S/attr.json` | `ATTR` + `NN` + `S` + `.DAT` | `FIELD2.VFS` |
| `icon.json` | `ICONNN.DAT` | `ICONANI.VFS` |
| `shop.json` | `SHOPNN.DAT` | `FIELD.VFS` |

`shop.json` is the three groups of twelve item ids in [File formats](formats.md). `SHOP00.DAT` through `SHOP29.DAT` are the shop files. An index past 29 has none. A group ends at `0xff` or at the twelfth byte.

`S` is the section number from the `DSC` count. Scenarios 5, 7, 29, and 63 have two sections. The other indexes that have a `DSC` have one. Picture `N` of section `S` is the frame already extracted for that section's `.cel`.

Indexes 30 and 33 have no `MAP` and no `COD`. Skip 30. Index 33 has a detail file and a section-0 grid and terrain file, and no `DSC`. Index 31 has a map, coordinates, a detail file, and section 0, and no `DSC`. Where the `DSC` is absent, still write section 0 from `MNN0.MPL` and `ATTRNN0.DAT` when those members exist, and record the missing `DSC` in the directory. `M310.CEL` does not expand, so index 31 has JSON and no tile pictures. A member that is not in its archive is recorded and skipped. The run continues with the next index.

Every `.dat` member of `ICONANI.VFS` is an icon script: `ICON00` through `ICON29`, `ICON7-1`, `ICON7-2`, `ICON7-3`, `WIN00` through `WIN29`, `WIN17-1`, `WINGA26`, and `GOODEND`. Write each one to `extract/icon/`, one JSON file, with the opcode walk in [Scenario files](scenario.md). Opcode 0 ends the file. `icon.json` inside `extract/scenario/NN/` is the same walk of `ICONNN.DAT`, and only indexes 0 through 29 have that member.

Done when each index from 0 through 64 has been attempted, scenario 0 still matches the pack already checked, indexes 0 through 29 each have `shop.json`, a two-section index has two section directories, and every icon `.dat` has a JSON file that ends on opcode 0. Then check this item.
