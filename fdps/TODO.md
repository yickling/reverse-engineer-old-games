# Work log

Part of the [FDPS notes](README.md). This is the remaining work to play a battle from [extract](extract/). It is not a finding about the program. A finished item is checked here. Findings stay in the topic files.

Pictures, text, named waves, `SAF` samples, the stat tables, and the scenario-0 records are already in [extract](extract/). Music is a later extract. `extract/` stays on disk and is not committed. The local copy of the program is only read. Do not create or change files there, and do not name that directory in a note.

The files for a battle share one shape. Indexes 0 through 64, except 30, are packed as JSON, and the rules that differ per scenario are still the programs in [Turns](turns.md), [Scenario files](scenario.md), and [Session](session.md).

## Open

### A playable scenario-0 battle

One visit, in JavaScript, from the moment the cursor moves until outcome 1 or 2. The picture is the 320×200 screen in [Pictures](pictures.md), scaled nearest-neighbor. Combat uses the map path in [Combat](combat.md). The battle reads [extract](extract/) and the notes, and does not open the data files.

The map is one 30×24 section. The player is side 2, the roster prefix of one, character 0 from `tables/friaprda.json`. The ally is side 1 and moves itself. The other 21 units are side 0. Losing the player or the ally loses the visit. Every side-0 unit gone wins it. Phase nibbles on this map are 0, 1, and 3. Nobody has a learned spell. Weapons reach the next tile.

Start at the icon instruction that stores index 0. Apply the spawns and the one tile placement. Skip the walks, the faces, the clips, and the music. The enemy phase is the swing path of those three nibbles, including the flood fill and the tile where a unit stops, in [Turns](turns.md). The player gets move, attack, and wait. The loss line is scenario string 15, with portrait 12. The cues are `BEEP`, `MISS`, `REST`, and the `EXPLO` sample.

Leave the item corner, the fight clips, and the opener's camera for later. This map does not use them to reach an outcome.

Done when a player can win the visit and can lose it, and both outcomes follow the index-0 checks.

### A roster for the index being played

The battle copies a prefix of the campaign roster. The prefix length is byte 1 of the map. Who stands in it is the append list in [Session](session.md): scenario 0 adds character 0, and later openers add the others. The map file does not store that list.

Done when starting at an index later than 0 places the roster those earlier openers would have built.

### The programs that differ per scenario

The map file stores a handler number, a phase nibble, and a scenario index. The behavior is the disassembly in [Turns](turns.md) and [Scenario files](scenario.md). A loader that only draws the JSON will miss reinforcements and the win rule.

Turn those programs into a table the engine runs:

- Win and loss. The shared test is that every side-0 unit is gone, and most indexes then lose if slot 0 is gone. The other indexes add a turn limit, a set of slots, or one of the two campaign flags. Scenario 0 adds the ally.
- Turn rows and detail-byte steps. Eighteen battles name a handler. A handler spawns a group, shows a string, rewrites a phase nibble, gives an item, or sets an outcome. The handlers on maps 7, 15, and 24 also branch on a confirm and on what the unit carries.
- The phase scripts this map does not use. Scenario 0 uses nibbles 0, 1, and 3. The other nine are in the same table, including the walk to a detail byte and the ones that cast or use an item.
- Spells and item use, on the player menu and on the enemy scorer. Scenario 0 has neither learned spell.
- Openers and endings. An opener is the same four calls, plus an append or a pool write on some indexes. An ending plays its script and stores the next index. Index 26 can quit. Index 29 ends the game.

Done when loading a packed index runs that index's win rule and its handlers, and a phase nibble the unit stores resolves with the row in [Turns](turns.md).

## Done

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
