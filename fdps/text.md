# Text

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

## Where the strings are

There are two blocks, and both use the layout below. `FUN_00029630` loads `Fdetxt00.txt` into `DAT_000643d0`. `FUN_000227b0`, `FUN_00030f80`, and `FUN_000312b0` load `fdetxt%02d.txt` from `FIELD.VFS` into `DAT_00060124`. The number is `DAT_00069cf4 + 1`, so scenario 0 reads `FDETXT01.TXT` and the interface strings stay in `FDETXT00.TXT`. `FUN_000312b0` frees the previous block first.

All 66 `FDETXT##.TXT` members share the layout. A file holds between 9 and 555 strings. Together they hold 1746 strings, and the longest run is 798 indexes.

```
count = first_u16 / 2
offset[i] = u16 at byte i*2, for i in 0 .. count-1
glyphs of string i = the u16s from offset[i] up to offset[i+1], or to EOF for the last
```

The offsets are nondecreasing and every span is an even number of bytes, so the strings tile the tail of the file. The glyphs of `FDETXT00.TXT` start at byte `0x456`. Every string ends with `0xffff`, and that word does not occur earlier in the span. `FUN_0001ff30` stops on it. 317 strings contain only that word.

`FDETXT.FON` is 57344 bytes, which is 1792 cells of 32. `FUN_00029630` stores the drawing metrics before it opens the font:

| Address | Stored | What the drawer reads |
| --- | --- | --- |
| `0x6403c` | byte `0x10` | Cell width. |
| `0x6403d` | byte `0x10` | Cell height. |
| `0x6403e` | dword 1 | Shadow step in x. |
| `0x64042` | dword 1 | Shadow step in y. |
| `0x64046` | dword `0x20` | Bytes from one cell to the next. |
| `0x6404a` | byte 0 | Outline. No other instruction stores this byte. |
| `0x6404b` | dword `0x10` | How far the pen moves after a cell. |
| `0x6404f` | dword `0x12` | How far a new line moves. |
| `0x643d4` | the font pointer | `FUN_0001fd50` adds the cell index times `0x20` to this. |

Cell `n` is the 32 bytes at `font + n * 0x20`. Indexes 0 through 1791 all occur. Every other word in the 66 files is one of the eight controls in the next section, `0xffee` through `0xffff`. A cell index is not a character code. A GBK scan of the text members finds no Han bytes.

Cells 0 through 9 are the digits, and cells 10 through 35 are `A` through `Z`. The other cells were read from the bitmaps. That reading is `extract/text/glyph-map.tsv`. `scripts/extract_text.py` applies it: scenario index N is `FDETXT(N+1).TXT`, written to `extract/text/scenario-NN.txt`, and `FDETXT00.TXT` is `extract/text/interface.txt`. Two blank cells are spaces. A cell that looks like two similar characters can be off by one stroke. The notes do not carry the strings.

## How a string is drawn

`FUN_0001ff30(block, index, dest, pitch, ink, fill, shadow)` walks one string. The pen starts at `dest`. The cursor starts at `block + u16[index]`. The arithmetic is that function:

```
line = 0
origin = dest
while the word at the cursor is not 0xffff:
    0xfffe: line = line + 1
            pen = origin + pitch * 0x12 * line
    0xfffd: draw the message box, set line = 0, and move origin and the pen
    0xfffc: pen = the same walk on DAT_000643d0, string DAT_00064030
    0xfffb: pen = the same walk on DAT_000643d0, string DAT_00064034
    0xfffa: format the number at DAT_00064038 with the "%d" at 0x617e8
            draw each resulting byte minus 0x30 as a cell, then pen = pen + 0x10
    0xffef: read the next word, show that portrait, then origin = pen = 0xaa44a
    0xffee: read the next word as a unit slot, show that portrait, then origin = pen = 0xaa44a
    anything else: stamp that cell, then pen = pen + 0x10
```

A line breaks only on `0xfffe`. The walk does not measure the line.

`0xfffd` is the page. It rebuilds the map, draws the box, draws the portrait at `DAT_00060120` when that pointer is set, and copies the 312×192 window. The box, the portrait expansion, and the copy are the message path in [Pictures](pictures.md). Byte `DAT_00060070` chooses the box and the pen. At 0 the box is `MESSAGE.CEL` and the following cells start at `0xaa44a`, VGA `(138, 131)`. Any other value uses the picture at `DAT_00069d84` and starts at `0xaa3d4`, VGA `(20, 131)`. The pitch stays the one the caller passed. `FUN_00030f80` stores 1 into the byte at `0x31066` and stores `ShopWin.Cel` at `DAT_00069d84`, then stores 0 at `0x3122c`.

Icon opcode 3, in [Scenario files](scenario.md), is the call at `0x21896`. It passes the scenario block, the next script byte as the index, destination `0xa0000`, pitch `0x140`, ink `0xd0`, fill 0, and shadow `0x6d`.

`FUN_0001fd50` stamps one cell. A nonzero fill paints the 16×16 rectangle with that palette index. The cell is then stamped one pixel down and to the right in the shadow index, and at the pen in the ink index. `FUN_0001fea0` reads 16 rows of two bytes each. The high bit of a byte is the leftmost pixel, and the byte shifts left for the next pixel. A set bit writes the palette index. A clear bit leaves the pixel already there. The outline path stamps the cell four more times, one pixel up, down, left, and right, and it runs when byte `0x6404a` is nonzero. The loader stores 0, and nothing else writes that byte, so the image takes the shadow path.

`0xffee` takes the following word as a slot. `FUN_0002cfa0` returns `DAT_00069cd8 + slot * 0x50`. Byte 0 and byte 1 of that unit are the tile, and byte `+7` is the character id, as in [Units](units.md). `0xffef` passes its following word to `FUN_0002d9b0`, in [Turns](turns.md), and uses byte `+7` of the record that call writes. Both call `FUN_00020a40(x, y, id)`. A lookup that returns −1 passes x as −1, and `FUN_00020a40` then calls `FUN_00020580`. Otherwise it centres the camera on the tile and, for frames 0 through 6, draws `MESSAGE.CEL` through `FUN_0002d930` with expander mode 4. The box grows to 302×73. Frame 6 lands at buffer `(29, 140)`, which is where a page draws the same picture. Either path finishes with `FUN_000177c0(0xa708c, 0x140, id)`: `FACE.CEL` at VGA `(12, 90)`, pitch 320.

`FUN_00017c90` is the loss window. It opens `MISC.VFS`, reloads the nine tables through `FUN_00018920`, and opens `WinFail.Cel` through `FUN_000293d0`. The archive is freed before the picture is drawn. It expands picture 0 through `FUN_0002d930` into a buffer of `0x6c95` bytes at pitch `0xd1`, so the picture is 209×133. Scenario strings 2 and 3 are drawn there with ink `0xd0` and shadow `0x6d`. String 2 is at `(35, 22)` and string 3 is at `(35, 59)`. `FUN_00017520` draws `DAT_00069cf4 + 1` in two digits at `(85, 4)`, `DAT_00069ce8` in three digits at `(131, 4)`, and `DAT_000643b8` in eight digits at `(87, 121)`. How a value becomes those digits is in [Pictures](pictures.md). `FUN_00018340(side)` counts slots whose byte `+6` equals that side and whose flag bit 0 is clear. The three numbers at `(47, 104)`, `(119, 104)`, and `(174, 104)` are that count for sides 0, 2, and 1, each in two digits.

The window then slides on in four bands. The source rectangles are the dwords at `0x1497c`, `0x1498c`, `0x1499c`, and `0x149ac`. The y of each step in is one of the 76 dwords at `0x1484c`, nineteen per band. The y of each step out is one of the 52 dwords at `0x149bc`. A negative y clips the top of the band. Destination x is the band's source x plus `0x4c`, and destination y is the step plus `0x14`, both in the 360-wide map buffer. The copy to the screen is the 312×192 window in [Pictures](pictures.md).

| Band | Source | Size | Nineteen steps in | Thirteen steps out |
| --- | --- | --- | --- | --- |
| 0 | `(69, 117)` | 71×16 | −8, 8, 20, 45, 75, 110, 156, 157, 156 eleven times | 157, 160, 170, 195, 200 nine times |
| 1 | `(0, 100)` | 209×16 | −16 four times, −8, 10, 30, 55, 85, 110, 139, 140, 139 seven times | 139 twice, 140, 141, 145, 150, 170, 190, 200 five times |
| 2 | `(0, 17)` | 209×82 | −90 eight times, −80, −70, −50, −30, −10, 15, 56, 57, 56 three times | 56 four times, 57, 60, 70, 90, 120, 160, 200 three times |
| 3 | `(55, 0)` | 99×16 | −16 thirteen times, −8, 0, 15, 39, 40, 39 | 39 six times, 43, 48, 60, 80, 110, 150, 190 |

The loss window stays up while `FUN_0005652e` returns a byte above `0x7f`. That call reads a ring of ten bytes at `0x7000f`. `DAT_00070019` is the read index and `DAT_0007001d` is the other index. Equal indexes return `0xff`. Otherwise the byte at the read index is returned, the index advances, and 10 wraps to 0. `FUN_00056523` copies the read index onto the other index, so the next read returns `0xff` until a new byte is stored. The store that advances `DAT_0007001d` was not read.

`FUN_000178e0` is the key read inside the map wait `FUN_000170b0`. It reads the byte at `0x70006`. A value that differs from the previous one is returned immediately, and `DAT_00060018` is cleared. The same value returns `0xff` on a tick of `DAT_00069d64` that has not changed, and on the ticks after a change, until `DAT_00060018` is at least 5 and divisible by 3. The wait in [Pictures](pictures.md) keeps drawing the speaker while the returned byte is above `0x7f`.

Menus and the other windows call `FUN_0001ff30` with their own destination, pitch, and palette indexes. The same cell stamp and the same control words apply.
