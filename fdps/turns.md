# Selection, turns, and outcomes

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`object 1 + 0x1b870` is the body of one visit to the map. It polls a byte from `object 1 + 0x46509`. A new key is handled immediately. Repeats 1 through 5 skip movement; after that the key repeats. The visit returns only when the outcome dword is nonzero or the system menu returns nonzero. That exit, and what the session does with the outcome, is in [Session](session.md). The effects below are what the comparisons do. The names in parentheses are the BIOS scan codes for those bytes.

| Byte | What it does |
| --- | --- |
| `0x48`, `0x50`, `0x4b`, `0x4d` (arrows) | Move the cursor one tile, inside the map, and play `Beep.wav`. |
| `0x01`, `0x2c`, `0x4c`, `0x53` | Center on the next side-`2` unit whose flag byte has bits `0x85` clear. |
| `0x39`, `0x1c` (space, enter) | `object 1 + 0x1d830` picks the unit under the cursor. None opens `object 1 + 0x4aa0`. A side-`2` unit with bit `0x80` clear and `+0x26` clear goes to `object 1 + 0x5460`, then `object 1 + 0x1e7a0` if the outcome dword is still 0. Anything else goes to `object 1 + 0x6a90`. |
| `0x3b` | `object 1 + 0x1def0`, the scaled map below. |
| `0x3c`, `0x47` | `object 1 + 0x6a90` on the unit under the cursor. |

`object 1 + 0x1def0` is the scaled map on key `0x3b`. It reads section 0's width and height from the shorts at MPL `+7` and `+9`. A height above `0x28` uses a scale of 3 and a stride of `0x380`. Any other height uses 4 and `0x280`. On indexes 0 through 29 the tallest section 0 is 39 tiles, so the scale is 4. The marks are centred at VGA `(0xa0, 0x64)`.

`object 1 + 0x1e3d0` builds the cells from section 0's CEL, the pointer at `object 2 + 0x9c20`. The picture count is the short at CEL `+0xb`. It allocates `count * 0x240 + 6` and stores 24, 24, and that count in the first three words. `object 1 + 0x1d930` expands picture `n` at pitch 24 with x 6 and y `n * 24`, so the pixels of slot `n` are the `0x240` bytes at offset 6. `object 1 + 0x1def0` then fills a table of 64 pointers per row. Column `x` of row `y` points at the slot of the picture short `object 1 + 0x1b790` stored for that tile. The widest of these thirty sections is 33 tiles, so the row holds it.

`object 1 + 0x1e4a0(screen, x, y, step, table)` clears the screen and samples a 312 by 192 window at `screen + 0x504`, pitch 320. A tile outside the section leaves the cleared 0, and a source byte of 0 is written. Frame 7 is 4 dest pixels per tile. The point it aims at moves from the camera window toward the middle of the section.

```
# object 1 + 0x1e4a0. one tile is 0xc00. one source pixel is 0x80.
# frame n is 1 through 7. division is toward zero.
step = stride * n / 7 + 0x80
src = (x - step * 0x9c, y - step * 0x60)
# each dest pixel adds step. the sample is pixel (frac / 0x80) inside that tile.

viewX = cameraTileX * 0xc00 + 13 * 0x600
viewY = cameraTileY * 0xc00 + 8 * 0x600
midX  = width * 0x600
midY  = height * 0x600
x = viewX + (midX - viewX) * (n + 1) / 8
y = viewY + (midY - viewY) * (n + 1) / 8
```

The camera tile is the pixel origin divided by 24. The close walks `n` from 6 down through 1 with the same formula. Each frame copies 64000 bytes to `0xa0000`.

While the key byte from `object 1 + 0x4652e` is above `0x7f`, a tick of `object 2 + 0x9d64` that has moved by 2 or more draws one mark per visible unit and one for the cursor. The mark is `scale − 1` pixels on a side, filled by `object 1 + 0x32a40`. A unit's colour is the dword at `object 1 + 0x1b024` for its side, `0x28`, `0xb4`, or `0xd6`, plus an index that bounces from 0 through 7. The cursor uses `0x82` plus that index. The position is `0xa0 + tileX * scale − width * scale / 2` and `0x64 + tileY * scale − height * scale / 2`. The cursor tile is its pixel divided by 24.

The camera follows the cursor, keeping it away from the edges by a margin of about two tiles (`0x18` on the near side, `0x108` horizontally and `0x90` vertically on the far side).

`object 1 + 0x5460` is the move. It flood-fills from the unit with budget `+0x3b`, then asks for a destination. Cancelling recenters and leaves the loop. A destination whose path result is 0 opens a menu (`object 1 + 0x5cf0`) without changing the tile. Any other accepted destination writes the new tile into bytes `+0` and `+1` unless `object 2 + 0x4` is set, in which case the unit stays and the action is committed through `object 1 + 0x19b0`. After the loop, if `object 2 + 0x9d90` is not `0xff`, it calls `(&`object 2 + 0x1c4`)[`object 2 + 0x9d90`](unit)`. It always then calls `(&`object 2 + 0x28c`)[scenario]()`. The flood fill and the terrain costs are in [Map](map.md).

`object 1 + 0x5cf0` keeps four disable flags. Slot 0 is disabled when `object 1 + 0x15110(unit, 0)` finds no weapon or `object 1 + 0x1e50` lists nobody. Slot 1 is disabled when `object 1 + 0x17810` returns 0 or byte `+0x27` is nonzero. Slot 2 is disabled when `object 1 + 0x15210` returns 0. The first flag that is still 0 is the initial selection. Choosing slot 0 runs the attack in [Combat](combat.md) and then `object 1 + 0x19b0`, which ORs bit `0x80` into byte `+5`. Slot 1 is `object 1 + 0x17bf0`. Slot 2 is `object 1 + 0x15280`. Any other slot calls `object 1 + 0x20d0` when the menu was opened without a move, then `object 1 + 0x84e0` and `object 1 + 0x19b0`. `object 1 + 0x20d0` is the rest below. `object 1 + 0x84e0` is the search of the cursor tile, also below.

`object 1 + 0x61f0` reads that menu, and the item menu below. It loops while its result is 0. `object 1 + 0x4652e` is the key. `0x01` or `0x53` returns −1. `0x39` or `0x1c` returns 1. `0x48` selects corner 0 when the first flag is 0, `0x4b` selects corner 1 when the second flag is 0, `0x4d` selects corner 2 when the third flag is 0, and `0x50` selects corner 3 when the fourth flag is 0. A set flag blocks that corner. Every pass calls `object 1 + 0x1e840`, `object 1 + 0x5bd0`, and `object 1 + 0x5850` with step `0x18` and the current corner. The two calls are the palette pulse and the palette cycle in [Pictures](pictures.md). `object 1 + 0x61a0` closes the menu. It calls `object 1 + 0x1a1c0` with `OpWin.wav`, then `object 1 + 0x5850` with steps `0x17`, `0x13`, `0x0f`, `0x0b`, `0x07`, and `0x03`.

`object 1 + 0x17bf0` stays in a spell list until one cast is confirmed. `object 1 + 0x18100` reads up and down. A window of eight rows follows the selection. Enter or Space returns 1 when byte `+5` of the spell row is at or below `+0x44`, and stays on the list when it is not. Escape or Delete returns −1, which leaves the command menu. The id comes from `object 1 + 0x17810`. Byte `+3` of the spell row decides the aim. The mask it paints, and the line taken when that byte is 16 or more, are in [Combat](combat.md). Zero lists targets from the cursor tile at range byte `+4`, with the side filter fixed at 0, and the cursor picker runs in mode 4, or mode 5 when that list is empty. Nonzero first lists at range byte `+3` with the side byte at `+6`. At 15 or below it then lists again at byte `+4`. At 16 or above the second list is the line from the caster toward the cursor, and `Chess.wav` plays. Id `0x15` refuses a list whose first id is the caster, and a confirmed aim stores the cursor tile at `object 2 + 0x437c` and `object 2 + 0x4380` before a second confirm. A confirmed cast always calls `object 1 + 0xa4a0`, then the death spin and the death-record walk. `object 1 + 0xdd00` applies the term. Division is toward zero.

```
# the term passed to object 1 + 0xdd00
scale = unit[+0x21]
if unit[+8] > 8:
    scale = scale + 0x1e
term = term / scale
```

`object 1 + 0x15280` draws a second menu through `object 1 + 0x6120` and reads it with `object 1 + 0x61f0`. Cancelling returns. An empty carried list returns before the menu. Row 0 picks a carried index with `object 1 + 0x15990`, reads the id at `+0x0b + index * 2`, and calls `object 1 + 0x16270`. The leash during the aim is record byte `+0x12` plus 2. The first paint is byte `+0x10` from the cursor, with inner 1 when byte `+0x0d` is `0x1c` and inner 0 otherwise, and the side is byte `+0x15`. After that picker, byte `+0x10` below `0x10` lists targets with `object 1 + 0x1e50` at the cursor, shape byte `+0x12`, inner 0, and side byte `+0x15`. At or above `0x10` the list is the line in [Combat](combat.md), from the cursor when the item row was chosen toward the cursor after the aim, length `byte +0x10 - 0x10`, side argument 1. Record byte `+0x0d` of `0x1c` or `0x19` asks for one more confirm and stores the cursor tile the same way id `0x15` does. A confirmed use then calls `object 1 + 0x19b0` and returns 1. Row 1 picks an item and a unit on the cursor tile, then `object 1 + 0x1d550` slides the cursor back to where the menu opened. `object 1 + 0x15cf0` returning −1 swaps one item each way through `object 1 + 0x15c90`. Any other return removes the giver's item. Both paths call `object 1 + 0x14d40` and return 2. Row 2 is `object 1 + 0x15d70`. It lists the pairs. `object 1 + 0x15fb0` returns 1 when one of six bytes from `object 1 + 0x8b90(class)` equals the item record's first byte. A row that passes calls `object 1 + 0x16040`, plays `Equip.wav`, and rebuilds the combat words. `object 1 + 0x16040` clears bit `0x40` on other pairs in the same group, then stores `0x40` in the chosen pair's flag. The group is the record's first byte: below `0x16` is one group, and `0x16` or above is the other. A first byte of 0 does not clear another pair. Any other menu row removes the picked item with `object 1 + 0x15c90` and calls `object 1 + 0x14d40`.

`object 1 + 0x15990` plays `OpWin1.wav` and returns what `object 1 + 0x15af0` chooses. That picker counts pairs whose flag bit `0x80` is clear and moves an index inside that count. Up and down wrap, and each plays `Beep.wav`. Enter or Space returns 1. Escape or Delete returns −1. The use row passes 1 as the second argument, and then Enter is refused while byte `+0x0d` of the record is 0. The other calls in `object 1 + 0x15280` pass 0, so Enter accepts the row. Give and remove keep the empty pairs at the end, so this index is the pair index.

`object 2 + 0x28c` is a table of code pointers indexed by the scenario, parallel to the ending table at `object 2 + 0x304` and the opener table at `object 2 + 0x74`, but not the same pointers. The first is `object 1 + 0x2a120` and the last, index 29, is `object 1 + 0x2b7c0`. These bodies were not created as functions. The disassembly below is not a decompile. `object 1 + 0x9b0(slot)` returns bit 0 of that unit's byte `+5`. The session loop treats outcome `1` as `GameOver.saf` and outcome `2` as the per-scenario ending.

`object 1 + 0x2a050` is the check most of the bodies call. `object 1 + 0x9b0(slot)` is bit 0 of that unit's byte `+5`. A set bit means the unit is gone.

```
# object 1 + 0x2a050
if object 2 + 0x9da0 != 0:
    return
object 2 + 0x9da0 = 2
for each slot:
    if slot.side == 0 and object 1 + 0x9b0(slot) == 0:
        object 2 + 0x9da0 = 0
if scenario in (0x10, 0x15):
    if object 1 + 0x9b0(3) != 0: object 2 + 0x9da0 = 1
else if object 1 + 0x9b0(0) != 0:
    object 2 + 0x9da0 = 1
```

Indexes 1, 6, 11, 12, 13, 15, 17, 20, 27, and 28 call that and return. Index 0 then shows scenario string `0xf` and stores 1 when slot 2 is gone. Indexes 3, 4, and 5 store 1 when slot 3 is gone. Index 8 stores 1 when slot 6 or slot 7 is gone. Index 10 stores 1 when slot 8 is gone. Index 16 stores 1 when slot 3 is gone, which the shared check already did for index `0x10`.

The others do not rely on that walk alone.

- Index 2 stores 1 when slot 0 is gone. Otherwise, when slot 4 is gone, it shows string `0xd` and stores 2.
- Index 7 stores 1 when slot 0 is gone, and again when the turn counter `object 2 + 0x9ce8` is above 3 and slot `0x13` is gone. When slots `0xf`, `0x10`, `0x11`, and `0x12` are all gone, byte `object 2 + 0x40e9` clear stores 1 and shows string `0x1b`, and a set byte shows string `0x23` and stores 2.
- Index 9 counts slots 0 through 7 whose byte `+1` is `0x17` or whose bit 0 is set. Slot 0 gone stores 1. A count of 8 stores 2.
- Index 14 calls the shared check only when byte `object 2 + 0x40e8` is clear. When the byte is set and slot 4 or slot `0x35` is gone, slot 4 gone shows string `0x16`, and the other case shows string `0x17` and, when `object 1 + 0x15210(4)` is not 8, shows string `0x18` and gives id `0xa5` to slot 4. Either case stores 2.
- Index 18 calls the shared check only when byte `object 2 + 0x40e9` is clear. When the byte is set and slot 4 or slot `0x4d` is gone, slot `0x4d` gone shows string `0x11`, removes item `0xa5` from slot 4 when that pair exists, and gives id `0xa6`. The other case shows string `0x12`. Either case stores 2. A separate branch runs when the turn is at most `0x14`, the outcome is already 2, the byte is clear, slot 4 is not gone, and slot 4 carries item `0xa5`. It calls `object 1 + 0x13800` with the scenario index, group 2, and 0, shows strings `0xd` and `0xe`, and reads a confirm. A 0 sets byte `+5` to 1 on slots 0 through `0x4c`, leaving slot 4, and stores outcome 0. Any other confirm shows string `0xf`. The branch then stores 1 into `object 2 + 0x40e9`.
- Index 19, while the turn is at most `0x11`, calls `object 1 + 0x268d0` three times. That function writes its third argument into the low nibble of `+0x34` on each slot from the first argument through the second. The three calls name one slot each, `turn + 0xc`, `turn + 0x1d`, and `turn + 0x2e`, and the nibble is 0. It then calls the shared check.
- Index 21 stores 1 when slot 3 is gone. Index 22 stores 1 when slot 3 is gone, and when slot `0x1f` is gone it shows string `0x14` and stores 1. Index 29 stores 1 when slot 0 is gone. None of these three stores 2.
- Index 23 is the same shape as index 18 with the flag `object 2 + 0x40e9`. Slot `0x52` gone shows string `0x19`, removes item `0xa6` from slot 4, and gives id `0xa7`. The other gone slot shows string `0x1a`. The turn bound is `0x19`, the item is `0xa6`, and `object 1 + 0x13800` is called with group 7. The confirm's 0 path shows string `0x17`, then sets byte `+5` to 1 on every slot below the unit count minus one, leaving slot 4, and stores outcome 0. The other path shows string `0x18`. The same store of 1 into `object 2 + 0x40e9` follows.
- Index 24 stores 2 when slots `0xc`, `0xd`, and `0xe` are all gone, and stores 1 when slot 0 is gone. Index 25 adds slot `0xf` to that set, and stores 1 when byte `object 2 + 0x40e8` is 1 and slot `0x5b` is gone. Index 26 stores 2 when slot `0xc` is gone, and stores 1 when slot 0 is gone.

A death record whose first byte is 4 stores 2, and 5 stores 1, in [Combat](combat.md). That is the other writer of the outcome during a battle. The pointer table at `object 2 + 0x1c4` continues past the first 16 entries up to this after-action table, 50 pointers. Which of those a scenario names is in [Scenario files](scenario.md).

`object 1 + 0x1e7a0` looks for a side-`2` unit that is still eligible (flag bits `0x81` clear, `+0x26` clear). If none remains, it calls `object 1 + 0xe3c0`, which is the turn change:

1. Heal each eligible side-2 unit, and play `REST.WAV` if any pool changed. Division is toward zero.

```
# eligible: flag bits 0x81 clear, +0x26 clear, side 2
if unit[+0x40] != unit[+0x42] and unit[+0x25] == 0 and unit[+0x26] == 0:
    unit[+0x40] = min(unit[+0x42], unit[+0x40] + unit[+0x42] / 5)
```
2. `object 1 + 0x2b20` walks side `1`. For each eligible unit it calls `object 1 + 0x10(unit, 1)`, then the same two callback tables as the player's action. It stops when `object 2 + 0x9da0` becomes nonzero.
3. If the outcome is still 0, `object 1 + 0xead0` plays `EnyPhase.saf`, then `object 1 + 0x2960` walks side `0` in two passes. Both passes take a unit whose side is 0, whose flag bits `0x81` are clear, and whose `+0x26` is 0. The first pass calls `object 1 + 0x1dd20` and then `object 1 + 0x3420` and `object 1 + 0x3040`. It calls `object 1 + 0x10(unit, 0)` only when `object 2 + 0x3f88` or `object 2 + 0x3f8c` is greater than 5. Those two globals are the spell score and the item score in [Combat](combat.md). The second pass calls `object 1 + 0x10(unit, 0)` with no score test. A unit that already acted has bit `0x80` set by the script tail, so the second pass skips it. Either pass stops when `object 2 + 0x9da0` becomes nonzero. `object 1 + 0x1dd20` allocates `(`object 2 + 0x150 + 1) * 0x50` bytes, copies that many bytes out of the unit array, clears `object 2 + 0x150` * 0x50` bytes of the old array, frees it, and keeps the new pointer. It also allocates and frees `(`object 1 + 0x32a68`() % 0x400) + 1` bytes. The count is not written.
4. If the outcome is still 0, increment `object 2 + 0x9ce8` at `object 1 + 0xe5cd`, then call `object 1 + 0xead0` with the `PlyPhase.saf` string at `object 2 + 0x17a0`. Inside that player, `object 1 + 0x32d50` compares the name with `object 2 + 0x17c0` (`PLYPHASE.SAF`). A zero return calls `object 1 + 0xe810` before `object 1 + 0xecc0` plays the clip. `EnyPhase.saf` does not match, so the card does not run before the enemy clip. The same player is also called with `PlyPhase.saf` from `object 1 + 0x14190`, and that call takes the same compare. On the way back, `object 1 + 0x1d8e0` clears bit `0x80` of byte `+5` on every slot. `object 1 + 0x20a30` is then called with the scenario and 0, `object 1 + 0x1de50` with 2, and `object 1 + 0xfa00` with 2. Three item checks follow, each at `object 1 + 0xe614`. A hit centres the camera with `object 1 + 0x1d7e0` and draws the added amount with `object 1 + 0xf4e0`.

```
# object 1 + 0x24290 returns the pair index, or -1.
# object 1 + 0x17570 adds the points.
def grant(slot, id, need_flag):
    if object 1 + 0x24290(slot, id) < 0: return 0
    if unit[+5] != 0 or unit[+0x44] == unit[+0x46]: return 0
    if need_flag and the pair's flag bit 0x40 is clear: return 0
    unit[+0x44] = min(unit[+0x46], unit[+0x44] + 0xf)
    return 1

if grant(4, 0xa6, 1) == 0:
    grant(4, 0xa7, 1)
grant(8, 0xb1, 1)
for each slot:
    grant(slot, 0xb3, 0)
```

`object 1 + 0x9b0(0)` then centres slot 0 when that unit's bit 0 is clear, and byte `object 2 + 0x159` is stored as 1.

`object 1 + 0xe810` is the turn card. Disassembly, not a decompile. It copies thirteen signed dwords from `object 1 + 0xc250`: −60, −20, 10, 35, 50, 65, 75, 80, 85, 90, 92, 91, 90. It opens `Turn.saf` through `object 1 + 0x1a210` on the string at `object 2 + 0x17b0`. That opener reads the archive at `object 2 + 0x43bc`, which is `BaseAni.vfs`. The member is the eleven-frame clip in the effect extract. Frame 0 is the banner. `object 1 + 0xea50` formats `object 2 + 0x9ce8` with the `%d` at `object 2 + 0x17bc` and draws each byte as frame `byte - 0x2f`, so `'0'` is frame 1 and `'9'` is frame 10. There is no sign and no padding. The counter has already been incremented.

The draw uses the map compose buffer, pitch `0x168`. Each step copies the caller's saved screen, at argument `+0x504`, into the buffer at `+0x21d8`, draws, and copies that 312×192 window back to VGA `0xa0504`. A buffer point `(x, y)` is screen `(x - 20, y - 20)`, as in [Pictures](pictures.md). The banner's buffer x is `step + 0x14` and the first digit's buffer x is `0x12c - step`. Both use buffer y `0x5c`, which is screen y 72. On the screen the banner is at `(step - 6, 72)` and the first digit is at `(280 - step, 72)`. Each further digit adds `0x1c` to the buffer x. The banner blit passes 1 to `object 1 + 0x4140` and the digit blit passes 0. Every frame of this clip stores sample index −1, so neither starts a sample.

The inbound pass is all thirteen steps, index 0 through 12, one change of `object 2 + 0x9d64` each. `object 1 + 0x2d0e0(0x1f4)` then waits. That is `object 1 + 0x33a20`. `object 1 + 0x339f2` counts INT 21h function `0x2c` calls across one change of the seconds byte and stores the count at `object 2 + 0x9ea8`. The wait runs `(argument * count + 0x1f4) / 0x3e8` of those calls. Argument `0x1f4` is `(count + 1) / 2`, half of that calibrated second. The outbound pass then takes indexes 10, 9, …, 0 of the same table, one tick each, and frees the buffer. The outbound does not repeat indexes 11 and 12.

`object 1 + 0x10` is one unit's phase. It returns immediately when bit 0 of byte `+5` is set. The low nibble of `+0x34` selects the script. Bytes `+0x35` and `+0x36` are the two tile arguments, and byte `+0x3d` is the index script 5 uses. The second argument is the side filter: `0` hunts a unit whose side is not `0`, and any other value hunts side `0`. The side-`1` walk passes `1`.

A script that returns 0 did not act, and the next call in that row runs. `object 1 + 0x2c10` is the scored action. The target lists, the bands, and the comparison are the routine in [Combat](combat.md). `object 1 + 0x26b0` and `object 1 + 0x27c0` choose a tile and hand it to `object 1 + 0x19e0`, which is the walk below. `object 1 + 0x20d0` rests. Division is toward zero.

```
# object 1 + 0x20d0
if unit[+0x40] == unit[+0x42] or unit[+0x25] != 0 or unit[+0x26] != 0:
    return 0
# center the camera, play REST.WAV
unit[+0x40] = min(unit[+0x42], unit[+0x40] + unit[+0x42] / 5)
```

`object 1 + 0x26b0` ranks opponents by terrain cost. It flood-fills from the unit with budget 100 on `object 1 + 0x8b60(class)` and does not stamp units first. `object 1 + 0x1460` in mode 2 then keeps the visible unit (flag bit 0 clear) whose side is not 0 and whose tile has the smallest cost byte. A cost of `0xff` means the fill never wrote that tile, and it is ignored. The lowest unit index wins a tie. The function returns that cost, or −1 when every candidate is `0xff`. A return of −1, or a chosen tile equal to the unit's own tile, is no move. Any other tile is walked. The side test here is fixed: the script's side filter is not passed in.

`object 1 + 0x27c0` ranks by Manhattan distance. `object 1 + 0x2d0d4` is the absolute value. Among visible units the side filter accepts, it keeps the smallest `|dx| + |dy|`, and the lowest index wins a tie. Filter 0 accepts a side other than 0. Any other filter accepts side 0. No opponent, or an opponent already on this tile, is no move. Otherwise it walks to that unit's tile.

Both walks clear `object 2 + 0x9cd0`, call `object 1 + 0x1d7e0` with the slot, call `object 1 + 0x19e0`, and set `object 2 + 0x9cd0` back to 1. `object 1 + 0x1d7e0` reads that slot and calls `object 1 + 0x1d550` with the tile times 24, which is the camera centre used by a portrait in [Text](text.md). The walk returns whether `object 1 + 0x19e0` returned nonzero.

`object 1 + 0x19e0(destX, destY, unit, filter)` stops short of a tile it cannot enter. The move row is `object 1 + 0x8b60(class + 1)` and the budget is byte `+0x3b`. `object 1 + 0xb90(filter)` stamps the hunted units before each fill, which is the occupancy write in [Map](map.md). The step bytes and the redraw are in [Combat](combat.md).

```
# object 1 + 0x19e0. object 1 + 0x1460 modes 0 and 1 rebuild a path.
# Both start at the destination and step to a cheaper neighbor,
# trying -Y, then +X, then +Y, then -X. Mode 0 requires a strictly
# lower cost. Mode 1 also accepts an equal cost once a neighbor has
# already been chosen this step, and only when the previous path byte
# is a different direction. The bytes are stored backwards and reversed,
# so playback starts at the unit. 0 is +Y, 1 is -X, 2 is -Y, else +X.
# The loop ends when the search tile is the unit's tile.

stamp(filter)                          # object 1 + 0xb90
fill(move_row, budget = unit.move)     # object 1 + 0xde0
path = rebuild(dest, mode = 0)         # object 1 + 0x1460
aim = dest
if path is -1:                         # dest not reached within the move
    clear_grid()                       # object 1 + 0xb20
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
punch_friends(unit, filter)            # object 1 + 0x18f0
candidates = tiles where cost != 0xff  # object 1 + 0x1da0, row-major
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
    play(path)                         # object 1 + 0x1d060
return length(path) != 0
```

`object 1 + 0x18f0` writes `0xff` into the cost byte of every other visible unit on the mover's side of the filter. Filter 0 punches side 0. Any other filter punches a side other than 0. The mover's own tile is left alone. A hunted unit's tile was already blocked by the stamp, so the closest candidate to that tile is a neighbor the fill could enter.

| Nibble | What it tries, in order |
| --- | --- |
| 0 | Scored action, then the budget-100 walk, then the nearest unit, then rest. |
| 1 | Scored action, then the budget-100 walk, then rest. |
| 2 | Scored action, then the swing scorer. That scorer returns 0, so this row then rests. |
| 3 | Scored action. Otherwise `object 1 + 0x1d9b0` looks up the unit id in `+0x35`. A miss uses row 0's three fallbacks. A hit walks to that unit's tile, and a failed walk rests. |
| 4 | Walk to the tile in `+0x35`, `+0x36`. A failed walk rests. |
| 5 | Scored action. Otherwise, when byte `object 2 + 0x40d8[+0x3d]` is 0 and `object 1 + 0x3e10(+0x3d)` returns a tile, walk there. That search is the first tile whose `DTL` byte equals `+0x3d` and whose attribute byte 0, masked with `0x60`, equals `0x20`. Landing copies the byte at `object 2 + 0x13c + index * 3 + 0x53` and the following short into `+0x31` and `+0x32`, calls `object 1 + 0x15cf0` when that byte is 0, sets `object 2 + 0x40d8[index]`, calls `object 1 + 0x1e6a0`, stores `7` in `+0x34`, and plays `Chess.wav`. A flag already set, or no tile, uses row 0's three fallbacks. |
| 6 | Nothing in the script. The tail below still runs. |
| 7 | Walk to `+0x35`, `+0x36`. A failed walk rests. Landing there plays `Posion.saf` through `object 1 + 0x16dd0` when the character id is `0x24` through `0x27`, then stores `1` in byte `+5`. `object 1 + 0x16dd0(count, slots, name)` opens that clip from `MISC.VFS` and, for each frame and then again, draws the map and the frame on each listed unit. The frame sits 24 pixels left of the unit's tile and 30 pixels above it. The first unit of the first pass is the one whose sample is started. |
| 8 | Return. The tail does not run. |
| 9 | Look up the unit id in `+0x35`. A miss is row 0. A hit walks there, and a failed walk is row 0. |
| 10 | Score the carried-item action. Above 5, take it. Then score the swing: below 6, the budget-100 walk, otherwise the swing. |
| 11 | Character ids `0x3c` through `0x3e` call `object 1 + 0x760` first. That call walks every unit whose character id is `0x55` or `0x6a` and whose flag bit 0 is set. It moves the unit to the nearest tile whose occupancy bit `0x40` is clear and whose terrain byte is below 5. Id `0x55` measures from tile `(5, 12)` and id `0x6a` from `(15, 13)`. It centres the camera, fades the palette, plays `Posion.saf` on that one slot, clears byte `+5`, and copies `+0x42` into `+0x40`. Then the same shape as row 10, with the spell score and `object 1 + 0x3c90` in place of the item. |

`object 1 + 0x1d9b0(id, out)` walks the battle slots. The first visible unit whose byte `+8` equals `id` is written through `out` and its slot is returned. No such unit returns −1. `object 1 + 0x9b0` is the visibility test: it returns bit 0 of the flag byte. After every nibble except 8, `object 1 + 0x1ddc0` is called with the unit's tile and `1`, bit `0x80` is ORed into byte `+5`, and the map is redrawn. `object 1 + 0x1ddc0` loads the tile. When attribute byte 0 masked with `0x60` is 0 and the `DTL` byte is not 0, it reads the pair at `object 2 + 0x13c + 0x31 + DTL * 2`. If the first byte is not `0xff` and the second byte equals the third argument, that first byte is stored in `object 2 + 0x9d90`. A call that misses leaves the previous index. The four walk steps `object 1 + 0x1d0f0`, `object 1 + 0x1d210`, `object 1 + 0x1d320`, and `object 1 + 0x1d430` pass the cursor tile, divided by 24, and 0. They are the steps `object 1 + 0x1d060` plays, in [Combat](combat.md). The phase tail at `object 1 + 0x71f` passes the unit's tile and 1. `object 1 + 0x5460` passes the unit's tile and 1 after `object 1 + 0x19b0` when a move is followed by a menu result other than −1, and when `object 2 + 0x4` is set on a cancelled menu. A menu accepted without a move does not call it. The index is stored as `0xff` at the start of each move attempt, and the move calls the handler with the unit slot when it leaves, if the index is not `0xff`. `object 1 + 0x2b20` and both side-0 passes do the same after `object 1 + 0x10`. Inside `object 1 + 0x4aa0`, menu result 1, once `object 1 + 0x7980` returns 0, walks each side-2 unit whose flag bits `0x85` and byte `+0x26` are clear to the cursor through `object 1 + 0x19e0`, calls the handler that walk stored, and then calls `object 1 + 0x19b0`. The bodies are in [Scenario files](scenario.md).

`object 1 + 0x1e6a0` walks every tile. Where attribute byte 0 masked with `0x60` is `0x20` or `0x60`, and `object 2 + 0x40d8` at the `DTL` byte is nonzero, it adds 1 to that tile's picture short and stores 0 in the `DTL` byte.

`object 1 + 0x1de50` and `object 1 + 0xfa00` are called with 1, then 0, then 2 around those walks. The call with 1 is before the side-1 walk, the call with 0 is before the side-0 walk, and the call with 2 is after the player clip and before the cursor returns. `object 1 + 0x1de50` walks the sixteen rows at byte 3 of the map file, in [Scenario files](scenario.md): a row whose first byte is the turn counter and whose third byte is this argument calls the handler indexed by the middle byte, passing 0. `object 1 + 0xfa00` walks the units whose side byte equals that argument and whose flag bit 0 is clear. The poison and the countdown are in [Units](units.md). `object 1 + 0x20a30(scenario, 0 or 1)` sits at the same points. It stores a track in `object 2 + 0x9d54`. When byte `object 2 + 0x8` is 0 the track is −1 and it calls `object 1 + 0x2c217`. Otherwise the track is the byte at `object 1 + 0x20230 + scenario * 2 + argument`, and it calls `object 1 + 0x2c5cb` with that byte plus 1. Index 0 is the first pair of the sixty bytes below: argument 0 is 13 and argument 1 is 6, so the drive is asked for 14 and for 7. In `object 1 + 0xe3c0` the request with 1 sits just before the side-0 action walk, and the request with 0 sits just after `PlyPhase.saf`. The enemies therefore start track 7, and the cursor returns on track 14. The music toggle also requests argument 0, which restarts that second cue. The recordings stay absent. The request, and the missing sequences, are in [File formats](formats.md). `object 1 + 0x209c0` runs from the palette pulse in [Pictures](pictures.md). When `object 2 + 0x9d74` differs from the tick `object 2 + 0x9d64`, it stores the tick and increments `object 2 + 0x170`. At `0x4b` it stores 0. If the track is not −1 and byte `object 2 + 0x8` is nonzero, it calls `object 1 + 0x2c458`, and a nonzero return calls `object 1 + 0x2c5cb` with the track plus 1. That call returns 1 when bit 9 of the driver status word is clear, so a track that has finished is started again, in [File formats](formats.md). The sixty bytes, two per scenario from 0 through 29, are `13 6`, `13 6`, `13 6`, `13 6`, `4 4`, `4 4`, `9 9`, `14 18`, `13 6`, `6 4`, `9 9`, `14 14`, `13 6`, `13 6`, `13 4`, `13 6`, `13 4`, `9 9`, `6 7`, `5 7`, `5 7`, `5 7`, `6 4`, `6 7`, `6 12`, `1 12`, `13 9`, `4 10`, `4 10`, `13 12`. The turn change passes 1 and then 0. The calls at `object 1 + 0x849d`, `object 1 + 0x141a0`, and `object 1 + 0x21292` pass 0. The disc check above that play is not entered: the flag is stored as 1 before the loop, and the loop runs only while the flag is 0. The body opens `{prefix}\Pack.vfs` and takes the first byte minus `0x30` as the disc. An index below 18 with disc 2, or an index of 18 or more with disc 1, would show interface string `0x222` or `0x223`. This build never shows them. The track number in the table is unchanged, and the same number is a different recording on each disc.

`object 1 + 0x84e0(slot)` is the search on the fourth command corner. It loads the cursor tile. It returns immediately unless attribute byte 0 masked with `0x60` is neither 0 nor `0x60`, and `object 2 + 0x40d8` at the `DTL` byte is 0. A `DTL` byte of 0 is index 0. The function does not return because that byte is 0. The index is the word `object 1 + 0x1b790` stores at `object 2 + 0x9d06`, in [Map](map.md). It shows the unit's portrait and interface string `0x20a` when the mask is `0x20`, otherwise string `0x20b`. `object 1 + 0x7980` returning anything other than 0 shows string `0x20c` and leaves the tile alone. A 0 return plays `Chess.wav` and reads the triple at `object 2 + 0x13c + DTL * 3 + 0x53`. Byte 0 gives the item whose id is the following short: string `0x20d` names it, and `object 1 + 0x15cf0` gives it. A give that fits stores 1 in `object 2 + 0x40d8[DTL]` and calls `object 1 + 0x1e6a0`. A full list shows string `0x20e`. Accepting that drops a chosen pair, gives the found id, writes the dropped id back into the short, and shows string `0x20f`. That swap does not set the flag and does not call `object 1 + 0x1e6a0`, so the tile can be searched again and the short is the dropped id. Refusing the drop, or cancelling the pair pick, shows string `0x210` and leaves the short. Byte 1 adds the short to `object 2 + 0x43b8`, the dword the loss window prints in eight digits and the save writes at `0x30cd`. The string is `0x211` when the short is 0 and `0x212` otherwise, then the same flag and `object 1 + 0x1e6a0`. Any other byte calls `(&`object 2 + 0x1c4`)[short]` with the slot. The keys are below.

Confirm with nobody under the cursor opens `object 1 + 0x4aa0`. Its four corners are the glyphs in [Pictures](pictures.md). Corner 0 calls `object 1 + 0x4e90` and, unless that returns −1, leaves the visit with the returned value. Corner 1 shows string `0x1ea`. Accepting shows `0x1eb`, walks every eligible side-`2` unit to the cursor tile, runs a handler when `object 2 + 0x9d90` changed, commits each unit, and calls the turn change. Refusing shows `0x1ec`. Corner 2 is `object 1 + 0x83c0`, the four toggles below. Corner 3 shows `0x1ed`. Accepting shows `0x1ee` and calls the turn change. Refusing shows `0x1ef`.

`object 1 + 0x4e90` is the second diamond, and it is the save writer in [Save](save.md). Cancelling returns −1. Corner 0 calls the loss window `object 1 + 0x7c90` and returns 0. Corner 1 confirms with string `0x1f3` and, on accept, writes `FDE.SAV` and shows `0x203`. Refusing shows `0x204`. Corner 2 confirms with `0x205`. Accepting shows `0x206` and calls `object 1 + 0x13df0`. Refusing shows `0x207`. Corner 3 confirms with `0x1f0`. Accepting shows `0x1f1`, stores 1 in the quit byte `object 2 + 0x43eb`, and returns 1. Refusing shows `0x1f2`. `object 1 + 0x13df0` reads that file back, in [Save](save.md). When `FDE.SAV` can be opened, the third dword of this diamond's second table is 1. When some unit has flag bit `0x80` set and bit 0 clear, the second dword is 1. The frame those dwords select is in [Pictures](pictures.md).

`object 1 + 0x7980` is the confirm. It keeps the 302×73 rectangle already on VGA `(9, 120)`, rebuilds the map, and paints that rectangle back at buffer `(29, 140)`. The choice starts at 0. Left (`0x4b`) selects 0 and right (`0x4d`) selects 1. Enter or Space returns that choice. Escape (`0x01`) or Delete returns −1. Callers treat 0 as accept. While the choice is 0, `SHADOW.CEL` picture `0x0d` sits at buffer `(275, 123)` and pictures 4 through 7 cycle at `(249, 123)`. While it is 1, picture 8 sits at `(249, 123)` and pictures 9 through 12 cycle at `(275, 123)`. The cycle is `tick / 3` modulo 4. The window copied to VGA `(4, 4)` starts at buffer offset `0x21d8` with pitch `0x168`, so those two points are `(255, 103)` and `(229, 103)` on the 320×200 screen.

`object 1 + 0x83c0` is four more corners from `COMMAND.CEL`. A stored 0 shows pictures `0x31`, `0x32`, `0x33`, and `0x3c`. Any other byte shows `0x0d`, `0x0e`, `0x0f`, and `0x18`. Corner 0 flips `object 2 + 0x8` and calls the phase music with argument 0. Corner 1 flips `object 2 + 0x9d70`, which has to be set before a sample starts, in [Pictures](pictures.md). Corner 2 flips `object 2 + 0x10`, which chooses the map swing or the fight clips in [Combat](combat.md). Corner 3 flips `object 2 + 0x158`. `object 1 + 0x1da80` returns at once unless that byte and `object 2 + 0x159` are both nonzero, and then it draws `ADWin.cel` picture 0 on the map buffer at `(`object 2 + 0x16c`, 160)`. The x becomes `0x124` when the cursor is at least 5 tiles below the camera and at most 1 tile to its right, and `0x19` when it is at least 5 tiles below and more than 10 tiles to the right. The current terrain picture is drawn at `(x + 9, 175)`, with the attack and defense percents of that terrain. A unit under the cursor adds its map frame and the pool at `+0x40` in four digits. `object 2 + 0xc` is 3 while that pool is not its maximum. `object 1 + 0x1a280`, `object 1 + 0x20f80`, and `object 1 + 0x2b7f0` also store 0 or 1 into `object 2 + 0x158`. Those conditions were not read. `object 2 + 0x159` is the other gate. The turn change stores 0 at `object 1 + 0xe3d7` and stores 1 at `object 1 + 0xe7fe`, on the way out. The visit stores 0 at `object 1 + 0x4c51` and `object 1 + 0x4e26` before that call, and stores 1 at `object 1 + 0x4d41` and `object 1 + 0x4e32` when the cursor loop resumes. The icon script stores 0 at `object 1 + 0x11f46` and stores 1 again at `object 1 + 0x120ab`. The status window saves the byte and stores 0 at `object 1 + 0x6ae4`.

`object 1 + 0x15210` counts the eight pairs whose flag bit `0x80` is clear. The village lists below treat 0 as an empty list and 8 as a full one.

`object 1 + 0x23440` picks a roster index. Escape or Delete returns −1. Enter or Space returns `object 2 + 0x1bc`, except when the scenario index is at least `0x17` and that index is 3, in which case Enter does not confirm. Left and right step by one, and up and down step by three, inside the roster count. The window at `object 2 + 0x1b8` shows six records, three across. Each cell draws `SELBAR.CEL` picture 2 on the selection, at the cell's x minus 6 and its y plus 5. Command pictures `0x2a` and `0x2b` sit on the cell, the roster icon frame is drawn, and interface string `byte + 8 + 1` is at the cell's x plus 28 and its y plus 6. On a scenario at or above `0x17`, a record whose byte `+8` is 1 is drawn with expander mode 9. The copy is 304×67 from buffer `(5, 3)` onto VGA `(8, 125)`. `object 1 + 0x5bd0` runs after the six cells. It is the palette cycle in [Pictures](pictures.md), and the command-menu reader calls it on the same poll.

`object 1 + 0x22fa0` draws one member of a second grid, three across, into a buffer of pitch `0x138`. The column is the index modulo 3 and the row is the index divided by 3. The icon is 24×24 at `(column * 101 + 9, row * 67 + 12)`. Interface string `byte + 8 + 1` is at `(column * 101 + 39, row * 67 + 21)`. Command picture `0x2a` is at `(column * 101 + 7, row * 67 + 29)` and `0x2b` is at `(column * 101 + 32, row * 67 + 29)`. When the class can wear the item, picture `0x2c` is drawn and the price digits follow. Otherwise interface string `0x1f7` is drawn in ink `0x2b`.

On the buy path that can equip, the line local is set to 38. Interface strings `0x1f8`, `0x213`, and `0x1f9` are then drawn at the shop pen plus those 38 rows, which is `(20, 169)`. String `0x1f8` is the path where the price is within `object 2 + 0x43b8`. String `0x213` is the path where it is not. String `0x1f9` follows the negation of the price dword.

`object 1 + 0x222e0` plays `ShopWin.Cel` in nine steps through expander mode 4. Argument 1 runs the steps from 8 down to 0, and 0 runs them upward. `object 1 + 0x23d70`, `object 1 + 0x23f80`, and `object 1 + 0x24190` are the three lists those village actions call. Each one picks a roster index, and a count of 0 shows interface string `0x1fb` with `object 2 + 0x4030` set to byte `+8` plus 1, at the shop pen `0xaa3d4`. `object 1 + 0x23d70` then picks a pair. String `0x1fc` names the item. The shift is unsigned.

```
# object 1 + 0x23d70, on accept
credit = (item[+0x13] * 3) >> 2
remove the pair
object 2 + 0x43b8 += credit          # play Incom.wav, then rebuild the combat words
```

`object 1 + 0x220e0(0xa8208, 0x140)` draws command pictures `0x34` through `0x36` at VGA `(8, 104)` and that dword in eight digits. `object 1 + 0x23f80` picks a pair, shows string `0x1fd`, and picks a second roster index. A count of 8 shows string `0x1fa`. Any smaller count removes the pair from the first record and gives that id to the second. `object 1 + 0x24190` calls `object 1 + 0x15d70` on the chosen index, which is the equip list in the command menu above.

The five village actions are the same menu shape. Each opens its `CEL`, keeps a `0xfa00` screen, and reveals it with `object 1 + 0x214f0(screen, 0x9f, 0x63, 1)`. That call walks nine steps, 0 through 8. Step 8 copies the whole screen. The other steps pass 50, 200, 500, 800, 1000, 1200, 1300, 1400, and 1500 to `object 1 + 0x21690`, with both angles 0. The call writes 318 samples on each of 198 rows, starting at `0xa0000`. Two bytes at the end of each row, and the last two rows, are left as they were. The first step reads source rows 74 through 124 and columns 123 through 201. The eighth reads source rows 0 through 197 and columns 4 through 321. A sample outside the fixed-point rectangle is written as 0. These nine scales stay inside it. Division is toward zero.

```
# object 1 + 0x214f0, each step 0 through 8
red = red + (step - 8) * 3
green = green + (step - 8) * 3
blue = blue + (step - 8) * 3

# object 1 + 0x21690. scale is 2000 minus the step's value.
# dest row y runs from -99 through 98. a column step is in 1/128 of a pixel.
src_row = 99 + trunc(y * 2000 / scale) / 4
column_step = trunc(table * 32 / scale) + 32
```

Leaving walks the steps from 8 down through 0, fills the screen with 0, and clears the bias. The menu then loops on `object 1 + 0x22150` until the selection is −1. Up and right move to the next corner. Down and left move to the previous one. Either move plays `Beep.wav`. Escape or Delete stores −1. Enter or Space accepts. `object 1 + 0x22240` draws the corners in one row at y 106. The rightmost picture starts at x 273 and each step to the left is 26. The selected corner is command picture `0x1a` and the others are `0x1b`, and the corner's own picture is drawn on top.

| Room | Pictures, left to right |
| --- | --- |
| Bar | `0x24`, `0x09`, `0x0a`, `0x08` |
| Church | `0x24`, `0x12`, `0x04`, `0x10` |
| Item | `0x24`, `0x14`, `0x15`, `0x04`, `0x10` |
| Weapon | `0x24`, `0x14`, `0x15`, `0x04`, `0x06` |
| Secret | `0x24`, `0x14`, `0x15`, `0x04`, `0x06`, `0x10` |

Leaving plays `ShopWin.Cel` closed. The corners, in order:

| Action | File | Prompt, then the corners |
| --- | --- | --- |
| `object 1 + 0x25a30` | `BarShop.cel` | Plays `object 1 + 0x261d0` before the menu. Prompt `0x200`. Scenario string 6. `object 1 + 0x141b0` on the screen, the slot writer in [Save](save.md). `object 1 + 0x14460`, and when that returns 1 it calls `object 1 + 0x212b0`. Interface string `0x1f0`; a confirm of 0 stores the quit byte, shows `0x1f1`, waits `object 1 + 0x2d0e0(0x12c)`, and leaves the menu. |
| `object 1 + 0x25810` | `Church.cel` | Prompt `0x200`. Scenario string 7. `object 1 + 0x24310`, the rank change in [Units](units.md). The give list. `object 1 + 0x23cf0`. |
| `object 1 + 0x255d0` | `Item.cel` | Prompt `0x1f4`. Scenario string 4. `object 1 + 0x238f0` with group 0. The sale list. The give list. `object 1 + 0x23cf0`. |
| `object 1 + 0x25d40` | `Weapon.cel` | Prompt `0x1fe`. Scenario string 5. `object 1 + 0x238f0` with group 1. The sale list. The give list. The equip list. |
| `object 1 + 0x25f80` | `Secret.cel` | Prompt `0x202`. Scenario string 8. `object 1 + 0x238f0` with group 2. The sale list. The give list. The equip list. `object 1 + 0x23cf0`. |

The prompt and the string shown again after a corner are interface strings, at the shop pen `0xaa3d4`. `object 1 + 0x23cf0` picks a roster index and calls `object 1 + 0x6a90`, the status window. `object 1 + 0x212b0` frees `object 2 + 0x124` when it is nonzero and loads `fdetxt%02d.txt` and `Shop%02d.dat` from `FIELD.VFS`. The text number is the scenario index plus 1, in [Text](text.md). The shop number is the index. It then points the battle array at the roster, in [Units](units.md). For each of the `object 2 + 0x9cdc` entries it frees the pointers at `object 2 + 0x9cb0`, `object 2 + 0x9c20`, and `object 2 + 0x9c98`, and stores 0. When `object 2 + 0x9cf0` is nonzero it frees the icon cache at `object 2 + 0x138` and stores 0. It opens `ICON.CEL` and calls `object 1 + 0x13020` with each roster record's byte `+7`. The return is not stored.

`object 1 + 0x261d0` returns at once unless `object 2 + 0x4110` is 0 and the date from `object 1 + 0x32ed0` is 28 January 1998. That helper is INT 21h function `0x2a`: the word at struct `+2` is the year, the byte at `+1` is the month, and the byte at `+0` is the day. The compares are year `0x7ce`, month 1, and day `0x1c`. The weekday byte at `+4` is stored and not tested. No other site compares that year. The dword is 0 after the title, which stores 0 at `object 1 + 0x1a2bc`, and a campaign-slot load copies the saved dword back, in [Save](save.md). On the matching day the body shows interface string `0x224` through `object 1 + 0xff30`, starting at VGA `(20, 131)`, then plays `Bonus-1.saf`. Disassembly of the body, not a decompile. `object 1 + 0x1a110(object 2 + 0x128, object 2 + 0x1fe0)` opens it from `MISC.VFS`. The picture is drawn in the fight compose buffer, pitch `0x170`, at `(0x18, 0x18)`. The copy to the VGA is 320×200 from buffer `+0x2298`, the same point, so the frame's top left is the screen's top left and a 336×216 frame is cut to that window.

The cursor is reset with `object 1 + 0x4540` mode 1, so the first picture is frame 0. Six steps mix that frame over the screen that already holds the string. The mode-9 pointer is `object 2 + 0x53f0`, then the selector, then `object 2 + 0x43f0`. The selectors are 15, 12, 9, 6, 3, and 0, one change of `object 2 + 0x9d64` each. The mix is the one in [Pictures](pictures.md). This blit passes 0, so it does not start the sample. Each of the ten frames stores hold 1 and sample index 0, and the file has one sample.

Mode 0 then advances one frame per call and wraps to frame 0 after frame 9. For a count of 8 down through 1, the body repeats `(object 1 + 0x32a68() % 10) + 1` times: advance, blit with the sample argument set, and hold for that many ticks. It calls `object 1 + 0x46523`, then advances and shows one tick while `object 1 + 0x4652e` returns a byte above `0x7f`. For a count of 1 through 8 it repeats `(object 1 + 0x32a68() % 3) + 1` times the same advance and hold. Each of those blits passes 1, so each one starts sample 0.

The compare that follows reads a local twelve bytes below the frame. This function does not store that local before the compare. The only caller is `object 1 + 0x25a30`, and the call passes no argument. That caller's frame is `0x20` bytes. At the call the unread local sits `0x20` bytes below that frame, so the bar function does not store it either. The only store is after the four arms, from the closing-text table, and it does not choose the gift. The arms are still in the body. 0 opens `Bonus.wav` at `object 2 + 0x1fec` in the same archive, starts it with `object 1 + 0x20790`, gives item `object 2 + 0x9cf4 / 10 + 0xbf` once, and calls `object 1 + 0x204d0` on the returned handle until that call returns 0. `object 1 + 0x204d0` returns 1 when `object 1 + 0x2f26e` on the slot `object 2 + 0x9d30` indexed by that handle returns 4, and 0 otherwise. The body of `object 1 + 0x2f26e` is the sample driver. It is outside the gameplay and is discarded. 1 gives item `0xb9` ten times. 2 adds `0x4e20` to `object 2 + 0x43b8`. Any other value gives item `0xb4` once. The give is `object 1 + 0x26860`. It walks roster slots 0 through `object 2 + 0x4114` minus 1. A slot whose `object 1 + 0x15210` count is 8 is skipped. Slot 3 is also skipped when `object 2 + 0x9cf4` is at least `0x17`. Any other slot is `object 1 + 0x15cf0(slot, item)`.

The ten dwords at `object 1 + 0x20f50` are 0, 3, 1, 2, 3, 2, 1, 3, 2, 3. The cursor's frame indexes that table. The body then shows interface string `0x225` plus the indexed value, then interface string `0x229`, both through the same walk at `(20, 131)` over the last frame, and stores 1 into `object 2 + 0x4110`. Which of the four arms runs is that local. The selector is outside the gameplay and is discarded.

`object 1 + 0x14e70(slot, row, dest, pitch)` draws the eight pairs. A selection argument from 0 through 7 draws `SELBAR.CEL` picture 0 at `(0, row * 17 + 8)`. A pair whose flag bit `0x80` is set is skipped. The mark comes from `COMMAND.CEL` through `object 1 + 0x5b80`, 25×22, at `(3, slot * 17 + 9)`. Item byte 0 from 1 through `0x15` uses picture `0x1d`, from `0x16` through `0x27` uses `0x1e`, and any other byte uses `0x1f`. Flag bit `0x40` adds 4. The name is interface string `id + 0xc9`, and the pen at `object 1 + 0x14fb5` is `(0x13, slot * 17 + 8)`, ink `0xd0`, shadow `0x6d`. The second picture is at `(0x66, slot * 17 + 13)`. Types 1 through `0x15` use picture `0x40` and the short at item `+1`. Types below `0x28` otherwise use picture `0x41` and the short at `+5`. A type at or above `0x28` uses picture `0x3e` when byte `+0x0d` is `0x0b`, picture `0x3f` when it is `0x0c`, and in both of those the short at `+0x0e`. Any other byte `+0x0d` uses picture `0x43` and no number. The four digits start `0x16` to the right of that picture, width 4, with the sign flag 0. The status window and the battle item picker call this too.
