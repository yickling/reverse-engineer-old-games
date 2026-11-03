# Selection, turns, and outcomes

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_0002b870` is the body of one visit to the map. It polls a byte from `FUN_00056509`. A new key is handled immediately. Repeats 1 through 5 skip movement; after that the key repeats. The visit returns only when the outcome dword is nonzero or the system menu returns nonzero. That exit, and what the session does with the outcome, is in [Session](session.md). The effects below are what the comparisons do. The names in parentheses are the BIOS scan codes for those bytes.

| Byte | What it does |
| --- | --- |
| `0x48`, `0x50`, `0x4b`, `0x4d` (arrows) | Move the cursor one tile, inside the map, and play `Beep.wav`. |
| `0x01`, `0x2c`, `0x4c`, `0x53` | Center on the next side-`2` unit whose flag byte has bits `0x85` clear. |
| `0x39`, `0x1c` (space, enter) | `FUN_0002d830` picks the unit under the cursor. None opens `FUN_00014aa0`. A side-`2` unit with bit `0x80` clear and `+0x26` clear goes to `FUN_00015460`, then `FUN_0002e7a0` if the outcome dword is still 0. Anything else goes to `FUN_00016a90`. |
| `0x3b` | `FUN_0002def0`. |
| `0x3c`, `0x47` | `FUN_00016a90` on the unit under the cursor. |

The camera follows the cursor, keeping it away from the edges by a margin of about two tiles (`0x18` on the near side, `0x108` horizontally and `0x90` vertically on the far side).

`FUN_00015460` is the move. It flood-fills from the unit with budget `+0x3b`, then asks for a destination. Cancelling recenters and leaves the loop. A destination whose path result is 0 opens a menu (`FUN_00015cf0`) without changing the tile. Any other accepted destination writes the new tile into bytes `+0` and `+1` unless `DAT_00060004` is set, in which case the unit stays and the action is committed through `FUN_000119b0`. After the loop, if `DAT_00069d90` is not `0xff`, it calls `(&DAT_000601c4)[DAT_00069d90](unit)`. It always then calls `(&DAT_0006028c)[scenario]()`. The flood fill and the terrain costs are in [Map](map.md).

`FUN_00015cf0` keeps four disable flags. Slot 0 is disabled when `FUN_00025110(unit, 0)` finds no weapon or `FUN_00011e50` lists nobody. Slot 1 is disabled when `FUN_00027810` returns 0 or byte `+0x27` is nonzero. Slot 2 is disabled when `FUN_00025210` returns 0. The first flag that is still 0 is the initial selection. Choosing slot 0 runs the attack in [Combat](combat.md) and then `FUN_000119b0`, which ORs bit `0x80` into byte `+5`. Slot 1 is `FUN_00027bf0`. Slot 2 is `FUN_00025280`. Any other slot calls `FUN_000120d0` when the menu was opened without a move, then `FUN_000184e0` and `FUN_000119b0`. `FUN_000120d0` is the rest below. `FUN_000184e0` is the search of the cursor tile, also below.

`FUN_00027bf0` stays in a spell list until one cast is confirmed. `FUN_00028100` reads up and down. A window of eight rows follows the selection. Enter or Space returns 1 when byte `+5` of the spell row is at or below `+0x44`, and stays on the list when it is not. Escape or Delete returns −1, which leaves the command menu. The id comes from `FUN_00027810`. Byte `+3` of the spell row decides the aim. The mask it paints, and the line taken when that byte is 16 or more, are in [Combat](combat.md). Zero lists targets from the cursor tile at range byte `+4`, with the side filter fixed at 0, and the cursor picker runs in mode 4, or mode 5 when that list is empty. Nonzero first lists at range byte `+3` with the side byte at `+6`. At 15 or below it then lists again at byte `+4`. At 16 or above the second list is the line from the caster toward the cursor, and `Chess.wav` plays. Id `0x15` refuses a list whose first id is the caster, and a confirmed aim stores the cursor tile at `DAT_0006437c` and `DAT_00064380` before a second confirm. A confirmed cast always calls `FUN_0001a4a0`, then the death spin and the death-record walk. The experience term is divided by `+0x21`, plus `0x1e` when the character id is above 8, and `FUN_0001dd00` applies it.

`FUN_00025280` draws a second menu through `FUN_00016120` and reads it with `FUN_000161f0`. Those two, and `FUN_000161a0`, were not decompiled. Cancelling returns. Row 0 picks a carried index with `FUN_00025990`, reads the id at `+0x0b + index * 2`, aims with the record's range byte `+0x10` and effect byte `+0x12`, and calls `FUN_00026270`. Record byte `+0x0d` of `0x1c` or `0x19` asks for one more confirm and stores the cursor tile the same way id `0x15` does. A confirmed use then calls `FUN_000119b0` and returns 1. Row 1 picks an item and a unit on the cursor tile. `FUN_00025cf0` returning −1 swaps one item each way through `FUN_00025c90`. Any other return removes the giver's item. Both paths call `FUN_00024d40` and return 2. Row 2 is `FUN_00025d70`. It lists the pairs. `FUN_00025fb0` returns 1 when one of six bytes from `FUN_00018b90(class)` equals the item record's first byte. A row that passes calls `FUN_00026040`, plays `Equip.wav`, and rebuilds the combat words. `FUN_00026040` clears bit `0x40` on other pairs in the same group, then stores `0x40` in the chosen pair's flag. The group is the record's first byte: below `0x16` is one group, and `0x16` or above is the other. A first byte of 0 does not clear another pair. Any other menu row removes the picked item with `FUN_00025c90` and calls `FUN_00024d40`.

`FUN_00025990` plays `OpWin1.wav` and returns what `FUN_00025af0` chooses. That picker counts pairs whose flag bit `0x80` is clear and moves an index inside that count. Up and down wrap, and each plays `Beep.wav`. Enter or Space returns 1. Escape or Delete returns −1. The use row passes 1 as the second argument, and then Enter is refused while byte `+0x0d` of the record is 0. The other calls in `FUN_00025280` pass 0, so Enter accepts the row. Give and remove keep the empty pairs at the end, so this index is the pair index.

`DAT_0006028c` is a table of code pointers indexed by the scenario, parallel to the ending table at `0x60304` and the opener table at `0x60074`, but not the same pointers. The first is `0x3a120` and the last, index 29, is `0x3b7c0`. These bodies were not created as functions. The disassembly below is not a decompile. `FUN_000109b0(slot)` returns bit 0 of that unit's byte `+5`. The session loop treats outcome `1` as `GameOver.saf` and outcome `2` as the per-scenario ending.

`FUN_0003a050` is the check most of the bodies call. If the outcome is already nonzero it returns. It stores 2, then walks every slot. A side-0 unit whose bit 0 is still clear stores 0 again, so 2 remains only when every side-0 unit is gone. After that walk, scenario indexes `0x10` and `0x15` store 1 when slot 3 is gone. Every other index stores 1 when slot 0 is gone.

Indexes 1, 6, 11, 12, 13, 15, 17, 20, 27, and 28 call that and return. Index 0 then shows scenario string `0xf` and stores 1 when slot 2 is gone. Indexes 3, 4, and 5 store 1 when slot 3 is gone. Index 8 stores 1 when slot 6 or slot 7 is gone. Index 10 stores 1 when slot 8 is gone. Index 16 stores 1 when slot 3 is gone, which the shared check already did for index `0x10`.

The others do not rely on that walk alone.

- Index 2 stores 1 when slot 0 is gone. Otherwise, when slot 4 is gone, it shows string `0xd` and stores 2.
- Index 7 stores 1 when slot 0 is gone, and again when the turn counter `DAT_00069ce8` is above 3 and slot `0x13` is gone. When slots `0xf`, `0x10`, `0x11`, and `0x12` are all gone, byte `0x640e9` clear stores 1 and shows string `0x1b`, and a set byte shows string `0x23` and stores 2.
- Index 9 counts slots 0 through 7 whose byte `+1` is `0x17` or whose bit 0 is set. Slot 0 gone stores 1. A count of 8 stores 2.
- Index 14 calls the shared check only when byte `0x640e8` is clear. When the byte is set and slot 4 or slot `0x35` is gone, slot 4 gone shows string `0x16`, and the other case shows string `0x17` and, when `FUN_00025210(4)` is not 8, shows string `0x18` and gives id `0xa5` to slot 4. Either case stores 2.
- Index 18 calls the shared check only when byte `0x640e9` is clear. When the byte is set and slot 4 or slot `0x4d` is gone, slot `0x4d` gone shows string `0x11`, removes item `0xa5` from slot 4 when that pair exists, and gives id `0xa6`. The other case shows string `0x12`. Either case stores 2. A separate branch runs when the turn is at most `0x14`, the outcome is already 2, the byte is clear, slot 4 is not gone, and slot 4 carries item `0xa5`. It calls `FUN_00023800` with the scenario index, group 2, and 0, shows strings `0xd` and `0xe`, and reads a confirm. A 0 sets byte `+5` to 1 on slots 0 through `0x4c`, leaving slot 4, and stores outcome 0. Any other confirm shows string `0xf`. The branch then stores 1 into `0x640e9`.
- Index 19, while the turn is at most `0x11`, calls `FUN_000368d0` three times. That function writes its third argument into the low nibble of `+0x34` on each slot from the first argument through the second. The three calls name one slot each, `turn + 0xc`, `turn + 0x1d`, and `turn + 0x2e`, and the nibble is 0. It then calls the shared check.
- Index 21 stores 1 when slot 3 is gone. Index 22 stores 1 when slot 3 is gone, and when slot `0x1f` is gone it shows string `0x14` and stores 1. Index 29 stores 1 when slot 0 is gone. None of these three stores 2.
- Index 23 is the same shape as index 18 with the flag `0x640e9`. Slot `0x52` gone shows string `0x19`, removes item `0xa6` from slot 4, and gives id `0xa7`. The other gone slot shows string `0x1a`. The turn bound is `0x19`, the item is `0xa6`, and `FUN_00023800` is called with group 7. The confirm's 0 path shows string `0x17`, then sets byte `+5` to 1 on every slot below the unit count minus one, leaving slot 4, and stores outcome 0. The other path shows string `0x18`. The same store of 1 into `0x640e9` follows.
- Index 24 stores 2 when slots `0xc`, `0xd`, and `0xe` are all gone, and stores 1 when slot 0 is gone. Index 25 adds slot `0xf` to that set, and stores 1 when byte `0x640e8` is 1 and slot `0x5b` is gone. Index 26 stores 2 when slot `0xc` is gone, and stores 1 when slot 0 is gone.

A death record whose first byte is 4 stores 2, and 5 stores 1, in [Combat](combat.md). That is the other writer of the outcome during a battle. The pointer table at `0x601c4` continues past the first 16 entries up to this after-action table, 50 pointers. Which of those a scenario names is in [Scenario files](scenario.md).

`FUN_0002e7a0` looks for a side-`2` unit that is still eligible (flag bits `0x81` clear, `+0x26` clear). If none remains, it calls `FUN_0001e3c0`, which is the turn change:

1. For each eligible side-`2` unit whose `+0x40` is not its `+0x42`, and whose `+0x25` and `+0x26` are 0, add `+0x42 / 5` to `+0x40`, capped at `+0x42`. If any unit was changed, play `REST.WAV`.
2. `FUN_00012b20` walks side `1`. For each eligible unit it calls `FUN_00010010(unit, 1)`, then the same two callback tables as the player's action. It stops when `DAT_00069da0` becomes nonzero.
3. If the outcome is still 0, `FUN_0001ead0` plays `EnyPhase.saf`, then `FUN_00012960` walks side `0` in two passes. Both passes take a unit whose side is 0, whose flag bits `0x81` are clear, and whose `+0x26` is 0. The first pass calls `FUN_0002dd20` and then `FUN_00013420` and `FUN_00013040`. It calls `FUN_00010010(unit, 0)` only when `DAT_00063f88` or `DAT_00063f8c` is greater than 5. Those two globals are the spell score and the item score in [Combat](combat.md). The second pass calls `FUN_00010010(unit, 0)` with no score test. A unit that already acted has bit `0x80` set by the script tail, so the second pass skips it. Either pass stops when `DAT_00069da0` becomes nonzero. `FUN_0002dd20` allocates `(DAT_00060150 + 1) * 0x50` bytes, copies that many bytes out of the unit array, clears `DAT_00060150 * 0x50` bytes of the old array, frees it, and keeps the new pointer. It also allocates and frees `(FUN_00042a68() % 0x400) + 1` bytes. The count is not written.
4. If the outcome is still 0, increment `DAT_00069ce8`, `FUN_0001ead0` plays `PlyPhase.saf`, and return to the cursor. A few item checks on the way back call `FUN_0001f4e0` when a carried byte has bit `0x40` and the second pool is not full. The same player is also called with `PlyPhase.saf` from `0x24190`.

`FUN_00010010` is one unit's phase. It returns immediately when bit 0 of byte `+5` is set. The low nibble of `+0x34` selects the script. Bytes `+0x35` and `+0x36` are the two tile arguments, and byte `+0x3d` is the index script 5 uses. The second argument is the side filter: `0` hunts a unit whose side is not `0`, and any other value hunts side `0`. The side-`1` walk passes `1`.

A script that returns 0 did not act, and the next call in that row runs. `FUN_00012c10` is the scored action. The target lists, the bands, and the comparison are the routine in [Combat](combat.md). `FUN_000126b0` and `FUN_000127c0` choose a tile and hand it to `FUN_000119e0`, which is the walk below. `FUN_000120d0` rests: if `+0x40` is already `+0x42`, or `+0x25` or `+0x26` is nonzero, it returns 0. Otherwise it centers the camera, plays `REST.WAV`, and adds `+0x42 / 5` to `+0x40`, capped at `+0x42`.

`FUN_000126b0` ranks opponents by terrain cost. It flood-fills from the unit with budget 100 on `FUN_00018b60(class)` and does not stamp units first. `FUN_00011460` in mode 2 then keeps the visible unit (flag bit 0 clear) whose side is not 0 and whose tile has the smallest cost byte. A cost of `0xff` means the fill never wrote that tile, and it is ignored. The lowest unit index wins a tie. The function returns that cost, or −1 when every candidate is `0xff`. A return of −1, or a chosen tile equal to the unit's own tile, is no move. Any other tile is walked. The side test here is fixed: the script's side filter is not passed in.

`FUN_000127c0` ranks by Manhattan distance. `FUN_0003d0d4` is the absolute value. Among visible units the side filter accepts, it keeps the smallest `|dx| + |dy|`, and the lowest index wins a tie. Filter 0 accepts a side other than 0. Any other filter accepts side 0. No opponent, or an opponent already on this tile, is no move. Otherwise it walks to that unit's tile.

Both walks clear `DAT_00069cd0`, call `FUN_0002d7e0` with the slot, call `FUN_000119e0`, and set `DAT_00069cd0` back to 1. `FUN_0002d7e0` reads that slot and calls `FUN_0002d550` with the tile times 24, which is the camera centre used by a portrait in [Text](text.md). The walk returns whether `FUN_000119e0` returned nonzero.

`FUN_000119e0(destX, destY, unit, filter)` stops short of a tile it cannot enter. The move row is `FUN_00018b60(class + 1)` and the budget is byte `+0x3b`. `FUN_00010b90(filter)` stamps the hunted units before each fill, which is the occupancy write in [Map](map.md). The step bytes and the redraw are in [Combat](combat.md).

```
# FUN_000119e0. FUN_00011460 modes 0 and 1 rebuild a path.
# Both start at the destination and step to a cheaper neighbor,
# trying -Y, then +X, then +Y, then -X. Mode 0 requires a strictly
# lower cost. Mode 1 also accepts an equal cost once a neighbor has
# already been chosen this step, and only when the previous path byte
# is a different direction. The bytes are stored backwards and reversed,
# so playback starts at the unit. 0 is +Y, 1 is -X, 2 is -Y, else +X.
# The loop ends when the search tile is the unit's tile.

stamp(filter)                          # FUN_00010b90
fill(move_row, budget = unit.move)     # FUN_00010de0
path = rebuild(dest, mode = 0)         # FUN_00011460
aim = dest
if path is -1:                         # dest not reached within the move
    clear_grid()                       # FUN_00010b20
    fill(move_row, budget = 100)       # no stamp, so unit tiles are open
    path = rebuild(dest, mode = 1)
    if path is not -1:
        clear_grid()
        stamp(filter)
        fill(move_row, budget = unit.move)
        for step in path:              # walked from the unit toward dest
            if cost_byte(step) != 0xff:
                aim = step             # furthest reached tile on that path

clear_grid()
stamp(filter)
fill(move_row, budget = unit.move)
punch_friends(unit, filter)            # FUN_000118f0
candidates = tiles where cost != 0xff  # FUN_00011da0, row-major
stand = aim
best = (0xff, 0xff)
for tile in candidates:
    manh = |tile.x - aim.x| + |tile.y - aim.y|
    diag = ||tile.x - aim.x| - |tile.y - aim.y||
    if manh < best.manh or (manh == best.manh and diag < best.diag):
        stand = tile
        best = (manh, diag)
clear_grid()
stamp(filter)
fill(move_row, budget = unit.move)
path = rebuild(stand, mode = 0)
clear_grid()
if length(path) != 0:
    play(path)                         # FUN_0002d060
return length(path) != 0
```

`FUN_000118f0` writes `0xff` into the cost byte of every other visible unit on the mover's side of the filter. Filter 0 punches side 0. Any other filter punches a side other than 0. The mover's own tile is left alone. A hunted unit's tile was already blocked by the stamp, so the closest candidate to that tile is a neighbor the fill could enter.

| Nibble | What it tries, in order |
| --- | --- |
| 0 | Scored action, then the budget-100 walk, then the nearest unit, then rest. |
| 1 | Scored action, then the budget-100 walk, then rest. |
| 2 | Scored action, then the swing scorer. That scorer returns 0, so this row then rests. |
| 3 | Scored action. Otherwise `FUN_0002d9b0` looks up the unit id in `+0x35`. A miss uses row 0's three fallbacks. A hit walks to that unit's tile, and a failed walk rests. |
| 4 | Walk to the tile in `+0x35`, `+0x36`. A failed walk rests. |
| 5 | Scored action. Otherwise, when byte `DAT_000640d8[+0x3d]` is 0 and `FUN_00013e10(+0x3d)` returns a tile, walk there. That search is the first tile whose `DTL` byte equals `+0x3d` and whose attribute byte 0, masked with `0x60`, equals `0x20`. Landing copies the byte at `DAT_0006013c + index * 3 + 0x53` and the following short into `+0x31` and `+0x32`, calls `FUN_00025cf0` when that byte is 0, sets `DAT_000640d8[index]`, calls `FUN_0002e6a0`, stores `7` in `+0x34`, and plays `Chess.wav`. A flag already set, or no tile, uses row 0's three fallbacks. |
| 6 | Nothing in the script. The tail below still runs. |
| 7 | Walk to `+0x35`, `+0x36`. A failed walk rests. Landing there plays `Posion.saf` through `FUN_00026dd0` when the character id is `0x24` through `0x27`, then stores `1` in byte `+5`. `FUN_00026dd0(count, slots, name)` opens that clip from `MISC.VFS` and, for each frame and then again, draws the map and the frame on each listed unit. The frame sits 24 pixels left of the unit's tile and 30 pixels above it. The first unit of the first pass is the one whose sample is started. |
| 8 | Return. The tail does not run. |
| 9 | Look up the unit id in `+0x35`. A miss is row 0. A hit walks there, and a failed walk is row 0. |
| 10 | Score the carried-item action. Above 5, take it. Then score the swing: below 6, the budget-100 walk, otherwise the swing. |
| 11 | Character ids `0x3c` through `0x3e` call `FUN_00010760` first. That call walks every unit whose character id is `0x55` or `0x6a` and whose flag bit 0 is set. It moves the unit to the nearest tile whose occupancy bit `0x40` is clear and whose terrain byte is below 5. Id `0x55` measures from tile `(5, 12)` and id `0x6a` from `(15, 13)`. It centres the camera, fades the palette, plays `Posion.saf` on that one slot, clears byte `+5`, and copies `+0x42` into `+0x40`. Then the same shape as row 10, with the spell score and `FUN_00013c90` in place of the item. |

`FUN_0002d9b0(id, out)` walks the battle slots. The first visible unit whose byte `+8` equals `id` is written through `out` and its slot is returned. No such unit returns −1. `FUN_000109b0` is the visibility test: it returns bit 0 of the flag byte. After every nibble except 8, `FUN_0002ddc0` is called with the unit's tile and `1`, bit `0x80` is ORed into byte `+5`, and the map is redrawn. `FUN_0002ddc0` loads the tile. When attribute byte 0 masked with `0x60` is 0 and the `DTL` byte is not 0, it reads the pair at `DAT_0006013c + 0x31 + DTL * 2`. If the first byte is not `0xff` and the second byte equals the third argument, that first byte is stored in `DAT_00069d90`. A call that misses leaves the previous index. The four walk steps `FUN_0002d0f0`, `FUN_0002d210`, `FUN_0002d320`, and `FUN_0002d430` pass the cursor tile, divided by 24, and 0. They are the steps `FUN_0002d060` plays, in [Combat](combat.md). The phase tail at `0x1071f` passes the unit's tile and 1. `FUN_00015460` passes the unit's tile and 1 after `FUN_000119b0` when a move is followed by a menu result other than −1, and when `DAT_00060004` is set on a cancelled menu. A menu accepted without a move does not call it. The index is stored as `0xff` at the start of each move attempt, and the move calls the handler with the unit slot when it leaves, if the index is not `0xff`. `FUN_00012b20` and both side-0 passes do the same after `FUN_00010010`. Inside `FUN_00014aa0`, menu result 1, once `FUN_00017980` returns 0, walks each side-2 unit whose flag bits `0x85` and byte `+0x26` are clear to the cursor through `FUN_000119e0`, calls the handler that walk stored, and then calls `FUN_000119b0`. The bodies are in [Scenario files](scenario.md).

`FUN_0002e6a0` walks every tile. Where attribute byte 0 masked with `0x60` is `0x20` or `0x60`, and `DAT_000640d8` at the `DTL` byte is nonzero, it adds 1 to that tile's picture short and stores 0 in the `DTL` byte.

`FUN_0002de50` and `FUN_0001fa00` are called with 1, then 0, then 2 around those walks. `FUN_0002de50` walks the sixteen rows at byte 3 of the map file, in [Scenario files](scenario.md): a row whose first byte is the turn counter and whose third byte is this argument calls the handler indexed by the middle byte, passing 0. `FUN_0001fa00` walks the units whose side byte equals that argument and whose flag bit 0 is clear. Where `+0x25` is nonzero it sets `+0x40` to `max(0, +0x40 - +0x42 / 10)`. It then decrements each nonzero byte from `+0x22` through `+0x27`, and a byte that reaches 0 is followed by `FUN_00024d40` on that unit. `FUN_00030a30(scenario, 0 or 1)` sits at the same points. It stores a track in `DAT_00069d54`. When byte `DAT_00060008` is 0 the track is −1 and it calls `FUN_0003c217`. Otherwise the track is the byte at `0x30230 + scenario * 2 + argument`, and it calls `FUN_0003c5cb` with that byte plus 1. The sixty bytes, two per scenario from 0 through 29, are `13 6`, `13 6`, `13 6`, `13 6`, `4 4`, `4 4`, `9 9`, `14 18`, `13 6`, `6 4`, `9 9`, `14 14`, `13 6`, `13 6`, `13 4`, `13 6`, `13 4`, `9 9`, `6 7`, `5 7`, `5 7`, `5 7`, `6 4`, `6 7`, `6 12`, `1 12`, `13 9`, `4 10`, `4 10`, `13 12`. The turn change passes 1 and then 0. The calls at `0x1849d`, `0x241a0`, and `0x31292` pass 0. A disc check in the same function is not entered.

`FUN_000184e0(slot)` is the search on the fourth command corner. It loads the cursor tile. It returns immediately unless attribute byte 0 masked with `0x60` is neither 0 nor `0x60`, and `DAT_000640d8` at the `DTL` byte is 0. It shows the unit's portrait and interface string `0x20a` when the mask is `0x20`, otherwise string `0x20b`. `FUN_00017980` returning anything other than 0 shows string `0x20c` and leaves the tile alone. A 0 return plays `Chess.wav` and reads the triple at `DAT_0006013c + DTL * 3 + 0x53`. Byte 0 gives the item whose id is the following short: string `0x20d` names it, and `FUN_00025cf0` gives it. A full list shows string `0x20e`. Accepting that drops a chosen pair, writes the dropped id back into the short, and shows string `0x20f`. Refusing shows string `0x210`. A successful give stores 1 in `DAT_000640d8[DTL]` and calls `FUN_0002e6a0`. Byte 1 adds the short to `DAT_000643b8`, the dword the loss window prints in eight digits and the save writes at `0x30cd`. The string is `0x211` when the short is 0 and `0x212` otherwise, then the same flag and `FUN_0002e6a0`. Any other byte calls `(&DAT_000601c4)[short]` with the slot. The keys are below.

Confirm with nobody under the cursor opens `FUN_00014aa0`. Its four corners are the glyphs in [Pictures](pictures.md). Corner 0 calls `FUN_00014e90` and, unless that returns −1, leaves the visit with the returned value. Corner 1 shows string `0x1ea`. Accepting shows `0x1eb`, walks every eligible side-`2` unit to the cursor tile, runs a handler when `DAT_00069d90` changed, commits each unit, and calls the turn change. Refusing shows `0x1ec`. Corner 2 is `FUN_000183c0`, the four toggles below. Corner 3 shows `0x1ed`. Accepting shows `0x1ee` and calls the turn change. Refusing shows `0x1ef`.

`FUN_00014e90` is the second diamond, and it is the save writer in [Save](save.md). Cancelling returns −1. Corner 0 calls the loss window `FUN_00017c90` and returns 0. Corner 1 confirms with string `0x1f3` and, on accept, writes `FDE.SAV` and shows `0x203`. Refusing shows `0x204`. Corner 2 confirms with `0x205`. Accepting shows `0x206` and calls `FUN_00023df0`. Refusing shows `0x207`. Corner 3 confirms with `0x1f0`. Accepting shows `0x1f1`, stores 1 in the quit byte `DAT_000643eb`, and returns 1. Refusing shows `0x1f2`. `FUN_00023df0` reads that file back, in [Save](save.md). When `FDE.SAV` can be opened, the third dword of this diamond's second table is 1. When some unit has flag bit `0x80` set and bit 0 clear, the second dword is 1. The frame those dwords select is in [Pictures](pictures.md).

`FUN_00017980` is the confirm. It keeps the 302×73 rectangle already on VGA `(9, 120)`, rebuilds the map, and paints that rectangle back at buffer `(29, 140)`. The choice starts at 0. Left (`0x4b`) selects 0 and right (`0x4d`) selects 1. Enter or Space returns that choice. Escape (`0x01`) or Delete returns −1. Callers treat 0 as accept. While the choice is 0, `SHADOW.CEL` picture `0x0d` sits at buffer `(275, 123)` and pictures 4 through 7 cycle at `(249, 123)`. While it is 1, picture 8 sits at `(249, 123)` and pictures 9 through 12 cycle at `(275, 123)`. The cycle is `tick / 3` modulo 4.

`FUN_000183c0` is four more corners from `COMMAND.CEL`. A stored 0 shows pictures `0x31`, `0x32`, `0x33`, and `0x3c`. Any other byte shows `0x0d`, `0x0e`, `0x0f`, and `0x18`. Corner 0 flips `DAT_00060008` and calls the phase music with argument 0. Corner 1 flips `DAT_00069d70`, which has to be set before a sample starts, in [Pictures](pictures.md). Corner 2 flips `DAT_00060010`, which chooses the map swing or the fight clips in [Combat](combat.md). Corner 3 flips `DAT_00060158`. When that byte and `DAT_00060159` are both nonzero, `FUN_0002da80` draws `ADWin.cel` picture 0 on the map buffer at `(DAT_0006016c, 160)`. The x becomes `0x124` when the cursor is at least 5 tiles below the camera and at most 1 tile to its right, and `0x19` when it is at least 5 tiles below and more than 10 tiles to the right. The current terrain picture is drawn at `(x + 9, 175)`, with the attack and defense percents of that terrain. A unit under the cursor adds its map frame and the pool at `+0x40` in four digits. `DAT_0006000c` is 3 while that pool is not its maximum. `FUN_0002a280`, `FUN_00030f80`, and `FUN_0003b7f0` also store 0 or 1 into `DAT_00060158`. Those conditions were not read.

`FUN_00025210` counts the eight pairs whose flag bit `0x80` is clear. The village lists below treat 0 as an empty list and 8 as a full one.

`FUN_00033440` picks a roster index. Escape or Delete returns −1. Enter or Space returns `DAT_000601bc`, except when the scenario index is at least `0x17` and that index is 3, in which case Enter does not confirm. Left and right step by one, and up and down step by three, inside the roster count. The window at `DAT_000601b8` shows six records, three across. Each cell draws `SELBAR.CEL` picture 2 on the selection, command pictures `0x2a` and `0x2b`, the roster icon frame, and interface string `byte + 8 + 1`. On a scenario at or above `0x17`, a record whose byte `+8` is 1 is drawn with expander mode 9. The copy is 304×67 from buffer `(5, 3)` onto VGA `(8, 125)`. `FUN_00015bd0` runs after the six cells and was not read.

`FUN_000322e0` plays `ShopWin.Cel` in nine steps through expander mode 4. Argument 1 runs the steps from 8 down to 0, and 0 runs them upward. `FUN_00033d70`, `FUN_00033f80`, and `FUN_00034190` are the three lists those village actions call. Each one picks a roster index, and a count of 0 shows interface string `0x1fb` with `DAT_00064030` set to byte `+8` plus 1, at the shop pen `0xaa3d4`. `FUN_00033d70` then picks a pair. The credit is the price short at item `+0x13`, multiplied by 3 and shifted right by 2. String `0x1fc` names the item. Accepting removes the pair, plays `Incom.wav`, adds the credit to `DAT_000643b8`, and rebuilds the combat words. `FUN_000320e0(0xa8208, 0x140)` draws command pictures `0x34` through `0x36` at VGA `(8, 104)` and that dword in eight digits. `FUN_00033f80` picks a pair, shows string `0x1fd`, and picks a second roster index. A count of 8 shows string `0x1fa`. Any smaller count removes the pair from the first record and gives that id to the second. `FUN_00034190` calls `FUN_00025d70` on the chosen index, which is the equip list in the command menu above.

The five village actions are the same menu shape. Each opens its `CEL`, keeps a `0xfa00` screen, and loops on `FUN_00032150` until the selection is −1. Leaving plays `ShopWin.Cel` closed. The corners, in order:

| Action | File | Prompt, then the corners |
| --- | --- | --- |
| `FUN_00035a30` | `BarShop.cel` | Plays `FUN_000361d0` before the menu. Prompt `0x200`. Scenario string 6. `FUN_000241b0` on the screen, the slot writer in [Save](save.md). `FUN_00024460`, and when that returns 1 it calls `0x312b0`. Interface string `0x1f0`; a confirm of 0 stores the quit byte, shows `0x1f1`, waits `0x3d0e0(0x12c)`, and leaves the menu. |
| `FUN_00035810` | `Church.cel` | Prompt `0x200`. Scenario string 7. `FUN_00034310`, the rank change in [Units](units.md). The give list. `FUN_00033cf0`. |
| `FUN_000355d0` | `Item.cel` | Prompt `0x1f4`. Scenario string 4. `FUN_000338f0` with group 0. The sale list. The give list. `FUN_00033cf0`. |
| `FUN_00035d40` | `Weapon.cel` | Prompt `0x1fe`. Scenario string 5. `FUN_000338f0` with group 1. The sale list. The give list. The equip list. |
| `FUN_00035f80` | `Secret.cel` | Prompt `0x202`. Scenario string 8. `FUN_000338f0` with group 2. The sale list. The give list. The equip list. `FUN_00033cf0`. |

The prompt and the string shown again after a corner are interface strings, at the shop pen `0xaa3d4`. `FUN_00033cf0` picks a roster index and calls `FUN_00016a90`, the status window. `0x312b0` frees the scenario text and opens the files for the current scenario index. The rest of that body was not read. The frames inside `FUN_000361d0` were not walked.

`FUN_00024e70(slot, row, dest, pitch)` draws the eight pairs. A row from 0 through 7 gets `SELBAR.CEL` picture 0 at y `row * 17 + 8`. A pair whose flag bit `0x80` is set is skipped. The name is interface string `id + 0xc9`. The mark comes from `COMMAND.CEL` through `FUN_00015b80`, 25×22. Item byte 0 from 1 through `0x15` uses picture `0x1d`, from `0x16` through `0x27` uses `0x1e`, and any other byte uses `0x1f`. Flag bit `0x40` adds 4. A second picture and a four-digit number sit further along the row. Types 1 through `0x15` use picture `0x40` and the short at item `+1`. Types below `0x28` otherwise use picture `0x41` and the short at `+5`. A type at or above `0x28` uses picture `0x3e` when byte `+0x0d` is `0x0b`, picture `0x3f` when it is `0x0c`, and in both of those the short at `+0x0e`. Any other byte `+0x0d` uses picture `0x43` and no number. The status window and the battle item picker call this too.
