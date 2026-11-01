# Text

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FDETXT##.TXT` is loaded to `DAT_00060124` for scenario index + 1. `FDETXT.FON` is 57344 bytes and is opened from `FUN_00029630`. The text block is not encoded characters. It is a table of 16-bit offsets into 16-bit glyph indexes, checked on `FDETXT00.TXT` (555 strings), `FDETXT01.TXT` (16), and `FDETXT02.TXT` (15):

```
count = first_u16 / 2
offset[i] = u16 at byte i*2, for i in 0 .. count-1
glyphs of string i = the u16s from offset[i] up to offset[i+1], or to EOF for the last
```

The offsets are nondecreasing and every span is an even number of bytes, so the strings tile the tail of the file. `FDETXT00.TXT` starts at byte `0x456`. The longest of those three files runs 371 glyphs.

57344 is `1792 * 32`. The first bytes of the font are `00 00 07 e0 1c 38 …`, which is the shape of 16-bit rows. `FUN_00029630` stores width `0x10`, height `0x10`, and `0x20` before it opens the font, so the cell is 16×16 and 32 bytes, not only a size inference. The function that references the loaded text block and was not decompiled is `FUN_00017c90`. The destination rectangle of that blit is still unread.

An extractor walks the offset table, writes each string as a sequence of glyph indexes, and cuts the font into 32-byte cells in index order. It does not produce characters. The mapping from a glyph index to a character is the font bitmap, and a GBK scan of the text members still finds no Han bytes because the bytes were never encoded that way. The notes do not carry the strings.
