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

`FUN_00015cf0` keeps four disable flags. Slot 0 is disabled when the equipped slot is empty or `FUN_00011e50` lists nobody. Slot 1 is disabled when `FUN_00027810` returns 0 or byte `+0x27` is nonzero. Slot 2 is disabled when `FUN_00025210` returns 0. The first flag that is still 0 is the initial selection. Choosing slot 0 runs the attack in [Combat](combat.md) and then `FUN_000119b0`, which ORs bit `0x80` into byte `+5`. Slot 1 calls `FUN_00027bf0` and slot 2 calls `FUN_00025280`. Any other slot calls `FUN_000120d0` when the menu was opened without a move, then `FUN_000184e0` and `FUN_000119b0`. Those three bodies were not decompiled.

`DAT_0006028c` is a table of code pointers indexed by the scenario, parallel to the ending table at `0x60304` and the opener table at `0x60074`, but not the same pointers. The first is `0x3a120`. These bodies were not created as functions. Disassembly of `0x3a120`, not a decompile: it calls `FUN_000109b0(2)`, and that function returns bit 0 of unit 2's flag byte. If the bit is set, it pushes the loaded text block and the constant `0xf` into a call, then writes `1` to `DAT_00069da0` and returns. The other scenarios were not disassembled. The session loop treats `1` as the `GameOver.saf` path and `2` as the per-scenario ending.

`FUN_0002e7a0` looks for a side-`2` unit that is still eligible (flag bits `0x81` clear, `+0x26` clear). If none remains, it calls `FUN_0001e3c0`, which is the turn change:

1. For each eligible side-`2` unit whose `+0x40` is not its `+0x42`, and whose `+0x25` and `+0x26` are 0, add `max / 5` to the second pool (`+0x44`), capped at `+0x46`. If any unit was changed, play `REST.WAV`.
2. `FUN_00012b20` walks side `1`. For each eligible unit it calls `FUN_00010010(unit, 1)`, then the same two callback tables as the player's action. It stops when `DAT_00069da0` becomes nonzero.
3. If the outcome is still 0, play `EnyPhase.saf`, then `FUN_00012960` walks side `0` the same way, with an extra distance test (`DAT_00063f88` and `DAT_00063f8c` against 5) in front of the call.
4. If the outcome is still 0, increment `DAT_00069ce8`, play `PlyPhase.saf`, and return to the cursor. A few item checks on the way back call `FUN_0001f4e0` when a carried byte has bit `0x40` and the second pool is not full.

`FUN_0002de50` and `FUN_0001fa00` are called with 1, then 0, then 2 around those walks. Their effect on the flag byte was not read. `FUN_00030a30(scenario, 0 or 1)` sits at the same points and was not read.
