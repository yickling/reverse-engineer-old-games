# Scenario files

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_000227b0` runs off the scenario index in `DAT_00069cf4`. Who calls it, and the per-scenario openers around that load, are in [Session](session.md).

| Pattern | Archive | What the code does with it |
| --- | --- | --- |
| `fdetxt%02d.txt` | `FIELD.VFS` | Loaded with index + 1. The table layout is in [Text](text.md). |
| `map%02d.dat` | `FIELD.VFS` | Who stands on the map. Byte 1 is the roster-block count. Byte 2 is the count of 26-byte records at `+0x83`. The tile grid is not in this file. |
| `Shop%02d.dat` | `FIELD.VFS` | One file per scenario index, `SHOP00.DAT` through `SHOP29.DAT`, each 36 bytes. `FUN_000312b0` loads `Shop%02d.dat` for `DAT_00069cf4` into `DAT_00069d80`. |
| `M%02d.dtl` | `FIELD1.VFS` | Magic `DTL`. `M00.DTL` is 4112 bytes: a 16-byte header whose short at `+7` is `0x40`, then `64 * 64` bytes. `FUN_0002b790` stores one of those bytes in `DAT_00069d06`. What that byte changes is unread. |
| `dsc%02d.dat` | `FIELD2.VFS` | First dword is the section count. Each section is 8 dwords. The third and fourth are the parallax scale in [Map](map.md), and the low bytes of the seventh and eighth are the paint order and the range highlight. Of 66 sections, 62 are order 9 and highlight 1 (the ground, a fixed recolor), 3 are order 8 and highlight 0 (a slower plate that skips the range), and 1 is order 11 and highlight 2 (painted over the units, blended). `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. |
| `m%02d%d.mpl` | `FIELD1.VFS` | One per section. |
| `m%02d%d.cel` | `FIELD1.VFS` | Tile graphics for that section. |
| `attr%02d%d.dat` | `FIELD2.VFS` | Magic `ATR`. One 4-byte record per tile picture, starting at file offset `0x11`. See [terrain](map.md). |

`M000.MPL` starts with `MPL`, is 1451 bytes, and stores width 30 and height 24 as little-endian shorts at offsets 7 and 9. An 11-byte header plus `30 * 24 * 2` bytes of cells is 1451, so the cells are 2 bytes. After loading, the game allocates `width * height * 2 + 4`, writes the two dimensions in front, and `FUN_00010b20` sets each cell's second byte to `0xff` and masks the first byte with `0x3f`. That runs on a fresh allocation, so it does not copy the MPL. The MPL remains the terrain; this buffer is a separate occupancy layer. Tile pixels are 24×24: the camera coordinates saved to disk are divided by `0x18`, and both map and combat sprites are blitted at 24×24.

A shop file is three groups of 12 bytes. `FUN_00031470(group, dest)` copies bytes from `group * 12` until `0xff` or 12 bytes, each byte widened to a dword item id, and returns the count. Every id in the thirty files is below 251, which is the `Item.dat` row count in [Units](units.md). Sixteen groups are twelve `0` bytes with no `0xff`, so that reader returns twelve ids of 0. One group begins with `0xff` and contributes nothing.

`FUN_00032480(group)` is the list. It returns the chosen id, or −1 on cancel. `FUN_000338f0` calls it, then `FUN_00018b30` on that id. The price starts as the unsigned short at item `+0x13`. When `FUN_00017980` returns 0, the short at `+0x13` of the equipped record found by `FUN_000251d0` is multiplied by 5 and shifted right by 2, and that credit is subtracted from the price. A price above 0 is refused when it is greater than the dword at `0x643b8`. A confirmed pay subtracts the price from that dword at `0x33bad`. A price at or below 0 is negated, and a confirmed pay adds it at `0x33c58`. The same function then gives the item with `FUN_00025cf0`. The three village actions pass the group: `FUN_000355d0` passes 0, `FUN_00035d40` passes 1, and `FUN_00035f80` passes 2. The rest of those three bodies was not read.

The scenario index is the battle map. `FUN_00022720` passes `DAT_00069cf4` to `FUN_00022bb0`, and that function calls `FUN_000227b0` before it places anyone. Every name in the table above is formatted with that same index. The walkable grid is section 0: `m%02d0.mpl`. Its width and height are the shorts at `+7` and `+9`, `FUN_000227b0` copies those two shorts into the occupancy grid, and each cell is the picture short already described above. A later section is another plate on that visit, drawn as in [Map](map.md). Of indexes 0 through 29, scenarios 5 and 29 add a plate at order 8, and scenario 7 adds the plate at order 11. The other 27 have one section.

The title stores index 0. Each ending in the table in [Session](session.md) stores the next index, 1 through 29, with `mov dword [DAT_00069cf4], imm`. The visit that follows therefore loads the next numbered grid. Files past index 29 use the same layout. None of those immediate stores names them.

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

`MAP##.DAT` says who is on that grid. Byte 0 is 0 in every file. Byte 1 is stored in `DAT_00064118` and is how many unit slots are allocated. Byte 2 is stored in `DAT_0006410c` and is how many 26-byte records sit at `+0x83`. Every file is `0x83 + byte 2 * 26` bytes. The saved copy of `0x8a3` bytes is that length at 80 records.

Bytes 3 through `0x32` are sixteen rows of three, read by `FUN_0002de50`. For each row, when byte 0 equals the turn counter `DAT_00069ce8` and byte 2 equals the side argument, it calls the pointer at `0x601c4 + byte 1 * 4` with argument 0. The first pointer there is `0x36920`. The rows and the call are in [Turns](turns.md). Bytes `0x33` through `0x52` still have no reader. The 26-byte record and the three-byte rows at `+0x53` are in [Units](units.md) and [Turns](turns.md).

`FUN_00022bb0` opens `ICON.CEL` (the string at `0x61a03`, mode at `0x61a00`) and loads `map%02d.cod` from `FIELD.VFS` into `DAT_00060140`. The file begins `COD`. The short at `+7` equals byte 1 plus byte 2, and the file is `9 + that count * 6` bytes in every pair. Placement does not read that short. It addresses a record at `file + 0x0b + index * 6`. The short at `+0` is x and the short at `+2` is y. The high byte of both is 0 in all 1647 records of indexes 0 through 29, and every one of those coordinates sits inside section 0. `FUN_00022bb0` copies the low bytes onto the unit. The loop runs `i` from 0 up to byte 1. While `i` is also below `DAT_00064114` it copies 80 bytes from `DAT_00064108 + i * 0x50`, then takes the coordinate at index `byte 2 + i`, and stores side 2. A slot at or above `DAT_00064114` is zeroed and gets flag bit 0 set. The roster count is how many of those records are filled. It grows only in `FUN_00023b90`, which the scenario openers call, and it is restored from a save or cleared at the title. Nothing else stores it, and nothing swaps two roster records. The characters who fight are therefore the prefix of the roster, in the order they were appended, cut off at byte 1. A character appended once the count already equals byte 1 is not copied. Which opener appends which id is in [Session](session.md).

`FUN_00023800(scenario, group, arg)` walks the 26-byte records and calls `FUN_00023280(index, icon, arg)` when byte `+0x15` equals `group`. The load calls it as `(scenario, 0, 1)`, so group 0 is on the map before the icon script. That spawn reads the same COD slot as the record's own index, and it loads x and y as the signed shorts. Across indexes 0 through 29, byte `+0x15` is 0 through 15, or `0xff` in 18 records. Byte 0 of the record is the side copied to unit `+6`, and byte `+1` is the character id copied to `+7` and `+8`. Across the 63 `MAP` files, indexes 0–64 except 30 and 33, that byte is a character id from 0 through 156. The short at COD record `+4` is not read by either placement. The 80-byte unit those calls fill is in [Units](units.md).

`FUN_00021620` is the icon script, one file `Icon##.dat` inside `IconAni.vfs`, named from the opener's argument. It walks opcodes until byte 0. The ones read here:

| Opcode | Advance | What it does |
| --- | --- | --- |
| 1 | 4, plus 2 per unit | `FUN_00021f30`. Steps the named units one tile along a facing, redrawing between frames. |
| 2 | 3, plus 2 per unit | `FUN_000220d0`. Stores a facing on each named unit, then redraws. |
| 3 | 2 | Shows the text id in the next byte. |
| 4 | 3 | Spawns a group. The next byte is the group, or `0xff` to use the value opcode 99 stored. The byte after that is the third argument of `FUN_00023800`. |
| 6 | 2 | Plays `Icon%04d.saf` from `IconAni.vfs`. The number is the next byte. Every frame is shown for its hold, in [Pictures](pictures.md). |
| 7 | 2 | `FUN_00030960` on the next byte, or on `-1` when that byte is `0xff`. |
| 8 | 2 | Plays `Icon%04d.wav`. |
| 10 | 5 | Writes x, y, and facing onto the unit named by the next byte, when that index is below the slot count. |
| 11 | 2 | Sets flag bit 0 on that unit. |
| 12 | 2 | Clears flag bit 0 and the six count bytes at `+0x22`. |
| 13 | 3 | Moves the camera and the cursor to the tile in the next two bytes, times 24. |
| 16 | 3, plus 2 per step | `FUN_000224c0`. Adds signed byte pairs to the camera and redraws. |
| 17 | 2 | Stores the next byte as the scenario index and calls `FUN_00022720`. |
| 18 | 4 | Writes the third byte into the unit's count byte at `+0x25` plus the second byte. |
| 19 | 3 | Stores the second byte into `DAT_000640d8` at the first byte, then calls `FUN_0002e6a0`. |
| 20 | 5 | Writes the short at the third byte into the section-0 cell at the first two bytes. |
| 21 | 4 | `FUN_00022f10` with the next three bytes. |
| 97 | 1 | Ten times, stores 99 and calls `FUN_0001dd00(3)`, then calls `FUN_00023950`. |
| 98 | 3 | `FUN_00010010` with the next two bytes. |
| 99 | 1 | `FUN_000225d0`. Two yes-or-no questions. Returns 1, 2, or 3, which a later opcode 4 can use as the group. |

Opcode 0, and any other byte, ends the script. Opcodes 5, 9, 14, and 15 call `FUN_00021e00`, `FUN_000221b0`, `FUN_000223e0`, and `FUN_00022450`. Those four were not read. `0x36920` also calls `FUN_00023800`; its other arguments were not read. The archive directory is in [Archives](archives.md).
