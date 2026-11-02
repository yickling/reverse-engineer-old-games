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

`FUN_00015cf0` keeps four disable flags. Slot 0 is disabled when `FUN_00025110(unit, 0)` finds no weapon or `FUN_00011e50` lists nobody. Slot 1 is disabled when `FUN_00027810` returns 0 or byte `+0x27` is nonzero. Slot 2 is disabled when `FUN_00025210` returns 0. The first flag that is still 0 is the initial selection. Choosing slot 0 runs the attack in [Combat](combat.md) and then `FUN_000119b0`, which ORs bit `0x80` into byte `+5`. Slot 1 is `FUN_00027bf0`. Slot 2 is `FUN_00025280`. Any other slot calls `FUN_000120d0` when the menu was opened without a move, then `FUN_000184e0` and `FUN_000119b0`. `FUN_000184e0` was not decompiled. `FUN_000120d0` is the rest below.

`FUN_00027bf0` stays in a spell list until one cast is confirmed. `FUN_00028100` reads up and down. A window of eight rows follows the selection. Enter or Space returns 1 when byte `+5` of the spell row is at or below `+0x44`, and stays on the list when it is not. Escape or Delete returns −1, which leaves the command menu. The id comes from `FUN_00027810`. Byte `+3` of the spell row decides the aim. Zero lists targets from the cursor tile at range byte `+4`, with the side filter fixed at 0, and the cursor picker runs in mode 4, or mode 5 when that list is empty. Nonzero first lists at range byte `+3` with the side byte at `+6`. Below `0x10` it then lists again at byte `+4`. At or above `0x10` the second list is `FUN_00013670` from the unit's own tile, and `Chess.wav` plays. Id `0x15` refuses a list whose first id is the caster, and a confirmed aim stores the cursor tile at `DAT_0006437c` and `DAT_00064380` before a second confirm. A confirmed cast always calls `FUN_0001a4a0`, then the death spin and the death-record walk. The experience term is divided by `+0x21`, plus `0x1e` when the character id is above 8, and `FUN_0001dd00` applies it.

`FUN_00025280` draws a second menu through `FUN_00016120` and reads it with `FUN_000161f0`. Those two, and `FUN_000161a0`, were not decompiled. Cancelling returns. Row 0 picks a carried index with `FUN_00025990`, reads the id at `+0x0b + index * 2`, aims with the record's range byte `+0x10` and effect byte `+0x12`, and calls `FUN_00026270`. Record byte `+0x0d` of `0x1c` or `0x19` asks for one more confirm and stores the cursor tile the same way id `0x15` does. A confirmed use then calls `FUN_000119b0` and returns 1. Row 1 picks an item and a unit on the cursor tile. `FUN_00025cf0` returning −1 swaps one item each way through `FUN_00025c90`. Any other return removes the giver's item. Both paths call `FUN_00024d40` and return 2. Row 2 is `FUN_00025d70`. It lists the pairs. `FUN_00025fb0` returns 1 when one of six bytes from `FUN_00018b90(class)` equals the item record's first byte. A row that passes calls `FUN_00026040`, plays `Equip.wav`, and rebuilds the combat words. `FUN_00026040` clears bit `0x40` on other pairs in the same group, then stores `0x40` in the chosen pair's flag. The group is the record's first byte: below `0x16` is one group, and `0x16` or above is the other. A first byte of 0 does not clear another pair. Any other menu row removes the picked item with `FUN_00025c90` and calls `FUN_00024d40`.

`FUN_00025990` plays `OpWin1.wav` and returns what `FUN_00025af0` chooses. That picker counts pairs whose flag bit `0x80` is clear and moves an index inside that count. Up and down wrap, and each plays `Beep.wav`. Enter or Space returns 1. Escape or Delete returns −1. The use row passes 1 as the second argument, and then Enter is refused while byte `+0x0d` of the record is 0. The other calls in `FUN_00025280` pass 0, so Enter accepts the row. Give and remove keep the empty pairs at the end, so this index is the pair index.

`DAT_0006028c` is a table of code pointers indexed by the scenario, parallel to the ending table at `0x60304` and the opener table at `0x60074`, but not the same pointers. The first is `0x3a120`. These bodies were not created as functions. Disassembly of `0x3a120`, not a decompile: it calls `FUN_000109b0(2)`, and that function returns bit 0 of unit 2's flag byte. If the bit is set, it pushes the loaded text block and the constant `0xf` into a call, then writes `1` to `DAT_00069da0` and returns. The other scenarios were not disassembled. The session loop treats `1` as the `GameOver.saf` path and `2` as the per-scenario ending.

`FUN_0002e7a0` looks for a side-`2` unit that is still eligible (flag bits `0x81` clear, `+0x26` clear). If none remains, it calls `FUN_0001e3c0`, which is the turn change:

1. For each eligible side-`2` unit whose `+0x40` is not its `+0x42`, and whose `+0x25` and `+0x26` are 0, add `+0x42 / 5` to `+0x40`, capped at `+0x42`. If any unit was changed, play `REST.WAV`.
2. `FUN_00012b20` walks side `1`. For each eligible unit it calls `FUN_00010010(unit, 1)`, then the same two callback tables as the player's action. It stops when `DAT_00069da0` becomes nonzero.
3. If the outcome is still 0, `FUN_0001ead0` plays `EnyPhase.saf`, then `FUN_00012960` walks side `0` the same way, with an extra distance test (`DAT_00063f88` and `DAT_00063f8c` against 5) in front of the call.
4. If the outcome is still 0, increment `DAT_00069ce8`, `FUN_0001ead0` plays `PlyPhase.saf`, and return to the cursor. A few item checks on the way back call `FUN_0001f4e0` when a carried byte has bit `0x40` and the second pool is not full. The same player is also called with `PlyPhase.saf` from `0x24190`.

`FUN_00010010` is one unit's phase. It returns immediately when bit 0 of byte `+5` is set. The low nibble of `+0x34` selects the script. Bytes `+0x35` and `+0x36` are the two tile arguments, and byte `+0x3d` is the index script 5 uses. The second argument is the side filter: `0` hunts a unit whose side is not `0`, and any other value hunts side `0`. The side-`1` walk passes `1`.

A script that returns 0 did not act, and the next call in that row runs. `FUN_00012c10` is the scored action in [Combat](combat.md). `FUN_000126b0` flood-fills with budget 100 on the class row and asks `FUN_00011460` for a destination; a destination other than the unit's own tile is walked. What `FUN_00011460` picks was not read. `FUN_000127c0` walks toward the nearest visible unit the side filter accepts, by Manhattan distance. `FUN_000120d0` rests: if `+0x40` is already `+0x42`, or `+0x25` or `+0x26` is nonzero, it returns 0. Otherwise it centers the camera, plays `REST.WAV`, and adds `+0x42 / 5` to `+0x40`, capped at `+0x42`.

| Nibble | What it tries, in order |
| --- | --- |
| 0 | Scored action, then the budget-100 walk, then the nearest unit, then rest. |
| 1 | Scored action, then the budget-100 walk, then rest. |
| 2 | Scored action, then the swing scorer. That scorer returns 0, so this row then rests. |
| 3 | Scored action. Otherwise `FUN_0002d9b0` looks up the unit id in `+0x35`. A miss uses row 0's three fallbacks. A hit walks to that unit's tile, and a failed walk rests. |
| 4 | Walk to the tile in `+0x35`, `+0x36`. A failed walk rests. |
| 5 | Scored action. Otherwise, when byte `DAT_000640d8[+0x3d]` is 0 and `FUN_00013e10` returns a tile, walk there. Landing on it copies the byte at `DAT_0006013c + index * 3 + 0x53` and the following short into `+0x31` and `+0x32`, calls `FUN_00025cf0` when that byte is 0, sets the flag byte, calls `FUN_0002e6a0`, stores `7` in `+0x34`, and plays `Chess.wav`. A flag already set, or no tile, uses row 0's three fallbacks. |
| 6 | Nothing in the script. The tail below still runs. |
| 7 | Walk to `+0x35`, `+0x36`. A failed walk rests. Landing there plays `Posion.saf` through `FUN_00026dd0` when the character id is `0x24` through `0x27`, then stores `1` in byte `+5`. |
| 8 | Return. The tail does not run. |
| 9 | Look up the unit id in `+0x35`. A miss is row 0. A hit walks there, and a failed walk is row 0. |
| 10 | Score the carried-item action. Above 5, take it. Then score the swing: below 6, the budget-100 walk, otherwise the swing. |
| 11 | Character ids `0x3c` through `0x3e` call `FUN_00010760` first. Then the same shape as row 10, with the spell score and `FUN_00013c90` in place of the item. |

`FUN_0002d9b0`, `FUN_00013e10`, `FUN_00010760`, and `FUN_00026dd0` were not decompiled. After every nibble except 8, `FUN_0002ddc0` is called with the unit's tile and `1`, bit `0x80` is ORed into byte `+5`, and the map is redrawn. `FUN_0002ddc0` was not decompiled.

`FUN_0002de50` and `FUN_0001fa00` are called with 1, then 0, then 2 around those walks. `FUN_0002de50` was not read. `FUN_0001fa00` walks the units whose side byte equals that argument and whose flag bit 0 is clear. Where `+0x25` is nonzero it sets `+0x40` to `max(0, +0x40 - +0x42 / 10)`. It then decrements each nonzero byte from `+0x22` through `+0x27`, and a byte that reaches 0 is followed by `FUN_00024d40` on that unit. `FUN_00030a30(scenario, 0 or 1)` sits at the same points and was not read.
