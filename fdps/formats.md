# File formats

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is how the bytes are laid out. How a frame is drawn is in [Pictures](pictures.md). How a visit uses a scenario is in [Scenario files](scenario.md). How a tile is queried is in [Map](map.md). How a string is drawn is in [Text](text.md). Packed members are the directory in [Archives](archives.md): magic `VFS`, version `uint16` 1 at `+3`, directory offset `uint16` `0x23` at `+5`, member count `uint32` at `+7`. Each entry is 26 bytes: a 13-byte name, `uint32` size at `+13`, a second `uint32` at `+17` that equals the size on every member checked, one zero byte, and the file offset `uint32` at `+22`. `FUN_00039820` reads that directory.

## Sprites

Two picture containers. Both store palette indexes, not RGB. A palette file is 768 bytes, 256 triples, each component 0 through 63. `Fde.pal` colors the map and the interface. `Fight.pal` colors the fight. `FUN_00022f10` writes those bytes to the DAC.

### CEL

Map sprites, portraits, section tiles, and the interface windows. The header is `CEL`, version byte `0x01`. On every file checked, byte 6 is 0 and byte 8 is 0 or 1. `FUN_0002d930` takes the width from the little-endian short at `+7` and the height from the little-endian short at `+9`. That width is byte 7 plus 256 times byte 8, so a section tile is 24×24 and `VILLAGE.CEL` is 320×200. The directory offset is the big-endian short at `+4`, and it is `0x0f` on every file checked, including all 69 section files in `FIELD1.VFS`. The little-endian dwords there are picture offsets. Picture `i` is the bytes from dword `i` to dword `i+1`. The uint16 at `+10` is the picture count for the `.cel` members of `MISC.VFS` and for `FACE.CEL`. On `ICON.CEL` that field is 128, and the ordered directory holds 1920 pictures.

A picture is a signed column count, a signed row count, and then that many cell indexes. None of the fight pictures has a negative count. Each cell is a compressed stream. Mode 0 of `FUN_0005664b` is the decoder that writes the stored indexes. The opcodes are in [Pictures](pictures.md).

`ICON.CEL` gives character `id` pictures `id * 12` through `id * 12 + 11`. `FUN_00023020` reads the directory at `0x0f`. The 1921 dwords run through index 1920, where the dword equals the file size, so ids 0 through 159 each have 12 frames. A frame expands to 24×24. `FACE.CEL` is one 125×100 picture per id, 160 pictures. Section tiles are the same container, one picture per `ATTR` record on 68 of the 69 section files. `M310.CEL` is the exception named in [Map](map.md).

### SAF

Fight clips, spell clips, backdrops, icon clips, and the three members of `BaseAni.vfs` (`EasyAni.saf`, `Explo.saf`, `Turn.saf`). Version byte `0x06`. `FUN_000140e0` returns one frame and `FUN_000144d0` returns the count.

| Offset | Field |
| --- | --- |
| 0 | `SAF` |
| 3 | version `0x06` |
| `+7`, `+9` | `uint16` cell width and height. 24 and 24 on `STAND000.SAF`. |
| `+0x0c` | `uint16` frame count |
| `+0x0e` | `uint32` offset of the frame-offset table, `count` dwords |
| `+0x16` | `uint16` limit on a chunk's picture index |
| `+0x18` | `uint32` offset of that picture table |
| `+0x20` | `uint16` limit on a cell index |
| `+0x22` | `uint32` offset of the compressed-cell table |
| `+0x2a` | `uint16` sample count |
| `+0x2c` | `uint32` offset of the sample-offset table |

Frame `i` is the record at `file + dword[table + i*4]`. Inside it: `int16` sample index at `+0`, `int16` hold at `+2`, a preamble byte at `+4`, a hit byte at `+5`, and the chunk count `int16` at `+8`. Chunks start at `+10` and are 13 bytes: picture `uint16`, x `int16`, y `int16`, a mode byte, an `int16`, and four trailing bytes that are 0 on the fight and effect clips. A picture in the picture table is the column count, the row count, and the cell indexes. A cell in the cell table is the compressed stream mode 0 expands. The same layout covers `FIGHT.VFS`, `FIGACT.VFS`, `BACKGRND.VFS`, the effect members of `MISC.VFS`, and the 67 `ICON####.SAF` members of `ICONANI.VFS`.

## Scenario data

`FUN_000227b0` formats these names with `DAT_00069cf4`. The grid each index loads is in [Scenario files](scenario.md).

`MAP##.DAT`, in `FIELD.VFS`, is who stands on the map. Byte 0 is 0 in every file. Byte 1 is how many unit slots are allocated. Byte 2 is how many 26-byte actor records follow. Every file is `0x83 + byte 2 * 26` bytes. Bytes 3 through `0x32` are sixteen rows of three. Bytes `0x33` through `0x52` are sixteen pairs. Bytes `0x53` through `0x82` are sixteen triples. The actor records start at `+0x83`. What those rows do in play is in [Turns](turns.md) and [Units](units.md).

`MAP##.COD` begins `COD`. The short at `+7` equals byte 1 plus byte 2 of the matching `MAP` file, and every file is `9 + that count * 6` bytes. A record is at `file + 0x0b + index * 6`. The short at `+0` is x and the short at `+2` is y. The short at `+4` is not read by placement. Header byte 4 is 1 or 16. What that byte selects was not read.

`SHOP00.DAT` through `SHOP29.DAT` are 36 bytes. `FUN_00031470` reads three groups of 12. A group ends at `0xff` or at 12 bytes, and each kept byte is an item id.

`Icon00.dat` through `Icon29.dat`, the `Win` scripts, and `GoodEnd.dat` are in `ICONANI.VFS`. A script is a byte stream. Opcode 0 ends it. There is no header. The opcodes and the lengths that walk every `.dat` member of that archive are in [Scenario files](scenario.md).

The character, enemy, class, spell, and rank rows are members of `MISC.VFS`. The structs, the strides, and which function indexes each one are in [Units](units.md).

## Map data

One scenario index names a `DSC` file, and each section of that file names an `MPL`, a `CEL`, and an `ATTR` file. `M%02d.dtl` is a separate byte per tile.

`DSC##.DAT`, in `FIELD2.VFS`. The first dword is the section count. Each section is eight dwords. `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. The third and fourth dwords are the parallax scale. The low bytes of the seventh and eighth are the paint order and the range highlight. The 66 sections are counted in [Map](map.md).

`M%02d%d.MPL`, in `FIELD1.VFS`. All 68 files start `MPL`, store version byte 1 at `+4`, and store `uint16` 11 at `+5`. The width and height are the little-endian shorts at `+7` and `+9`. The cells start at `+0x0b` and are little-endian shorts, one tile-picture index per cell, row by row. Every file is `11 + width * height * 2` bytes. `FUN_0002c0c0` reads `file + 0x0b + (y * width + x) * 2`.

`M%02d%d.CEL` is the tile sheet for that section. The container is the `CEL` layout above. The big-endian short at `+4` is `0x0f` on all 69 section files.

`ATTR###.DAT`, in `FIELD2.VFS`. All 69 files start `ATR`, store version byte 1 at `+4`, and store `uint16` 13 at `+5`. Records start at `+0x11` and are 4 bytes, so the count is `(length - 0x11) / 4`. `FUN_0002b790` reads the record of the picture index:

| Byte | Use |
| --- | --- |
| 0 | Animation. Bits `0x60` are the tile-search test. |
| 1 | Passed to the expander when bit `0x80` of byte 0 is set. |
| 2 | Terrain kind. On disk the values are 0, 1, 2, 5, and 6. |
| 3 | Backdrop index. Combat loads `Back%02d.saf` from it. |

`M%02d.DTL`, in `FIELD1.VFS`. All 64 files start `DTL`, store version byte 1 at `+4`, and store `uint16` 14 at `+5`. The little-endian shorts at `+7` and `+9` are a width and a height. The payload starts at `+0x10`, one byte per tile. `FUN_0002b790` copies the byte of the queried tile. For 63 files the length is `16 + width * height`. `M31.DTL` is 51 by 64 and 6545 bytes, longer than that product. The bytes past the first `51 * 64` were not read.

## Strings

`FDETXT##.TXT`, in `FIELD.VFS`. All 66 files use one layout. `FUN_00029630` loads `FDETXT00.TXT` as the interface block. `FUN_000227b0` and `FUN_00030f80` load `FDETXT(index + 1).TXT` for the scenario.

```
count = first_u16 / 2
offset[i] = u16 at byte i*2
glyphs of string i = the u16s from offset[i] up to offset[i+1], or to EOF for the last
```

The offsets are nondecreasing and every span is even, so the strings tile the tail of the file. Every string ends with `0xffff`. The other words are either a cell index or one of the eight controls in [Text](text.md). A cell index is not a character code.

`FDETXT.FON` is 57344 bytes, 1792 cells of 32. Cell `n` is `font + n * 0x20`. A cell is 16 rows of two bytes. `FUN_0001fea0` takes the high bit of a byte as the leftmost pixel and shifts left for the next pixel. A set bit writes the palette index. A clear bit leaves the pixel already there. Cells 0 through 9 are the digits and cells 10 through 35 are `A` through `Z`. The reading of the other cells is `extract/text/glyph-map.tsv`. The notes do not carry the strings.

## Sound

Sampled effects are RIFF `WAVE` files. Each one checked has a `fmt ` chunk of audio format 1, one channel, 8 bits, and a `data` chunk of that many bytes. The bytes sit around `0x80`. `BaseWav.vfs` is a `VFS` member of `MISC.VFS` with nine members, all 11025 Hz: `Beep.wav`, `Chess.wav`, `Equip.wav`, `Incom.wav`, `Miss.wav`, `OpWin.wav`, `OpWin1.wav`, `Rest.wav`, and `Sure.wav`. Three further waves sit directly in `MISC.VFS`. `Bonus.wav` and `EarQu.wav` are 11025 Hz. `Levup.wav` is 22050 Hz. Some of these files also carry `fact`, `LIST`, and `cue ` chunks after `data`. The calls that start a named wave were not decompiled.

A `SAF` sample is not a `WAVE` file. The record at `file + dword[sample_table + index * 4]` is two flag bytes, a `uint16` passed to `FUN_0003f096`, a `uint32` length, and that many bytes at `+8`. On the one sample in `ACT000.SAF` the `uint16` is 11025 and the length is 4464. `01 08` selects 0, `01 10` selects 1, `02 08` selects 2, and any other pair selects 3. That value is passed to `FUN_0003ee60` with a 2. `FUN_0003edde`, `FUN_0003f1f8`, and `FUN_0003eee2` then start the slot. Those three were not decompiled.

`BaseAni.vfs` is the other nested archive in `MISC.VFS`. Its three members are `SAF` clips, not waves.

Music is a track number, not a file in these archives. `FUN_00030a30` reads the byte at `0x30230 + scenario * 2 + argument` and calls `FUN_0003c5cb` with that byte plus 1. The sixty bytes are in [Turns](turns.md). No `.xmi`, `.mid`, or `.aud` member is in the archives walked. The executable names `%s\Pack.vfs` and `%s\%s.Aud`. The intro path names `FD1.Aud` beside `fd.exe` and `FD1.Vid`. Those files were not among the data files walked. `Icon%04d.wav` is the name icon opcode 8 formats. No member of that name is in `ICONANI.VFS` or `BaseWav.vfs`.
