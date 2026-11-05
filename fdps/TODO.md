# Work log

Part of the [FDPS notes](README.md). This is the remaining work to play a battle from [extract](extract/). It is not a finding about the program. A finished item is checked here. Findings stay in the topic files.

Map pictures, fight frames, text, named waves, `SAF` samples, the stat tables, and the scenario packs are already in [extract](extract/). `ui/FIGBAR` is already colored from `Fight.pal`. `extract/` stays on disk and is not committed. The local copy of the program is only read. Do not create or change files there, and do not name that directory in a note.

The files for a battle share one shape. Indexes 0 through 64, except 30, are packed as JSON, and the rules that differ per scenario are still the programs in [Turns](turns.md), [Scenario files](scenario.md), and [Session](session.md).

## Open

### A playable scenario-0 battle

One visit, in JavaScript, from the moment the cursor moves until outcome 1 or 2. The picture is the 320×200 screen in [Pictures](pictures.md), scaled nearest-neighbor. The battle reads [extract](extract/) and the notes, and does not open the data files.

The map is one 30×24 section. The player is side 2, the roster prefix of one, character 0 from `tables/friaprda.json`. The ally is side 1 and moves itself. The other 21 units are side 0. Losing the player or the ally loses the visit. Every side-0 unit gone wins it. Phase nibbles on this map are 0, 1, and 3. Nobody has a learned spell. Weapons reach the next tile.

Start at the icon instruction that stores index 0. Apply the spawns and the one tile placement. Skip the walks, the faces, the icon clips, and the music. The enemy phase is the swing path of those three nibbles, including the flood fill and the tile where a unit stops, in [Turns](turns.md). The player gets move, attack, and wait. The loss line is scenario string 15, with portrait 12. The cues are `BEEP`, `MISS`, `REST`, and the `EXPLO` sample.

A player attack always plays the fight. The menu does not read the animation byte. The backdrop is `backdrops/`, chosen from the defender's terrain. The standing body is `stands/` and the swing is `attacks/`, both by character id. The bars are `ui/FIGBAR`, and the fill widths are the ones in [Pictures](pictures.md). The motion is the slide, the strike, and the shake in that file. A frame whose hit mark is set is when the fill changes. The pool math is the same either way, in [Combat](combat.md). Draw the decoded frames as they are. A chunk the fight blends is already expanded as a solid pixel. The blend tables are in `extract/blend/`, and a remake can use alpha `strength / 16` instead, in [Pictures](pictures.md). The seventeen empty effect clips are not on this map.

The enemy swing does read the animation byte. Clear, it applies the pools on the map. Set, it plays the same fight. The settings corner flips the byte. The byte in the image is 1, and a new game has not stored it, so the visit begins with the fight, in [Combat](combat.md). The corner is present so the map path can be turned on. A death returns to the map and plays `effects/EXPLO` on that tile.

Leave the item corner and the opener's camera for later. This map does not use them to reach an outcome. Music stays the absent tracks. The seed at the first command depends on how many ticks have fired, so the rolls will not repeat one DOS session.

One person, with these notes, about 14 days. The range is 12 to 16. Drawing the map and placing the units is 3. The player's move, attack, and wait is 2. The fight, including the slide and the bars, is 4. The enemy walk for nibbles 0, 1, and 3 is 3. Win, loss, the death clip, the settings corner, and playing both outcomes is 2.

Done when a player can win the visit and can lose it, and both outcomes follow the index-0 checks.

### A roster for the index being played

The battle copies a prefix of the campaign roster. The prefix length is byte 1 of the map. Who stands in it is the append list in [Session](session.md): scenario 0 adds character 0, and later openers add the others. The map file does not store that list.

One person, after the scenario-0 visit exists, about 1 day.

Done when starting at an index later than 0 places the roster those earlier openers would have built.

### The programs that differ per scenario

The map file stores a handler number, a phase nibble, and a scenario index. The behavior is the disassembly in [Turns](turns.md) and [Scenario files](scenario.md). A loader that only draws the JSON will miss reinforcements and the win rule.

Turn those programs into a table the engine runs:

- Win and loss. The shared test is that every side-0 unit is gone, and most indexes then lose if slot 0 is gone. The other indexes add a turn limit, a set of slots, or one of the two campaign flags. Scenario 0 adds the ally.
- Turn rows and detail-byte steps. Eighteen battles name a handler. A handler spawns a group, shows a string, rewrites a phase nibble, gives an item, or sets an outcome. The handlers on maps 7, 15, and 24 also branch on a confirm and on what the unit carries.
- The phase scripts this map does not use. Scenario 0 uses nibbles 0, 1, and 3. The other nine are in the same table, including the walk to a detail byte and the ones that cast or use an item.
- Spells and item use, on the player menu and on the enemy scorer. Scenario 0 has neither learned spell.
- Openers and endings. An opener is the same four calls, plus an append or a pool write on some indexes. An ending plays its script and stores the next index. Index 26 can quit. Index 29 ends the game.

One person, after the scenario-0 visit exists, about 18 days. The range is 15 to 20. The win and loss table is 2. The eighteen handlers are 5. The other phase nibbles, spells, and item use are 6. The opener and ending walker is 3. Playing a few indexes past 0 is 2. Scenario 0's own opener, the one the first visit skips, is this walker.

Done when loading a packed index runs that index's win rule and its handlers, and a phase nibble the unit stores resolves with the row in [Turns](turns.md).

## Done

- [x] What an identical scenario 0 still has to read

The message blend, the section sort, the unit pass, the rising strip, the palette channels, the animation byte, the timer's one call of `rand`, index 0's two track bytes, and the glyph cells are in the topic files named in the item. `object 1 + 0x1fbd0` stays unread.

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
