# Scenario files

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`object 1 + 0x127b0` runs off the scenario index in `object 2 + 0x9cf4`. Who calls it, and the per-scenario openers around that load, are in [Session](session.md). The bytes of the files below are the structs in [File formats](formats.md).

| Pattern | Archive | What the code does with it |
| --- | --- | --- |
| `fdetxt%02d.txt` | `FIELD.VFS` | Loaded with index + 1. The table layout is in [Text](text.md). |
| `map%02d.dat` | `FIELD.VFS` | Who stands on the map. Byte 1 is the roster-block count. Byte 2 is the count of 26-byte records at `+0x83`. The tile grid is not in this file. |
| `Shop%02d.dat` | `FIELD.VFS` | One file per scenario index, `SHOP00.DAT` through `SHOP29.DAT`, each 36 bytes. `object 1 + 0x212b0` loads `Shop%02d.dat` for `object 2 + 0x9cf4` into `object 2 + 0x9d80`. |
| `M%02d.dtl` | `FIELD1.VFS` | Magic `DTL`. `M00.DTL` is 4112 bytes: a 16-byte header whose short at `+7` is `0x40`, then `64 * 64` bytes. `object 1 + 0x1b790` stores one of those bytes in `object 2 + 0x9d06`. Script 5, the search on the fourth command corner, and the call at the end of a script read it, in [Turns](turns.md). |
| `dsc%02d.dat` | `FIELD2.VFS` | First dword is the section count. Each section is 8 dwords. The third and fourth are the parallax scale in [Map](map.md), and the low bytes of the seventh and eighth are the paint order and the range highlight. Of 66 sections, 62 are order 9 and highlight 1 (the ground, a fixed recolor), 3 are order 8 and highlight 0 (a slower plate that skips the range), and 1 is order 11 and highlight 2 (painted over the units, blended). `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. |
| `m%02d%d.mpl` | `FIELD1.VFS` | One per section. The pointer is `object 2 + 0x9cb0`, in [Map](map.md). |
| `m%02d%d.cel` | `FIELD1.VFS` | Tile graphics for that section. The pointer is `object 2 + 0x9c20`. |
| `attr%02d%d.dat` | `FIELD2.VFS` | Magic `ATR`. One 4-byte record per tile picture, starting at file offset `0x11`. The pointer is `object 2 + 0x9c98`. See [terrain](map.md). |

`M000.MPL` starts with `MPL`, is 1451 bytes, and stores width 30 and height 24 as little-endian shorts at offsets 7 and 9. An 11-byte header plus `30 * 24 * 2` bytes of cells is 1451, so the cells are 2 bytes. After loading, the game allocates `width * height * 2 + 4`, writes the two dimensions in front, and `object 1 + 0xb20` sets each cell's second byte to `0xff` and masks the first byte with `0x3f`. That runs on a fresh allocation, so it does not copy the MPL. The MPL remains the terrain; this buffer is a separate occupancy layer. Tile pixels are 24×24: the camera coordinates saved to disk are divided by `0x18`, and both map and combat sprites are blitted at 24×24.

A shop file is three groups of 12 bytes. `object 1 + 0x21470(group, dest)` copies bytes from `group * 12` until `0xff` or 12 bytes, each byte widened to a dword item id, and returns the count. Every id in the thirty files is below 251, which is the `Item.dat` row count in [Units](units.md). Sixteen groups are twelve `0` bytes with no `0xff`, so that reader returns twelve ids of 0. One group begins with `0xff` and contributes nothing.

`object 1 + 0x22480(group)` is the list. It returns the chosen id, or −1 on cancel. `object 1 + 0x238f0` calls it, then `object 1 + 0x8b30` on that id. The first byte of that row is the type. A type at most `0x15` makes the credit lookup `object 1 + 0x15110` with group 0, and a greater type makes it group 1. The price starts as the unsigned short at item `+0x13`, and that short is stored at `object 2 + 0x4038`. The confirm is interface string `0x1f6`. `object 2 + 0x4030` is the buyer's `+8` plus 1, and `object 2 + 0x4034` is the equipped id plus `0xc9`. When `object 1 + 0x7980` returns 0, the class can equip the bought id, and that lookup found a pair, the short at `+0x13` of the equipped record found by `object 1 + 0x151d0` is multiplied by 5 and shifted right by 2, and that credit is subtracted from the price. A price above 0 is refused when it is greater than the dword at `object 2 + 0x43b8`. A confirmed pay subtracts the price from that dword at `object 1 + 0x23bad`. A price at or below 0 is negated, and a confirmed pay adds it at `object 1 + 0x23c58`. The same function then gives the item with `object 1 + 0x15cf0`. The three village actions pass the group: `object 1 + 0x255d0` passes 0, `object 1 + 0x25d40` passes 1, and `object 1 + 0x25f80` passes 2. The other corners of those menus are in [Turns](turns.md).

The scenario index is the battle map. `object 1 + 0x12720` passes `object 2 + 0x9cf4` to `object 1 + 0x12bb0`, and that function calls `object 1 + 0x127b0` before it places anyone. Every name in the table above is formatted with that same index. The walkable grid is section 0: `m%02d0.mpl`. Its width and height are the shorts at `+7` and `+9`, `object 1 + 0x127b0` copies those two shorts into the occupancy grid, and each cell is the picture short already described above. A later section is another plate on that visit, drawn as in [Map](map.md). Of indexes 0 through 29, scenarios 5 and 29 add a plate at order 8, and scenario 7 adds the plate at order 11. The other 27 have one section.

The title stores index 0. Winning a scenario stores the next index, and the visit that follows loads that grid. Indexes 0 through 25, 27, and 28 each store their own index plus one. Index 26 stores 27 only on the item check in [Session](session.md); the other path sets quit and leaves the index at 26. Index 29 stores nothing and sets quit. The other writes of `object 2 + 0x9cf4` are opcode 17, at `object 1 + 0x11bf6`, and the save and load copies. Files past index 29 use the same layout. A load of one of those higher indexes is a scene inside a script. The battle that follows an opener is the index the script left behind, which for every `Icon00.dat` through `Icon29.dat` is that file's own number.

Section 0 for indexes 0 through 29:

| Index | Grid | Index | Grid | Index | Grid |
| --- | --- | --- | --- | --- | --- |
| 0 | 30×24 | 10 | 22×24 | 20 | 33×25 |
| 1 | 25×31 | 11 | 15×13 | 21 | 24×25 |
| 2 | 30×20 | 12 | 33×24 | 22 | 33×25 |
| 3 | 24×24 | 13 | 22×24 | 23 | 33×25 |
| 4 | 33×24 | 14 | 29×25 | 24 | 21×23 |
| 5 | 30×12 | 15 | 33×39 | 25 | 19×38 |
| 6 | 26×20 | 16 | 33×25 | 26 | 17×30 |
| 7 | 33×25 | 17 | 33×25 | 27 | 22×25 |
| 8 | 26×24 | 18 | 33×25 | 28 | 26×25 |
| 9 | 20×24 | 19 | 33×25 | 29 | 21×18 |

`MAP##.DAT` says who is on that grid. Byte 0 is 0 in every file. Byte 1 is stored in `object 2 + 0x4118` and is how many unit slots are allocated. Byte 2 is stored in `object 2 + 0x410c` and is how many 26-byte records sit at `+0x83`. Every file is `0x83 + byte 2 * 26` bytes. The saved copy of `0x8a3` bytes is that length at 80 records.

Bytes 3 through `0x32` are sixteen rows of three, read by `object 1 + 0x1de50`. For each row, when byte 0 equals the turn counter `object 2 + 0x9ce8` and byte 2 equals the side argument, it calls the pointer at `object 2 + 0x1c4 + byte 1 * 4` with argument 0. The dwords from `object 2 + 0x1c4` up to the after-action table at `object 2 + 0x28c` are 50 pointers. A row of `255, 255, 0` does not match a turn. The other rows of maps 0 through 29 are turn, handler, side:

| Map | Rows |
| --- | --- |
| 1 | turn 10, handler 3, side 0 |
| 2 | turns 3 through 14, handler 0, side 0; turn 22, handler 5, side 0 |
| 3 | turns 3 and 5, handler 6, side 0 |
| 6 | turn 2, handler 9, side 0 |
| 7 | turns 1, 3, 4, 10, and 12, handler 10, side 0 |
| 8 | turn 15, handler 14, side 0 |
| 9 | turns 3, 6 through 13, and 19, handler 15, side 0 |
| 10 | turns 4 and 7, handler 17, side 0 |
| 13 | turn 6, handler 19, side 2 |
| 15 | turns 5 and 15, handler 23, side 0 |
| 16 | turns 8 and 9, handler 24, side 0 |
| 17 | turns 4 through 11 and 13, handler 25, side 0 |
| 18 | turn 6, handler 26, side 2 |
| 21 | turns 1, 3, 5, 8, and 9, handler 31, side 0 |
| 22 | turns 1 through 5 and 15, handler 34, side 0; turn 7, handler 34, side 2 |
| 23 | turns 5, 8, 10, 13, and 15, handler 36, side 0; turn 7, handler 36, side 2 |
| 25 | turn 4, handler 40, side 0 |
| 27 | turns 2, 4, 6, 7, 10, 12, 14, 16, and 18, handler 44, side 0 |

Maps 0, 4, 5, 11, 12, 14, 19, 20, 24, 26, 28, and 29 have no other row. The call is in [Turns](turns.md). Disassembly of the handlers those rows name, not a decompile. A spawn is `object 1 + 0x13800` with the scenario index, the group below, and 0. A nibble write is the same store as `object 1 + 0x268d0`: the low nibble of unit `+0x34`. A center is `object 1 + 0x1d7e0`. Twelve calls of `object 1 + 0x1bc40` are the redraw. Strings are scenario strings.

| Map | What the handler does |
| --- | --- |
| 1 | Turn 10 writes nibble 0 on slots `0x13` through `0x15`, slot `0x11`, slot `0xd`, and slots 8 and 9. |
| 2 | Turns 3 through 14 spawn group `turn - 1` with the first argument fixed at 2. Turn 3 shows strings `0x13` and `0x14`. Turn 14 shows string `0x15`. Turn 22 shows string `0x17`, spawns group `0xf` with the first argument fixed at 2, and stores outcome 1. |
| 3 | Turn 3 shows string `0x17`. Turn 5 spawns group 5, centers on slot `0x1f`, redraws, shows string `0x18`, and writes nibble 0 on slots `0xf` through `0x12` and slot `0xd`. |
| 6 | Turn 2 writes nibble 0 on slots 4 through 8. |
| 7 | Turn 1 shows string `0xc`. Turn 3 plays `Icon7-1.dat`. Turn 4 plays `Icon7-2.dat` and writes nibble 3 on slot `0xe`. Turn 10 spawns group 2 and shows string `0x15`. Turn 12 spawns group 3 and shows string `0x22`. |
| 8 | Turn 15 spawns group 1 and shows string `0x17`. |
| 9 | Turn 3 spawns group 1 and shows string `0x12`. Turns 6 through 13 spawn group `turn - 4` and call `object 1 + 0x1d550` with `0x48` and `0xd8`, then with `0x168` and `0xd8`, redrawing after each. Turn 19 spawns group `0xb` and shows string `0x13`. |
| 10 | Turn 4 spawns group 5 and shows string `0xf`. Turn 7 spawns group 4, centers on slot `0x34`, redraws, centers on slot `0x2c`, redraws, and shows string `0xf`. |
| 13 | Turn 6, side 2, spawns group 4, centers on slot `0x24`, redraws, centers on slot `0x2a`, redraws, and shows string `0x11`. |
| 15 | Turn 5 writes nibble 0 on slots `0x19` through `0x22`. Turn 15 writes nibble 0 on slots `0xa` through `0x19`. |
| 16 | Turns 8 and 9 spawn a group equal to the turn. |
| 17 | Each named turn spawns a group equal to the turn. |
| 18 | Turn 6, side 2, spawns group 1 and shows string `0xa`. |
| 21 | Turn 1 shows string `0xc` and spawns group 1. Turn 3 shows string `0xd` and spawns group 2. Turn 5 shows string `0xe`, spawns group 3, clears `object 2 + 0x9cd0`, calls `object 1 + 0x1d550` with `0x60` and 0 and then with `0x60` and `0x1b0`, stores 1 back, shows string `0xf`, spawns group 5, and repeats that camera pair, then shows string `0x10`. Turn 8 shows string `0x11`, spawns group 4, and pans through `(0x60, 0)`, `(0x60, 0x1b0)`, and `(0x1f8, 0x1b0)` with the same clear and restore. Turn 9 writes nibble `0xb` on slot `0xb` and nibble 0 on slots `0xc` through `0x41`. |
| 22 | Turns 1 through 5 spawn group `turn + 4`. Turn 3 also shows string `0x15` and spawns group 3. Turn 7, side 2, shows string `0x16` and spawns group 4. Turn 15 writes nibble `0xb` on slot `0x20`. |
| 23 | Turn 5 shows string `0x10` and spawns group 2. Turn 8 shows string `0x11`. Turn 7, side 2, spawns group 6 and shows string `0xe`. Turn 10 spawns group 4 and shows string `0x12`. Turn 13 shows string `0x13` and spawns group 3. Turn 15 shows string `0x14` and spawns group 5. |
| 25 | Turn 4 shows string `0x16` and writes nibble 0 on slots `0x1a` through `0x2d`. |
| 27 | Each named turn spawns group `turn / 2`, clears `object 2 + 0x9cd0`, calls `object 1 + 0x1d550` with 0 and `0x120`, redraws, and stores 1. |

Map 7's first pair, at file offset `0x33`, is handler 12 and second byte 0. No map row names handler 12. When a step stores that first byte into `object 2 + 0x9d90`, in [Turns](turns.md), the handler runs. If `object 2 + 0x40e8` is clear it stores 1, plays `Icon7-3.dat`, writes `0x15` and 4 into unit `0x13`'s `+0x35` and `+0x36`, writes nibble 4 on slots `0xf` through `0x12`, and writes nibble 0 on slot `0x13`.

Handler 21 is `object 1 + 0x278e0`. No row or pair of the map files selects it. The body was disassembled. It calls `object 1 + 0x29b80` first, which stores 0 into `+0x40` of every side-0 unit and runs the death spin. When the turn counter `object 2 + 0x9ce8` is above `0x19`, or `object 1 + 0x9b0(4)` is nonzero, it stores 2 in the outcome `object 2 + 0x9da0` and returns. Otherwise it calls `object 1 + 0x13800` with the scenario index, group 2, and 0. String `0x12` is drawn at `0xa0000`, portrait 3 is `object 1 + 0x10580(3)`, and string `0x13` is drawn at `0xaa44a`. Both strings come from `object 2 + 0x124` with pitch `0x140`, ink `0xd0`, fill 0, and shadow `0x6d`. `object 1 + 0x7980` reads the confirm, and `object 1 + 0x107f0` then dismisses the box, in [Pictures](pictures.md). A return of 0 draws string `0x14` at `0xa0000`, stores 1 into byte `+5` of slots 0, 1, 2, 3, 5, 6, 7, and 8 and of slot `0x34`, and stores 1 into `object 2 + 0x40e8`. Any other return draws string `0x15` at `0xa0000` and stores outcome 2.

Other pairs of maps 0 through 29 name a handler the same way. The second byte is what the step's third argument has to equal, in [Turns](turns.md).

| Map | Pair | What it does |
| --- | --- | --- |
| 2 | DTL 1, handler 1, second byte 0 | When `object 2 + 0x40e8` is clear, stores 1, shows string `0x12`, and calls `object 1 + 0x13800` with 2, group 1, and 0. |
| 2 | DTL 2, handler 4, second byte 0 | When `object 2 + 0x40e9` is clear and the mover's side is not 0, stores 1, shows string `0x16`, and calls `object 1 + 0x13800` with 2, group `0xe`, and 0. |
| 4 | DTL 1, handler 7, second byte 0 | When `object 2 + 0x40e8` is clear, stores 1 and writes nibble 0 on slots 6 through `0x22`. |
| 9 | DTL 1, handler 16, second byte 0 | When `object 2 + 0x40e8` is clear and the mover's side is above 0, stores 1 and spawns group `0xa`. |
| 19 | DTL 1, handler 28, second byte 0 | When the mover is slot 0, the turn is at most `0x14`, and that slot has item `0xa0`, shows string `0x13`, removes the pair, gives id `0xa1`, and rebuilds the combat words. |
| 20 | DTL 1, handler 29, second byte 0 | When `object 2 + 0x40e8` is clear and the mover's side is 2, spawns group 1, shows string `0x14`, and stores 1. |
| 7 | DTL 2, handler 13, second byte 0 | The mover's slot is `0xf` through `0x12`, or it returns. Increments byte `object 2 + 0x40e9` and shows string `slot + 0xd`. When exactly 3 of those four slots are gone and the byte is above 1, a slot below `0x11` shows string `0x20` and any other shows `0x21`, then gives slot `0x13` item `0xc8` when the byte is 2, `0xda` when it is 3, and `0xdd` otherwise. The mover's `+5` is stored as 1. |
| 15 | DTL 1, handler 22, second byte 1 | Slot 0, byte `object 2 + 0x40e8` clear, and the turn at most `0x14`. Portrait `0x81` shows string `0xc`, and the byte is stored as 1. Item `0x58` on slot 0 selects string `0xd`. Item `0x59` selects `0xe`. Neither returns. That string is shown, then string `0xf`, and `object 1 + 0x7980` runs. A nonzero return shows string `0x10`. A 0 return shows `0x11` and `0x12` and removes the pair. Item `0x58` then shows `0x13` and gives `0xa0`. Item `0x59` shows `0x14`, adds `0x1388` to `object 2 + 0x43b8`, shows `0x15`, and asks again: 0 shows `0x16` and gives `0xa9`, and any other return gives `0xa3` and shows `0x10`. Either gift rebuilds slot 0. |
| 18 | DTL 1, handler 27, second byte 0 | Byte `object 2 + 0x40e8` clear and the mover's side not 0. Spawns group 6, pans through (`0x108`, 0), (0, `0x210`), and (`0x300`, `0x210`), shows string `0x13`, and stores 1. |
| 20 | DTL 2, handler 30, second byte 0 | Byte `object 2 + 0x40e9` clear and the mover's side 2. Spawns group 2, shows string `0x15`, stores 1, and writes nibble 0 on slots `0xb` through `0x50`. |
| 22 | DTL 1, handler 35, second byte 1 | Byte `object 2 + 0x40e8` clear, the mover's `+8` equal to 7, and `object 1 + 0x15210` of that slot not 8. Shows string `0x17`, spawns group `0xa`, pans to (`0x2a0`, 0), shows string `0x18`, stores 1 into `+5` of the last slot and redraws, shows string `0x19`, gives id `0xb1` to the mover, and stores 1 into the flag. |
| 24 | DTL 1, handler 37, second byte 0 | Byte `object 2 + 0x40e8` clear and the mover's side 2. Shows string `0x12`, spawns group 1, pans through (0, 0) and (`0x1e0`, `0x108`), shows string `0x13`, writes nibble `0xb` on slots `0xc` through one below the unit count, and stores 1. |
| 24 | DTL 2, handler 38, second byte 1 | Slot 0 carrying item `0xa1`. Shows string `0x14`, removes that pair, gives `0xa2`, and rebuilds. |
| 24 | DTL 3, handler 39, second byte 1 | The mover's `+8` is 5, `object 2 + 0x43b8` is at least `0x7530`, byte `object 2 + 0x40e9` is clear, and the pair count is not 8. Shows string `0x15`, then string `0x16` with portrait `0x77`. `object 1 + 0x7980` returning 0 shows string `0x17`, gives id `0x4a`, and subtracts `0x7530`. Any other return shows string `0x18`. Either return stores 1 into the flag. |
| 25 | DTL 1, handler 41, second byte 0 | Byte `object 2 + 0x40e8` clear and the mover's side 2. Spawns group 2, shows string `0xa`, pans to (`0xf0`, `0x378`), shows string `0xb`, spawns group 3, shows string `0xc`, writes nibble 0 on slots `0xc` through `0x4f`, and stores 1. |
| 28 | DTL 1, handler 45, second byte 0 | The mover's side is 2. Writes nibble 0 on slots `0x24` through `0x59`. |
| 28 | DTL 2, handler 46, second byte 0 | The mover's side is 2. Writes nibble 0 on slots `0xc` through `0x59`, then nibble `0xa` on slots `0x5a` and `0x5b`. |
| 29 | DTL 1, handler 47, second byte 0 | Byte `object 2 + 0x40e8` clear. Spawns group 4, pans through (`0x60`, `0x150`) and (`0x198`, `0x150`), shows string `0x8`, and stores 1. |

A pan clears `object 2 + 0x9cd0`, calls `object 1 + 0x1d550` with the pair as its two arguments, redraws twelve times, and stores the leash as 1 when the pan ends. Bytes `0x33` through `0x52` are sixteen pairs. A nonzero `DTL` byte selects the pair at file offset `0x31 + DTL * 2`, which for values 1 through 16 is this block. The script tail stores the pair's first byte as a handler index when the second byte matches, in [Turns](turns.md). Bytes `0x53` through `0x82` are sixteen triples, one per `DTL` value, and `+0x83` is where the 26-byte records start. The triple's byte and short are what script 5 copies and what the cursor search gives, also in [Turns](turns.md). The 26-byte record is in [Units](units.md).

`object 1 + 0x12bb0` opens `ICON.CEL` (the string at `object 2 + 0x1a03`, mode at `object 2 + 0x1a00`) and loads `map%02d.cod` from `FIELD.VFS` into `object 2 + 0x140`. The file begins `COD`. The short at `+7` equals byte 1 plus byte 2, and the file is `9 + that count * 6` bytes in every pair. Placement does not read that short. It addresses a record at `file + 0x0b + index * 6`. The short at `+0` is x and the short at `+2` is y. The high byte of both is 0 in all 1647 records of indexes 0 through 29, and every one of those coordinates sits inside section 0. `object 1 + 0x12bb0` copies the low bytes onto the unit. The loop runs `i` from 0 up to byte 1. While `i` is also below `object 2 + 0x4114` it copies 80 bytes from `object 2 + 0x4108 + i * 0x50`, then takes the coordinate at index `byte 2 + i`, and stores side 2. A slot at or above `object 2 + 0x4114` is zeroed and gets flag bit 0 set. The roster count is how many of those records are filled. It grows only in `object 1 + 0x13b90`, which the scenario openers call, and it is restored from a save or cleared at the title. Nothing else stores it, and nothing swaps two roster records. The characters who fight are therefore the prefix of the roster, in the order they were appended, cut off at byte 1. A character appended once the count already equals byte 1 is not copied. Which opener appends which id is in [Session](session.md).

`object 1 + 0x13800(scenario, group, arg)` opens `ICON.CEL` and loads `map%02d.cod` from `FIELD.VFS` into `object 2 + 0x140` through `object 1 + 0x193d0`. It walks the 26-byte records and calls `object 1 + 0x13280(index, icon, arg)` when byte `+0x15` equals `group`. It then frees the `COD` member, the archive, and the icon file, and stores 0 at `object 2 + 0x140`. The load calls it as `(scenario, 0, 1)`, so group 0 is on the map before the icon script. That spawn reads the same COD slot as the record's own index, and it loads x and y as the signed shorts. Across indexes 0 through 29, byte `+0x15` is 0 through 15, or `0xff` in 18 records. Byte 0 of the record is the side copied to unit `+6`, and byte `+1` is the character id copied to `+7` and `+8`. Across the 63 `MAP` files, indexes 0–64 except 30 and 33, that byte is a character id from 0 through 156. The shorts are read from two bytes after the record's id. On every actor that id equals byte `+1`, and the reinforcement records store 0. Placement does not read the id or header byte 4. The record layout is in [File formats](formats.md). The 80-byte unit those calls fill is in [Units](units.md).

`object 1 + 0x11620` is the icon script, one file `Icon##.dat` inside `IconAni.vfs`, named from the opener's argument. It walks opcodes until byte 0. The ones read here:

| Opcode | Advance | What it does |
| --- | --- | --- |
| 1 | 4, plus 2 per unit | `object 1 + 0x11f30`. Byte +1 is how many times each of six frames is redrawn. Byte +2 is how many of those passes run. Byte +3 is the unit count. On the sixth frame of each pass the named units move one tile along the facing in the pair. |
| 2 | 3, plus 2 per unit | `object 1 + 0x120d0`. The unit count is the second byte. The first byte is how many times the map is redrawn afterwards. Stores a facing on each named unit. |
| 3 | 2 | Shows the text id in the next byte, from the scenario text block. The walk and the pen are in [Text](text.md). |
| 4 | 3 | Spawns a group. The next byte is the group, or `0xff` to use the value opcode 99 stored. The byte after that is the third argument of `object 1 + 0x13800`. |
| 6 | 2 | Opens `Icon%04d.saf` from `IconAni.vfs` through `object 1 + 0x193d0` and plays it with `object 1 + 0x12290`. The number is the next byte. Every frame is shown for its hold, in [Pictures](pictures.md). The member is freed after the clip. |
| 7 | 2 | `object 1 + 0x20960` on the next byte, or on `-1` when that byte is `0xff`. |
| 8 | 2 | Formats `Icon%04d.wav` from the next byte. While fewer than `0x14` of these are open, `object 1 + 0x193d0` opens it from `IconAni.vfs` and `object 1 + 0x20790` starts it with arguments 1, −1, −1. The pointers are freed when the script ends. |
| 9 | 2, plus 1 per slot | The next byte is the slot count. Stores 0 into `object 2 + 0x9cd0` and `object 2 + 0x159`. For steps 1 through 7, stores the low bit of the step into `+5` of each named slot and calls `object 1 + 0x1bc40` three times. Then stores 1 into both bytes. |
| 10 | 5 | Writes x, y, and facing onto the unit named by the next byte, when that index is below the slot count. |
| 11 | 2 | Sets flag bit 0 on that unit. |
| 12 | 2 | Clears flag bit 0 and the six count bytes at `+0x22`. |
| 13 | 3 | Moves the camera and the cursor to the tile in the next two bytes, times 24. |
| 16 | 3, plus 2 per step | `object 1 + 0x124c0`. Byte +1 is how many times each step redraws. Byte +2 is the step count. Adds each signed pair to the camera, redraws, then writes the camera back to the values from entry. |
| 17 | 2 | Stores the next byte as the scenario index and calls `object 1 + 0x12720`, which loads that index's map. The script then continues. |
| 18 | 4 | Writes the third byte into the unit's count byte at `+0x25` plus the second byte. |
| 19 | 3 | Stores the second byte into `object 2 + 0x40d8` at the first byte, then calls `object 1 + 0x1e6a0`. |
| 20 | 5 | Writes the short at the third byte into the section-0 cell at the first two bytes. |
| 21 | 4 | `object 1 + 0x12f10` with the next three bytes. |
| 97 | 1 | Ten times, stores 99 and calls `object 1 + 0xdd00(3)`, then calls `object 1 + 0x13950`. |
| 98 | 3 | `object 1 + 0x10` with the next two bytes. |
| 99 | 1 | `object 1 + 0x125d0`. Two yes-or-no questions. Returns 1, 2, or 3, which a later opcode 4 can use as the group. |

Opcode 0, and any other byte, ends the script. Every `.dat` member of `IconAni.vfs` walks to a final 0 with the lengths above. Handler 0, at `object 1 + 0x26920`, is the map 2 row in the table above. The archive directory is in [Archives](archives.md).

Opcode 5 calls `object 1 + 0x11e00` with the script base and the cursor. The next two bytes are a tile. It steps `object 2 + 0x9ce4` and `object 2 + 0x9ce0` from the current camera toward that tile times 24. The step count is the larger absolute delta divided by 24, and each step adds the two deltas divided by that count, then redraws. A zero count skips the loop. It then stores the target plus 24 into the cursor, `object 2 + 0x9cd4` and `object 2 + 0x9ccc`, and snaps the camera to the target. The cursor advances by 3.

Opcode 14 calls `object 1 + 0x123e0` with the next byte, then advances 2. The byte is the wait passed to `object 1 + 0x2d0e0`. The fade walks a bias from 0 through `0x3c` in steps of 4. Each step waits until bit 3 of `object 1 + 0x2d254(0x3da)` is set, the vertical retrace in [Pictures](pictures.md), then `object 1 + 0x12f10` writes palette indexes 0 through 255 from `object 2 + 0x43cc` with that bias negated on every channel. Opcode 15 is the same walk from `0x40` down to 0, so the bias runs from −64 back to 0.

Opcode 97's call of `object 1 + 0x13950` writes the battle back onto the roster. The body is in [Session](session.md).

Opcode 17 is a scene change inside the script. The opener for index n passes `Icon%02d.dat`. These opener scripts reload another index and then store their own index again, so the battle stays on n:

| Script | Indexes, in order |
| --- | --- |
| `Icon00.dat` | 32, 34, 35, 0 |
| `Icon06.dat` | 47, 6 |
| `Icon07.dat` | 48, 7 |
| `Icon08.dat` | 54, 55, 8 |
| `Icon09.dat` | 37, 38, 9 |
| `Icon11.dat` | 52, 40, 11 |
| `Icon19.dat` | 58, 19 |
| `Icon24.dat` | 56, 24 |
| `Icon29.dat` | 29 |

The instructions in `Icon00.dat` are in [Opening](opening.md). The other `Icon00.dat` through `Icon29.dat` contain no opcode 17. `Icon7-1.dat`, `Icon7-2.dat`, and `Icon7-3.dat` also contain none. Map 7's handler plays the first two, and handler 12 plays the third, in the table above.

The ending plays its `Win` script before it stores the successor, so the last index in that script is not the next battle. The sequences are `Win00.dat` 36, 41, 42, 43; `Win03.dat` 39; `Win05.dat` 46; `Win08.dat` 57; `Win09.dat` 37; `Win11.dat` 53; `Win16.dat` 60; `Win17.dat` and `Win17-1.dat` 45 then 17; `Win18.dat` 44; `Win20.dat` 51 then 20; `Win22.dat` 50; `Win24.dat` 59, 3, 47, 51, 22, 59; `Win26.dat` 62 then 26; `WinGA26.dat` 61; `Win29.dat` 63 then 29. `GoodEnd.dat` stores 64. The other `Win` files contain no opcode 17. What the ending stores afterwards is in [Session](session.md).
