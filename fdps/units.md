# Unit record

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_0002cfa0` returns `DAT_00069cd8 + id * 0x50`. The array is allocated to `count * 0x50`. Count lives in `DAT_00060150`.

Bytes filled by the spawners `FUN_00023280` and `FUN_00022bb0`, and read by the map drawer and the combat players:

| Offset | Role |
| --- | --- |
| `+0`, `+1` | Tile x, y. `FUN_0002b790` reads the map cell there. Backdrop, terrain, and the detail byte all come from that query. |
| `+2` | Slot in the loaded `ICON.CEL` cache. `FUN_00023020` returns it. |
| `+3` | Facing, 0..3. See [map sprites](pictures.md#map-sprites). |
| `+4` | Sub-tile progress. The drawer multiplies it by a per-facing pixel step. |
| `+5` | Flags. Bit 0: map drawer skips the unit. Bit `0x80`: map sprite locks to the middle walk frame, and the system menu treats the unit as eligible when bit 0 is clear. |
| `+6` | Side. `0` selects the `"E"` spell prefix and one mirror sign; any other value selects `"M"`. Spawn writes `2`. The cursor commands side `2`. The two phase walks use side `0` and side `1`. |
| `+7` | Character id. Indexes `STAND`, `ACT`, `MAGIC`, and the character inside `ICON.CEL`. `0x80` means "no sprite" on the map. |
| `+8` | Compared with `7` and `3` while a destination is being chosen. Not followed. |
| `+0x20` | Class. `FUN_00018b60` returns `DAT_00063fd0 + (class + 1) * 10`, a row of `ProMap.dat`. |
| `+0x21` | Byte used as the divisor of the experience term in `FUN_0001c4f0`. |
| `+0x25` | Written by a weapon whose byte `+9` is `4`. Regeneration skips the unit while this is nonzero. |
| `+0x26` | Nonzero freezes the map sprite on frame 0 of its facing and jitters x by one pixel. A weapon whose byte `+9` is `1` writes `2` or `3` here. The cursor will not command the unit while it is nonzero. |
| `+0x31` | Set to `0xff` at spawn. |
| `+0x3b` | Move budget, in tiles. The flood fill stops when the accumulated cost would pass it. |
| `+0x40` | Word reduced by the damage formula. At spawn it is copied from `+0x42`. Inferred to be current hit points: the bar and both attack paths treat it as the pool that reaches 0. |
| `+0x42` | Maximum of that pool. |
| `+0x44`, `+0x46` | Second current/max pair. At the start of `FUN_0001e3c0` a side-`2` unit gains `max / 5`, capped at max. Inferred to be a second pool, from that shape. |
| `+0x48` | Attack word, read by `FUN_0001c4f0` and `FUN_00019f60`. |
| `+0x4a` | Defense word. |
| `+0x4c` | Hit word. A roll of `rand % 100` lands when it is below this minus the defender's `+0x4e`. |
| `+0x4e` | Word subtracted from the attacker's hit word. |

`+0x37`, `+0x39`, `+0x3b`, `+0x3e` are filled from class tables (`FUN_00018aa0` / `FUN_00018ad0` below id `0x3c`, else `FUN_00018b00`). Six item slots start at `+0x0e` as byte pairs. `FUN_00018920` loads `ProMap.dat` to `DAT_00063fd0`, and beside it `Friaprda.dat`, `FriLevUp.dat`, `Item.dat`, `EnemyDat.dat`, `ProEqu.dat`, `MagicDat.dat`, `GetMgTab.dat`, and `RankUp.dat`. Those files were not decoded. The rest of the 80 bytes is still unmapped.

How those words are combined in an attack is in [Combat](combat.md). How a scenario places the records is in [Scenario files](scenario.md).
