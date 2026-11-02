# VFS archives

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_00039820` opens an archive in `"rb"`, seeks to 7, reads a dword count, seeks to 5, reads a word directory offset, and reads `count * 26` directory bytes. `FUN_0002a110(archiveName, memberName)` is the usual caller: open, `FUN_00039940` to extract one member into a malloc block, free the directory. `FUN_0003d1e8` frees those blocks. A missing archive prints `file not found` and exits. A missing member prints `Can't find the string` and exits.

On disk, checked against `FIGHT.VFS`, `FIELD.VFS`, `FIELD1.VFS`, `FIELD2.VFS`, and `MISC.VFS` with zero members past end of file:

| Offset | Field |
| --- | --- |
| 0 | `VFS` |
| 3 | `uint16` version, always 1 |
| 5 | `uint16` directory offset, always `0x23` |
| 7 | `uint32` member count |
| `0x23` | directory |

Each directory entry is 26 bytes. Names are fixed 13-byte fields, not variable C strings.

| Offset | Field |
| --- | --- |
| 0 | name, 13 bytes, null padded |
| 13 | `uint32` size |
| 17 | `uint32` second size. Equal to the first on every member checked, so these files are stored uncompressed. |
| 21 | one byte, 0 on the members checked |
| 22 | `uint32` file offset |

`FUN_00039940` reads the size from entry+`0x0d` and seeks to entry+`0x16`. `FIGHT.VFS` is packed with no gaps: member 0 starts at 3675, which is the end of the directory.

| Archive | Members | Contents the game asks for |
| --- | --- | --- |
| `FIGHT.VFS` | 140 `.saf` | `STAND###.SAF` (94), `MAGIC###.SAF` (46) |
| `FIGACT.VFS` | 91 `.saf` | `ACT###.SAF` |
| `BACKGRND.VFS` | 63 `.saf` | `BACK##.SAF`, one frame each |
| `FIELD.VFS` | 223 | `FDETXT.FON`, 66 `FDETXT##.TXT`, 63 `MAP##.COD`, 93 `.dat` including `MAP##.DAT` and `SHOP00.DAT` through `SHOP29.DAT` |
| `FIELD1.VFS` | 201 | 64 `.dtl`, 69 `.cel`, 68 `.mpl` |
| `FIELD2.VFS` | 131 `.dat` | `DSC##.DAT`, `ATTR###.DAT` |
| `MISC.VFS` | 208 | window `.cel`, `.wav`, `.pal`, 161 `.saf`, `FIGBAR.CEL`, and the item and progression tables in [Units](units.md) |
| `ICONANI.VFS` | 133 | `ICON####.SAF` (67) and `.dat` (66). The clip player is in [Pictures](pictures.md). The `.dat` members were not read. |
| `ICON.CEL` | loose file, 630141 bytes | every map character |
| `FACE.CEL` | loose file, 679928 bytes | 160 pictures, 125×100. The directory is in [Pictures](pictures.md). |

Of the 161 `.saf` members in `MISC.VFS`, 155 are the fight effect clips counted in [Pictures](pictures.md). The other six are `BONUS-1.SAF`, `CHAPTER.SAF`, `ENYPHASE.SAF`, `GAMEOVER.SAF`, `LOGO.SAF`, and `PLYPHASE.SAF`.

`FDETXT##.TXT` is a table of 16-bit offsets into 16-bit glyph indexes. `FDETXT.FON` is 57344 bytes and is the bitmap those indexes draw. A GBK scan of the text members found no Han characters. The table and the font cell are in [Text](text.md). Clip playback is in [Pictures](pictures.md). Scenario members are in [Scenario files](scenario.md).
