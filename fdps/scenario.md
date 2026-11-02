# Scenario files

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_000227b0` runs off the scenario index in `DAT_00069cf4`. Who calls it, and the per-scenario openers around that load, are in [Session](session.md).

| Pattern | Archive | What the code does with it |
| --- | --- | --- |
| `fdetxt%02d.txt` | `FIELD.VFS` | Loaded with index + 1. The table layout is in [Text](text.md). |
| `map%02d.dat` | `FIELD.VFS` | Byte 1 and byte 2 stored in `DAT_00064118` and `DAT_0006410c`. For `MAP00.DAT` those bytes are 1 and `0x16`. Byte 1 is the unit count. Byte 2 is added to the unit index before the `MAP##.COD` lookup below. Record layout past those two bytes is unread. |
| `Shop%02d.dat` | `FIELD.VFS` | One file per scenario index, `SHOP00.DAT` through `SHOP29.DAT`, each 36 bytes. `FUN_000312b0` loads `Shop%02d.dat` for `DAT_00069cf4` into `DAT_00069d80`. |
| `M%02d.dtl` | `FIELD1.VFS` | Magic `DTL`. `M00.DTL` is 4112 bytes: a 16-byte header whose short at `+7` is `0x40`, then `64 * 64` bytes. `FUN_0002b790` stores one of those bytes in `DAT_00069d06`. What that byte changes is unread. |
| `dsc%02d.dat` | `FIELD2.VFS` | First dword is the section count. Each section is 8 dwords, then two trailing bytes stored separately. `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. |
| `m%02d%d.mpl` | `FIELD1.VFS` | One per section. |
| `m%02d%d.cel` | `FIELD1.VFS` | Tile graphics for that section. |
| `attr%02d%d.dat` | `FIELD2.VFS` | Magic `ATR`. One 4-byte record per tile picture, starting at file offset `0x11`. See [terrain](map.md). |

`M000.MPL` starts with `MPL`, is 1451 bytes, and stores width 30 and height 24 as little-endian shorts at offsets 7 and 9. An 11-byte header plus `30 * 24 * 2` bytes of cells is 1451, so the cells are 2 bytes. After loading, the game allocates `width * height * 2 + 4`, writes the two dimensions in front, and `FUN_00010b20` sets each cell's second byte to `0xff` and masks the first byte with `0x3f`. That runs on a fresh allocation, so it does not copy the MPL. The MPL remains the terrain; this buffer is a separate occupancy layer. Tile pixels are 24×24: the camera coordinates saved to disk are divided by `0x18`, and both map and combat sprites are blitted at 24×24.

A shop file is three groups of 12 bytes. `FUN_00031470(group, dest)` copies bytes from `group * 12` until `0xff` or 12 bytes, each byte widened to a dword item id, and returns the count. Every id in the thirty files is below 251, which is the `Item.dat` row count in [Units](units.md). Sixteen groups are twelve `0` bytes with no `0xff`, so that reader returns twelve ids of 0. One group begins with `0xff` and contributes nothing.

`FUN_00032480(group)` is the list. It returns the chosen id, or −1 on cancel. `FUN_000338f0` calls it, then `FUN_00018b30` on that id. The price starts as the unsigned short at item `+0x13`. When `FUN_00017980` returns 0, the short at `+0x13` of the equipped record found by `FUN_000251d0` is multiplied by 5 and shifted right by 2, and that credit is subtracted from the price. A price above 0 is refused when it is greater than the dword at `0x643b8`. A confirmed pay subtracts the price from that dword at `0x33bad`. A price at or below 0 is negated, and a confirmed pay adds it at `0x33c58`. The same function then gives the item with `FUN_00025cf0`. The three village actions pass the group: `FUN_000355d0` passes 0, `FUN_00035d40` passes 1, and `FUN_00035f80` passes 2. The rest of those three bodies was not read.

`FUN_00022bb0` then opens `ICON.CEL` (the string at `0x61a03`, mode at `0x61a00`), loads `map%02d.cod` from `FIELD.VFS` into `DAT_00060140`, and builds the unit array. For each unit index `i` below `DAT_00064114` it copies 80 bytes from `DAT_00064108 + i * 0x50`, then overwrites x and y from a 6-byte `COD` record. The record is at `file + 0x0b + (DAT_0006410c + i) * 6`. Byte 0 of that record becomes x and byte 2 becomes y. `MAP00.COD` begins `COD` and is 147 bytes, so the 6-byte stride reaches the last record with only a few bytes left; the fields past byte 2 were not read. Units at or above `DAT_00064114` are zeroed and get flag bit 0 set. `FUN_00023800` runs at the end of that load. The 80-byte record is in [Units](units.md). The archive directory those names come from is in [Archives](archives.md).
