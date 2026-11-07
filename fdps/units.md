# Unit record

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`object 1 + 0x1cfa0` returns `object 2 + 0x9cd8 + id * 0x50`. The array is allocated to `count * 0x50`. Count lives in `object 2 + 0x150`. `object 1 + 0x13920(index)` returns the roster record at `object 2 + 0x4108 + index * 0x50`. `object 1 + 0x212b0` frees the battle array when the count is nonzero and the pointer is not the roster, then stores the roster count into `object 2 + 0x150` and the roster base into `object 2 + 0x9cd8`.

Bytes filled by the spawners `object 1 + 0x13280` and `object 1 + 0x12bb0`, and read by the map drawer and the combat players:

| Offset | Role |
| --- | --- |
| `+0`, `+1` | Tile x, y. `object 1 + 0x1b790` reads the map cell there. Backdrop, terrain, and the detail byte all come from that query. |
| `+2` | Slot in the loaded `ICON.CEL` cache. `object 1 + 0x13020` returns it. |
| `+3` | Facing, 0..3. See [map sprites](pictures.md#map-sprites). |
| `+4` | Sub-tile progress. The drawer multiplies it by a per-facing pixel step. |
| `+5` | Flags. Bit 0: map drawer skips the unit. Bit `0x80`: map sprite locks to the middle walk frame and uses expander mode 11, and the system menu treats the unit as eligible when bit 0 is clear. `object 1 + 0x19b0` ORs in bit `0x80` when an action is committed. A unit whose pool at `+0x40` is 0 is stored as `1` by the destruction sequence, so bit 0 is set and bit `0x80` is cleared. |
| `+6` | Side. `0` selects the `"E"` spell prefix and one mirror sign; any other value selects `"M"`. A roster copy stores `2`. A scenario spawn copies byte 0 of its 26-byte record, which is 0, 1, or 2. The cursor commands side `2`. The two phase walks use side `0` and side `1`. |
| `+7` | Character id. Indexes `STAND`, `ACT`, `MAGIC`, the twelve `ICON.CEL` frames, and the `FACE.CEL` portrait of the same number. Which of those files are present, and which ids share one sheet, is in [Pictures](pictures.md). `0x80` means "no sprite" on the map. |
| `+8` | The same character id as `+7` at spawn and at append. Promotion reads it to index `RankUp` and does not write it, so it stays the id the record was given. The new id is stored at `+7`. The roster name, `object 1 + 0x1d9b0`, and the roster match in `object 1 + 0x13950` read this byte. The move compares it with 3 and with 7 at `object 1 + 0x5641` and `object 1 + 0x5651`. The local stored at `object 1 + 0x5658` is not read, and both results reach the same call. |
| `+9` | Stored as 0 by the spawn `object 1 + 0x13280` and by the append `object 1 + 0x13b90`. No later read of this unit byte was found. |
| `+0x1a` | First byte of the learned-id bits. `object 1 + 0x18280(unit, id)` sets bit `id % 8` of byte `+0x1a + id / 8`. The masks are `01 02 04 08 10 20 40 80` at `object 1 + 0x17630`. |
| `+0x1b` through `+0x1e` | The next learned-id bytes. `MagicDat.dat` has 40 rows, so ids 32 through 39 land in `+0x1e`. Spawn copies four bytes of the actor at `+0x0d` onto `+0x1a`, and copies actor byte `+0x19` onto `+0x1e`. |
| `+0x1f` | Byte 0 of the `Friaprda.dat` or `EnemyDat.dat` row, copied by spawn. `object 1 + 0x62f0` draws interface string `value + 0x97`. |
| `+0x20` | Class. Byte 1 of that same row. `object 1 + 0x8b60` returns `object 2 + 0x3fd0 + (class + 1) * 10`, a row of `ProMap.dat`. |
| `+0x21` | Byte used as the divisor of the experience term in `object 1 + 0xc4f0`. `object 1 + 0xdd00` adds 1 when the byte at `+0x3c` crosses 100. |
| `+0x22`, `+0x23` | Counts. While nonzero, the rebuild multiplies attack, or defense, by the double `1.15` at `object 2 + 0x1b1c` and `object 2 + 0x1b24`, then `object 1 + 0x2d25c` rounds toward zero. `object 1 + 0x62f0` writes 1 to `object 2 + 0xc` when the byte is nonzero. |
| `+0x24` | Count. While nonzero, the rebuild adds `0x0f` to the hit base before equipped items are added. |
| `+0x25` | Count. A weapon whose byte `+9` is `4` writes `rand % 4 + 2`. Regeneration skips the unit while this is nonzero, and the phase tick below subtracts a tenth of `+0x42` from `+0x40`. |
| `+0x26` | Count. Nonzero freezes the map sprite on frame 0 of its facing and jitters x by one pixel. A weapon whose byte `+9` is `1` writes `rand % 2 + 2`. The cursor will not command the unit while it is nonzero. |
| `+0x27` | Count. Nonzero makes menu slot 1 refuse, and the spell scorer returns without a candidate. |
| `+0x28` through `+0x30` | Nine bytes between the counts and the three bytes at `+0x31`. No instruction below `object 1 + 0x33000` uses a displacement in that range on a unit pointer. The one `[eax + 0x2a]` in that part of the image is the frame-count short of a clip header, in `object 1 + 0x42d0`, which the blit `object 1 + 0x4140` calls. The save copies these bytes with the rest of the `0x50` record, in [Save](save.md). |
| `+0x31` | Three bytes. Spawn sets the first to `0xff`. When the pool at `+0x40` is below 1 and bit 0 of `+5` is clear, `object 1 + 0x16150` copies all three into the list that `object 1 + 0xd960` walks. What the first byte selects is in [Combat](combat.md). |
| `+0x34` | Low nibble selects the phase script in [Turns](turns.md). Bit `0x40` makes a tied score prefer the swing. Bit 0, which an odd nibble already has set, doubles the pool-fraction spell score. Bit `0x80` triples the pool-fraction item score. Bytes `+0x35` and `+0x36` are that script's tile arguments. |
| `+0x3b` | Move budget, in tiles. The flood fill stops when the accumulated cost would pass it. |
| `+0x3c` | Byte added to the experience term. At 100 it is reduced by 100 and `+0x21` increases by 1. |
| `+0x3d` | Index script 5 reads, into `object 2 + 0x40d8` and into the three-byte rows at `object 2 + 0x13c`. |
| `+0x40` | Word reduced by the damage formula. At spawn it is copied from `+0x42`. Inferred to be current hit points: the bar and both attack paths treat it as the pool that reaches 0. |
| `+0x42` | Maximum of that pool. |
| `+0x44`, `+0x46` | Second current/max pair. Spawn copies `+0x46` into `+0x44` beside the copy of `+0x42` into `+0x40`, at `object 1 + 0x12d90`. Endings 18 and 23 make the same pair of copies, and clear byte `+5`, when `object 2 + 0x40e9` is set and the character id is at most `0xb`. The addresses are `object 1 + 0x2ae8f` and `object 1 + 0x2b3df`, in [Session](session.md). The spell scorer skips a spell whose row byte `+5` is above `+0x44`. A cast subtracts that byte: `object 1 + 0x18590` does it for the fight player `object 1 + 0xa4a0`, and `object 1 + 0x188c0` does the same store at `object 1 + 0x18942`. The subtraction does not clamp. `object 1 + 0x17570` adds to `+0x44` and caps it at `+0x46`. The rest at the start of `object 1 + 0xe3c0` adds to `+0x40`, not to this pair. Inferred to be a second pool. |
| `+0x48` | Attack word, read by `object 1 + 0xc4f0` and `object 1 + 0x9f60`. |
| `+0x4a` | Defense word. |
| `+0x4c` | Hit word. A roll of `rand % 100` lands when it is below this minus the defender's `+0x4e`. |
| `+0x4e` | Word subtracted from the attacker's hit word. |

`+0x37`, `+0x39`, `+0x3b`, `+0x3e` are filled from class tables (`object 1 + 0x8aa0` / `object 1 + 0x8ad0` below id `0x3c`, else `object 1 + 0x8b00`). `object 1 + 0x14d40` rebuilds the four combat words from those bases and from every equipped item. The arithmetic below is that function. `Item.dat` is the table at `object 2 + 0x3fe0`, one record per id, stride `0x17`, from `object 1 + 0x8b30`.

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

`trunc` is `object 1 + 0x2d25c`, which rounds toward zero. The two `1.15` values are the doubles at `object 2 + 0x1b1c` and `object 2 + 0x1b24`.

Eight item pairs start at `+0x0a`. Pair `i` is the flag byte at `+0x0a + i * 2` and the id at `+0x0b + i * 2`. Bit `0x80` of the flag marks an empty pair. Bit `0x40` marks the pair equipped. `object 1 + 0x15cf0` writes an id into the first empty pair and clears bit `0x80`. It returns −1 when all eight are full. `object 1 + 0x15c90` slides the later pairs down over the removed index and stores `0x80` at `+0x18`.

The first byte of the item record is the type. `object 1 + 0x16040` keeps one equipped item in each group. A type below `0x16` clears other equipped items below `0x16`. A type at or above `0x16` clears other equipped items at or above `0x16`. A type of 0 clears nothing. The chosen flag is then stored as `0x40`. `object 1 + 0x15110(unit, 0)` returns the first equipped pair whose type is from 1 through `0x15`. `object 1 + 0x15110(unit, 1)` returns the first whose type is from `0x16` through `0x27`. The attack paths call it with 0. `object 1 + 0x238f0` passes 0 when the bought item's type is at most `0x15`, and 1 when the type is greater. That call is the credit in [Scenario files](scenario.md), not a use. Across the 251 rows of `Item.dat`, every type from `0x16` through `0x27` has byte `+0x0d` equal to 0. The carried-item action requires that byte to be nonzero, in [Combat](combat.md), so none of those rows is used. A class may equip a type when one of six bytes in its `ProEqu.dat` row equals that type. `object 1 + 0x8b90` returns `object 2 + 0x3fe4 + class * 6`, and `object 1 + 0x8920` loads `ProEqu.dat` there. How a use changes the pools is in [Combat](combat.md). A level raises the bases and both maximums, in [Combat](combat.md). `object 1 + 0x193d0(archive, name, dest)` stores the pointer `object 1 + 0x29940(name, archive)` returns. A null pointer calls `object 1 + 0x46510` and `object 1 + 0x32b7f(1)`. It does not read the rows. `object 1 + 0x8920` is the call that passes the nine names, each a member of `MISC.VFS`, and the pointer each one is stored in: `object 2 + 0x3fd8` for `Friaprda.dat`, `object 2 + 0x3fec` for `FriLevUp.dat`, `object 2 + 0x3fe0` for `Item.dat`, `object 2 + 0x3fd4` for `EnemyDat.dat`, `object 2 + 0x3fd0` for `ProMap.dat`, `object 2 + 0x3fe4` for `ProEqu.dat`, `object 2 + 0x3ff0` for `MagicDat.dat`, `object 2 + 0x3fe8` for `GetMgTab.dat`, and `object 2 + 0x3fdc` for `RankUp.dat`. The stride is the multiplier in the index function, and the row count is the file length divided by that stride. Every row ends at or before the end of the file.

| File | Index | Stride | Rows |
| --- | --- | --- | --- |
| `Friaprda.dat` | `object 1 + 0x8aa0(character)` | `0x18` | 60 |
| `FriLevUp.dat` | `object 1 + 0x8ad0(character)` | `0x0b` | 60 |
| `EnemyDat.dat` | `object 1 + 0x8b00(character - 0x3c)` | `0x0a` | 91 |
| `Item.dat` | `object 1 + 0x8b30(id)` | `0x17` | 251 |
| `ProMap.dat` | `object 1 + 0x8b60(class + 1)` | `0x0a` | 41 |
| `ProEqu.dat` | `object 1 + 0x8b90(class)` | 6 | 36 |
| `MagicDat.dat` | `object 1 + 0x8bc0(id)` | 7 | 40 |
| `GetMgTab.dat` | `object 1 + 0x8bf0(index)` | `0x0c` | 60 |
| `RankUp.dat` | `object 1 + 0x8c20(index)` | `0x0c` | 9 |

`ProMap.dat` has 41 rows because the callers pass `class + 1`. Class 0 reads the second row, and class 39 reads the last. `MagicDat.dat` byte `+6` is the side `object 1 + 0x3420` passes to the target list, and `Item.dat` byte `+0x11` is the same byte for `object 1 + 0x3040`. Both folds are in [Combat](combat.md). `Item.dat` byte `+0x16` is 0 in all 251 rows. The unsigned short at `+0x13` is the amount a shop adds to or subtracts from the dword at `object 2 + 0x43b8`. A sale adds that short times 3, shifted right by 2, in [Turns](turns.md). The item row draws the short at `+1` for types 1 through `0x15`, the short at `+5` for other types below `0x28`, and the short at `+0x0e` when byte `+0x0d` is `0x0b` or `0x0c`. Across the file that short runs from 0 to 45000, and 34 rows are 0. Shops are in [Scenario files](scenario.md).

Spawn in `object 1 + 0x13280` fills the bases from these rows and takes its tile from the `COD` record of the same index, in [Scenario files](scenario.md). The 26-byte record is at `object 2 + 0x13c + index * 0x1a + 0x83`. Byte 0 is the side stored at unit `+6`. Byte `+1` is the character id stored at `+7` and `+8`. Unit `+9` is stored as 0. Byte `+4` is the multiplier. Byte `+0x15` is the value `object 1 + 0x13800` compares before it will spawn the record. For a character id below `0x3c` the rows are `Friaprda.dat` and `FriLevUp.dat`. Otherwise the row is `EnemyDat.dat` of `id - 0x3c`. The arithmetic below is that function.

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
    +0x3b = row[8]
    hp = short(row + 2) * scale
    mp = row[4] * scale
+0x40 = +0x42 = hp
+0x44 = +0x46 = mp
```

`object 1 + 0x13b90(characterId)` appends one roster record at `object 2 + 0x4108 + object 2 + 0x4114 * 0x50` and then adds 1 to the count. It is the only append. Side is 2, `+7` and `+8` are the argument, and `+9` is 0. The rows are the same `Friaprda.dat` and `FriLevUp.dat` rows as a spawn whose character id is below `0x3c`, and `+0x21` is byte `+2` of the `Friaprda` row, the scale those formulas multiply by. The first two item pairs are flagged `0x40` with the ids at `Friaprda` `+0xc` and `+0xd`. Each of the next four is flagged `0x80` when the byte at `+0xe` plus the index is `0xff`, and flagged 0 otherwise. Four bytes at `+8` are copied to `+0x1a`. It then calls `object 1 + 0x13a90` with the index it just filled. That function starts from `+0x37`, `+0x39`, and `+0x3e`, and for each of the eight pairs whose flag has bit `0x40` it adds the item shorts at `+1`, `+5`, `+3`, and `+7` to attack, defense, hit, and avoid. It stores those four sums at `+0x48`, `+0x4a`, `+0x4c`, and `+0x4e`. It does not apply the `+0x22`, `+0x23`, or `+0x24` terms that `object 1 + 0x14d40` does. Who calls the append is in [Session](session.md). How far the copy into a battle goes is in [Scenario files](scenario.md).

`FriLevUp.dat` byte 10 selects the `GetMgTab.dat` row used when a level is gained, unless that byte is `0xff`. The five pairs at bytes 0, 2, 4, 6, and 8 are the level-up rolls in [Combat](combat.md). Spawn uses only the first byte of each pair.

The same spawn copies the rest of the 26-byte actor record. Byte `+5` is the first equipped id, and byte `+6` is the second, unless byte `+5` is `0xff`: then the first pair is byte `+6` and the second pair is empty. Bytes `+7` through `+0xc` are the other six ids, and `0xff` sets the empty flag. Four bytes at `+0x0d` are copied to unit `+0x1a`. Byte `+0x11` is the phase byte at `+0x34`, and `+0x12` and `+0x13` are its tile arguments. Byte `+0x14` is `+0x3d`. Byte `+0x16` and the short at `+0x17` are the three bytes at `+0x31`. Byte `+0x19` is copied to `+0x1e`. Bytes `+2` and `+3` are not loaded. Across the 63 map files, 1676 records, byte `+2` is 0 in every record. Byte `+3` is 0 except fourteen records of map 18, indexes 45 through 58, where it is 18. Those fourteen are side 0, character id 96, scale 17, group 6. That record is `MapActor` in [File formats](formats.md). The item row is the struct below.

```
struct Item {                /* object 1 + 0x8b30, 251 rows of 0x17 */
    uint8_t type;            /* +0  below 0x16 is one equip group, 0x16 through 0x27 is the other */
    uint16_t attack;         /* +1  added when the pair is equipped. Drawn for types 1 through 0x15 */
    uint16_t hit;            /* +3 */
    uint16_t defense;        /* +5  drawn for the other types below 0x28 */
    uint16_t avoid;          /* +7 */
    uint8_t swing;           /* +9  1 writes +0x26, 4 writes +0x25, 2 plays a second swing. Status counts */
    uint8_t at_0x0a;         /* not read */
    uint8_t inner;           /* +0x0b the swing's inner radius */
    uint8_t shape;           /* +0x0c the swing's target shape */
    uint8_t kind;            /* +0x0d a use. 0 means the row is not used */
    uint16_t amount;         /* +0x0e passed to the use. Also the number drawn for kinds 0x0b and 0x0c */
    uint8_t range;           /* +0x10 below 0x10 is a radius, at or above is a line */
    uint8_t cpu_side;        /* +0x11 the side object 1 + 0x3040 passes to the list */
    uint8_t use_shape;       /* +0x12 the use's target shape. The aim leash is this plus 2 */
    uint16_t price;          /* +0x13 what a shop adds or subtracts */
    uint8_t menu_side;       /* +0x15 the side the player's item menu passes to the list */
    uint8_t at_0x16;         /* +0x16  0 in all 251 rows */
};

struct Friaprda {            /* object 1 + 0x8aa0, 60 rows of 0x18 */
    uint8_t  kind;           /* +0  -> unit +0x1f. Inferred. The status window draws string value + 0x97 */
    uint8_t  class_id;       /* +1  -> unit +0x20. ProMap row is class_id + 1 */
    uint8_t  scale;          /* +2  -> unit +0x21 on a roster append */
    uint16_t hp;             /* +3 */
    uint16_t mp;             /* +5 */
    uint8_t  move;           /* +7  -> unit +0x3b */
    uint8_t  spells[4];      /* +8  -> unit +0x1a on a roster append */
    uint8_t  items[6];       /* +0x0c. 0xff marks an empty pair */
    uint16_t attack;         /* +0x12 */
    uint16_t defense;        /* +0x14 */
    uint16_t hit;            /* +0x16 */
};

struct EnemyDat {            /* object 1 + 0x8b00, 91 rows of 0x0a */
    uint8_t  kind;           /* +0  -> unit +0x1f */
    uint8_t  class_id;       /* +1  -> unit +0x20 */
    uint16_t hp;             /* +2  times the actor scale */
    uint8_t  mp;             /* +4  times the actor scale */
    uint8_t  attack;         /* +5  times the actor scale */
    uint8_t  defense;        /* +6  times the actor scale */
    uint8_t  hit;            /* +7  times the actor scale */
    uint8_t  move;           /* +8  -> unit +0x3b, not scaled */
    uint8_t  experience;     /* +9  the term in Combat */
};

struct ProMap {              /* object 1 + 0x8b60(class_id + 1), 41 rows of 0x0a */
    uint8_t move_cost[8];    /* +0  indexed by the terrain byte. 1, 2, or 255 */
    uint8_t crit;            /* +8  the crit roll in Combat */
    uint8_t spell_scale;     /* +9  percent. Positive spell power is multiplied by it */
};

struct MagicDat {            /* object 1 + 0x8bc0, 40 rows of 7 */
    int16_t power;           /* +0  signed. The amount is in Combat */
    uint8_t chance;          /* +2 */
    uint8_t budget;          /* +3 */
    uint8_t shape;           /* +4 */
    uint8_t cost;            /* +5  subtracted from unit +0x44 */
    uint8_t side;            /* +6 */
};

struct RankChoice {          /* one triple of a RankUp.dat row */
    uint8_t character_id;    /* object 1 + 0x24980 stores this at unit +7 */
    uint8_t class_id;        /* stored at unit +0x20 */
    uint8_t third;           /* object 1 + 0x24310 stores this at object 2 + 0x4038. Not copied onto the unit */
};

struct RankUp {              /* object 1 + 0x8c20, 9 rows. Index is the character id */
    RankChoice choice[4];
};
```

The flood fill indexes a `ProMap` row by the terrain byte, so byte 8 is also the cost of terrain 8 and byte 9 is also the cost of terrain 9. The attribute files use terrains 0, 1, 2, 5, and 6, in [Map](map.md).

`RankUp.dat` is those 9 rows, so the index runs through character ids 0 through 8. `object 1 + 0x25030`, called from the rank window at `object 1 + 0x244b5`, reads `RankUp` of unit byte `+8` at `object 1 + 0x251e1`. The triple index comes from the caller's array, and the window draws interface string `choice.class_id + 0xa1`. `object 1 + 0x24980` selects its triple with `argument * 3`. It indexes the table with unit `+8` and does not write that byte. Byte 0 of the chosen triple is stored at `+7`, and byte 1 at `+0x20`. `object 1 + 0x24310` compares byte 0 of the row with byte 0 of the selected triple, stores byte 1 at `object 2 + 0x4034`, and stores byte 2 at `object 2 + 0x4038` before the text call at `object 1 + 0x246f6`. The same function stores `row[7] + 1` at `object 2 + 0x4030`. A roster record is eligible when `+0x21` is at least `0x14` and `+7` is below 9. Character id 0 carrying item `0xdb` is marked 3. Item `0xe0` marks 1, item `0xe1` marks 2, and neither marks 0. A count of 0 shows interface string `0x214` and returns. Accepting removes the marking item, adds the stored byte 2 to `+0x3b`, and adds bytes 1, 3, 5, 7, and 9 of `FriLevUp` for the chosen character id to `+0x37`, `+0x39`, `+0x3e`, both hp words, and both mp words. It stores 1 in `+0x21` and calls `object 1 + 0x14d40`.

## Status counts

A status is a countdown on the unit. The six bytes at `+0x22` through `+0x27` are those countdowns. Zero is off. Any other value is how many phase changes are left. Spawn writes zero over all six: `push 6`, `push 0`, `push unit + 0x22`, then the call at `object 1 + 0x13715`. A scenario can store a count itself. The first battle's opener writes `0xb` into slot 2's `+0x25` and 100 into its hit points, in [Opening](opening.md).

On a phase change, `object 1 + 0xfa00` in [Turns](turns.md) does two things, in this order. While `+0x25` is nonzero it sets hit points to `max(0, +0x40 − +0x42 / 10)`. Then every nonzero byte from `+0x22` through `+0x27` drops by one, and a byte that reaches zero is followed by the combat-word rebuild `object 1 + 0x14d40`.

| Byte | While it is nonzero |
| --- | --- |
| `+0x22` | The rebuild multiplies attack by 1.15 |
| `+0x23` | The rebuild multiplies defense by 1.15 |
| `+0x24` | The rebuild adds 15 to hit and to avoid |
| `+0x25` | Poison. Each phase takes a tenth of maximum hit points, as above. Regeneration and rest both skip the unit |
| `+0x26` | The map sprite stays on frame 0 of its facing and jitters one pixel. The cursor will not command the unit |
| `+0x27` | The spell command is refused, and the spell scorer skips the unit |

The mark under the sprite is `ICONSTS.CEL`, in [Pictures](pictures.md). Five pictures are tried, in the order `+0x23`, `+0x22`, `+0x24`, `+0x25`, `+0x27`, so poison is picture 3. `+0x26` has no picture. A byte of zero is skipped. When more than one of the five is set, the tick modulo that count picks which mark is drawn. The mark is 24×11 and sits 12 rows below the sprite.

A weapon, a spell, or a use selects one of these bytes by a number in its row. The id tables, with an estimated name on each row, are in [Combat](combat.md).

`Item.swing`, byte `+9` of `Item.dat`, is the weapon's choice. Value 4 writes `+0x25`. Value 1 writes `+0x26`. Value 2 plays a second swing and writes no count. The damage formula in [Combat](combat.md) rolls `rand % 100` against `arg` before the write, and skips the write when `object 1 + 0x19050` returns 1. That return is 1 for class `0x19`, `0x21`, `0x22`, `0x24`, `0x25`, or `0x26`, and for a character id from `0x3c` through `0x44`. A poison write stores `rand % 4 + 2`, so the count is 2, 3, 4, or 5. A `+0x26` write stores `rand % 2 + 2`, so the count is 2 or 3. Which field supplies `arg` is not named in that formula.

A spell selects the byte by its id. `object 1 + 0x18f40(kind, id)` reads `MagicDat.chance` of that row. When `rand % 100` is below that chance and the chosen byte is still 0, it stores `rand % 2 + 2`. Kind `0x12` chooses `+0x25`, kind `0x13` chooses `+0x26`, and kind `0x11` chooses `+0x27`. Any other kind chooses byte `kind + 0x22` and reads the chance from magic row `0x14`. Kinds `0x11`, `0x12`, and `0x13` also require `object 1 + 0x19050` to return 0, the same immunity as the weapon. The spell player calls this with kind `0x11`, with its own id when that id is `0x12` or `0x13`, and with 0, 1, and 2 when the id is `0x14`. Spell `0x14` is therefore the three rebuild counts, and its chance is row `0x14` rather than its own row. Spell `0x0d` is a separate roll: each of `+0x25`, `+0x26`, and `+0x27` is set to `rand % 2 + 2` when `rand % 100` is below `0x14` and the same immunity check returns 0. Spell `0x18` stores 0 in those three bytes.

A carried item clears one countdown and is consumed. Use kind `0x16` clears `+0x25`. Use kind `0x18` clears `+0x26`. Both play `Cure.saf`. The kind is `Item.kind`, byte `+0x0d`, and the table of uses is in [Combat](combat.md).

How the combat words are combined in an attack is in [Combat](combat.md). How a scenario places the records is in [Scenario files](scenario.md).
