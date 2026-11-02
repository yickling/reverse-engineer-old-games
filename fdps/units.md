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
| `+5` | Flags. Bit 0: map drawer skips the unit. Bit `0x80`: map sprite locks to the middle walk frame, and the system menu treats the unit as eligible when bit 0 is clear. `FUN_000119b0` ORs in bit `0x80` when an action is committed. A unit whose pool at `+0x40` is 0 is stored as `1` by the destruction sequence, so bit 0 is set and bit `0x80` is cleared. |
| `+6` | Side. `0` selects the `"E"` spell prefix and one mirror sign; any other value selects `"M"`. A roster copy stores `2`. A scenario spawn copies byte 0 of its 26-byte record, which is 0, 1, or 2. The cursor commands side `2`. The two phase walks use side `0` and side `1`. |
| `+7` | Character id. Indexes `STAND`, `ACT`, `MAGIC`, the twelve `ICON.CEL` frames, and the `FACE.CEL` portrait of the same number. Which of those files are present, and which ids share one sheet, is in [Pictures](pictures.md). `0x80` means "no sprite" on the map. |
| `+8` | Compared with `7` and `3` while a destination is being chosen. Not followed. |
| `+9` | `FUN_00034310` adds this byte to `+0x44`. That function is called from the village action at `0x35810`. The rest of the body was not read. |
| `+0x1a` | First byte of the learned-id bits. `FUN_00028280(unit, id)` sets bit `id % 8` of byte `+0x1a + id / 8`. The masks are `01 02 04 08 10 20 40 80` at `0x27630`. |
| `+0x1f` | Byte 0 of the `Friaprda.dat` or `EnemyDat.dat` row, copied by spawn. What reads it was not followed. |
| `+0x20` | Class. Byte 1 of that same row. `FUN_00018b60` returns `DAT_00063fd0 + (class + 1) * 10`, a row of `ProMap.dat`. |
| `+0x21` | Byte used as the divisor of the experience term in `FUN_0001c4f0`. `FUN_0001dd00` adds 1 when the byte at `+0x3c` crosses 100. |
| `+0x22`, `+0x23` | Counts. While nonzero, the rebuild multiplies attack, or defense, by the double `1.15` at `0x61b1c` and `0x61b24`, then `FUN_0003d25c` rounds toward zero. `FUN_000162f0` writes 1 to `0x6000c` when the byte is nonzero. |
| `+0x24` | Count. While nonzero, the rebuild adds `0x0f` to the hit base before equipped items are added. |
| `+0x25` | Count. A weapon whose byte `+9` is `4` writes `rand % 4 + 2`. Regeneration skips the unit while this is nonzero, and the phase tick below subtracts a tenth of `+0x42` from `+0x40`. |
| `+0x26` | Count. Nonzero freezes the map sprite on frame 0 of its facing and jitters x by one pixel. A weapon whose byte `+9` is `1` writes `rand % 2 + 2`. The cursor will not command the unit while it is nonzero. |
| `+0x27` | Count. Nonzero makes menu slot 1 refuse, and the spell scorer returns without a candidate. |
| `+0x31` | Three bytes. Spawn sets the first to `0xff`. When the pool at `+0x40` is below 1 and bit 0 of `+5` is clear, `FUN_00026150` copies all three into the list that `FUN_0001d960` walks. What the first byte selects is in [Combat](combat.md). |
| `+0x34` | Low nibble selects the phase script in [Turns](turns.md). Bit `0x40` makes a tied score prefer the swing. Bit 0, which an odd nibble already has set, doubles the pool-fraction spell score. Bit `0x80` triples the pool-fraction item score. Bytes `+0x35` and `+0x36` are that script's tile arguments. |
| `+0x3b` | Move budget, in tiles. The flood fill stops when the accumulated cost would pass it. |
| `+0x3c` | Byte added to the experience term. At 100 it is reduced by 100 and `+0x21` increases by 1. |
| `+0x3d` | Index script 5 reads, into `DAT_000640d8` and into the three-byte rows at `DAT_0006013c`. |
| `+0x40` | Word reduced by the damage formula. At spawn it is copied from `+0x42`. Inferred to be current hit points: the bar and both attack paths treat it as the pool that reaches 0. |
| `+0x42` | Maximum of that pool. |
| `+0x44`, `+0x46` | Second current/max pair. Spawn copies `+0x46` into `+0x44` beside the copy of `+0x42` into `+0x40`, at `0x22d90`. The same pair of copies, with byte `+5` cleared, is at `0x3ae8f` and `0x3b3df`. The spell scorer skips a spell whose row byte `+5` is above `+0x44`. A cast subtracts that byte: `FUN_00028590` does it for the fight player `FUN_0001a4a0`, and `FUN_000288c0` does the same store at `0x28942`. The subtraction does not clamp. `FUN_00027570` adds to `+0x44` and caps it at `+0x46`. The rest at the start of `FUN_0001e3c0` adds to `+0x40`, not to this pair. Inferred to be a second pool. |
| `+0x48` | Attack word, read by `FUN_0001c4f0` and `FUN_00019f60`. |
| `+0x4a` | Defense word. |
| `+0x4c` | Hit word. A roll of `rand % 100` lands when it is below this minus the defender's `+0x4e`. |
| `+0x4e` | Word subtracted from the attacker's hit word. |

`+0x37`, `+0x39`, `+0x3b`, `+0x3e` are filled from class tables (`FUN_00018aa0` / `FUN_00018ad0` below id `0x3c`, else `FUN_00018b00`). `FUN_00024d40` rebuilds the four combat words from those bases and from every equipped item. The arithmetic below is that function. `Item.dat` is the table at `DAT_00063fe0`, one record per id, stride `0x17`, from `FUN_00018b30`.

```
attack  = +0x37
defense = +0x39
hit     = +0x3e
avoid   = +0x3e
if +0x24 != 0:
    hit += 0x0f
    avoid += 0x0f
for each pair whose flag has bit 0x40:
    rec = Item.dat[id]
    attack  += short(rec + 1)
    hit     += short(rec + 3)
    defense += short(rec + 5)
    avoid   += short(rec + 7)
if +0x22 != 0: attack  = trunc(attack  * 1.15)
if +0x23 != 0: defense = trunc(defense * 1.15)
+0x48, +0x4a, +0x4c, +0x4e = attack, defense, hit, avoid
```

`trunc` is `FUN_0003d25c`, which rounds toward zero. The two `1.15` values are the doubles at `0x61b1c` and `0x61b24`.

Eight item pairs start at `+0x0a`. Pair `i` is the flag byte at `+0x0a + i * 2` and the id at `+0x0b + i * 2`. Bit `0x80` of the flag marks an empty pair. Bit `0x40` marks the pair equipped. `FUN_00025cf0` writes an id into the first empty pair and clears bit `0x80`. It returns −1 when all eight are full. `FUN_00025c90` slides the later pairs down over the removed index and stores `0x80` at `+0x18`.

The first byte of the item record is the type. `FUN_00026040` keeps one equipped item in each group. A type below `0x16` clears other equipped items below `0x16`. A type at or above `0x16` clears other equipped items at or above `0x16`. A type of 0 clears nothing. The chosen flag is then stored as `0x40`. `FUN_00025110(unit, 0)` returns the first equipped pair whose type is from 1 through `0x15`. `FUN_00025110(unit, 1)` returns the first whose type is from `0x16` through `0x27`. The attack paths call it with 0. `FUN_000338f0` calls it with 1, and that function is also the shop list in [Scenario files](scenario.md). A class may equip a type when one of six bytes in its `ProEqu.dat` row equals that type. `FUN_00018b90` returns `DAT_00063fe4 + class * 6`, and `FUN_00018920` loads `ProEqu.dat` there. How a use changes the pools is in [Combat](combat.md). A level raises the bases and both maximums, in [Combat](combat.md). `FUN_00018920` loads nine tables through `FUN_000293d0`. Each file below is a member of `MISC.VFS`. The stride is the multiplier in the index function, and the row count is the file length divided by that stride. Every row ends at or before the end of the file.

| File | Index | Stride | Rows |
| --- | --- | --- | --- |
| `Friaprda.dat` | `FUN_00018aa0(character)` | `0x18` | 60 |
| `FriLevUp.dat` | `FUN_00018ad0(character)` | `0x0b` | 60 |
| `EnemyDat.dat` | `FUN_00018b00(character - 0x3c)` | `0x0a` | 91 |
| `Item.dat` | `FUN_00018b30(id)` | `0x17` | 251 |
| `ProMap.dat` | `FUN_00018b60(class + 1)` | `0x0a` | 41 |
| `ProEqu.dat` | `FUN_00018b90(class)` | 6 | 36 |
| `MagicDat.dat` | `FUN_00018bc0(id)` | 7 | 40 |
| `GetMgTab.dat` | `FUN_00018bf0(index)` | `0x0c` | 60 |
| `RankUp.dat` | `FUN_00018c20(index)` | `0x0c` | 9 |

`ProMap.dat` has 41 rows because the callers pass `class + 1`. Class 0 reads the second row, and class 39 reads the last. `MagicDat.dat` byte `+6` is the side `FUN_00013420` passes to the target list, and `Item.dat` byte `+0x11` is the same byte for `FUN_00013040`. Both folds are in [Combat](combat.md). `Item.dat` byte `+0x16` is 0 in all 251 rows. The unsigned short at `+0x13` is the amount a shop adds to or subtracts from the dword at `0x643b8`. Across the file that short runs from 0 to 45000, and 34 rows are 0. Shops are in [Scenario files](scenario.md).

Spawn in `FUN_00023280` fills the bases from these rows and takes its tile from the `COD` record of the same index, in [Scenario files](scenario.md). The 26-byte record is at `DAT_0006013c + index * 0x1a + 0x83`. Byte 0 is the side stored at unit `+6`. Byte `+1` is the character id stored at `+7` and `+8`. Byte `+4` is the multiplier. Byte `+0x15` is the value `FUN_00023800` compares before it will spawn the record. For a character id below `0x3c` the rows are `Friaprda.dat` and `FriLevUp.dat`. Otherwise the row is `EnemyDat.dat` of `id - 0x3c`. The arithmetic below is that function.

```
scale = roster[+4]
if character < 0x3c:
    fri = Friaprda[character]
    lev = FriLevUp[character]
    +0x1f = fri[0]
    +0x20 = fri[1]
    +0x3b = fri[7]
    +0x37 = short(fri + 0x12) + lev[0] * scale
    +0x39 = short(fri + 0x14) + lev[2] * scale
    +0x3e = short(fri + 0x16) + lev[4] * scale
    hp = short(fri + 3) + lev[6] * (scale - 1)
    mp = short(fri + 5) + lev[8] * (scale - 1)
else:
    row = EnemyDat[character - 0x3c]
    +0x1f = row[0]
    +0x20 = row[1]
    +0x37 = row[5] * scale
    +0x39 = row[6] * scale
    +0x3e = row[7] * scale
    hp = short(row + 2) * scale
    mp = row[4] * scale
+0x40 = +0x42 = hp
+0x44 = +0x46 = mp
```

`FUN_00023b90(characterId)` appends one roster record at `DAT_00064108 + DAT_00064114 * 0x50` and then adds 1 to the count. It is the only append. Side is 2, and `+7` and `+8` are the argument. The rows are the same `Friaprda.dat` and `FriLevUp.dat` rows as a spawn whose character id is below `0x3c`, and `+0x21` is byte `+2` of the `Friaprda` row, the scale those formulas multiply by. The first two item pairs are flagged `0x40` with the ids at `Friaprda` `+0xc` and `+0xd`. Each of the next four is flagged `0x80` when the byte at `+0xe` plus the index is `0xff`, and flagged 0 otherwise. It then calls `FUN_00023a90` with the index it just filled. That body was not read. Who calls the append is in [Session](session.md). How far the copy into a battle goes is in [Scenario files](scenario.md).

`FriLevUp.dat` byte 10 selects the `GetMgTab.dat` row used when a level is gained, unless that byte is `0xff`. The five pairs at bytes 0, 2, 4, 6, and 8 are the level-up rolls in [Combat](combat.md). Spawn uses only the first byte of each pair. Bytes `+2` and `+8` through `+0x11` of `Friaprda.dat`, and bytes `+8` and `+9` of `EnemyDat.dat`, were not read.

`RankUp.dat` is 9 rows of 12 bytes, and each row is four triples of 3. `FUN_00034980` selects a triple with `argument * 3`. It stores byte 0 at unit `+7` and byte 1 at unit `+0x20`. `FUN_00034310` compares byte 0 of the row with byte 0 of the selected triple, stores byte 1 at `0x64034`, and stores byte 2 at `0x64038` before the text call at `0x346f6`. The same function stores `row[7] + 1` at `0x64030`. The read at `0x351e1` was not separated. The rest of the 80 bytes is still unmapped.

The six bytes at `+0x22` are counts. Spawn clears them: `push 6`, `push 0`, `push unit + 0x22`, then the call at `0x23715`. `FUN_00028f40(kind, id)` looks the unit up and, when `rand % 100` is below byte `+2` of a `MagicDat.dat` row and the chosen byte is still 0, stores `rand % 2 + 2`. Kind `0x11` chooses `+0x27`, kind `0x12` chooses `+0x25`, and kind `0x13` chooses `+0x26`. Any other kind chooses byte `kind + 0x22` and reads the chance from magic row `0x14`. Kinds `0x11`, `0x12`, and `0x13` also require `FUN_00029050` to return 0. The spell player `FUN_000288c0` calls this with kind `0x11`, with its own argument when that argument is `0x12` or `0x13`, and with 0, 1, and 2 when the argument is `0x14`. The phase tick that counts the bytes down is in [Turns](turns.md).

How those words are combined in an attack is in [Combat](combat.md). How a scenario places the records is in [Scenario files](scenario.md).
