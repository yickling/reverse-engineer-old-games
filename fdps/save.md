# Save file

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`object 1 + 0x4e90` is the system menu and the writer of `FDE.SAV`. The file is one 22987-byte buffer (`0x59cb`), which matches the copy on disk. Layout written in order:

| Offset | Size | Contents |
| --- | --- | --- |
| `0x0000` | `0x8a3` (2211) | current `MAP##.DAT` |
| `0x08a3` | `0xa00` (2560) | block at `object 2 + 0x4108` |
| `0x12a3` | `count * 0x50` | the unit array |
| `0x30a3` | `0x20` | flags at `object 2 + 0x40d8` |
| `0x30c3` | 1 | turn counter `object 2 + 0x9ce8` |
| `0x30c4` | 1 | unit count |
| `0x30c5` | 1 | scenario index |
| `0x30c6` | 4 | camera x, camera y, cursor x, cursor y, each already divided by 24 |
| `0x30ca` | 2 | both written 0 |
| `0x30cc` | 1 | roster count `object 2 + 0x4114` |
| `0x30cd` | 4 | `object 2 + 0x43b8` |
| `0x30d1` | 1 | `object 2 + 0x10` |
| `0x30d2` | 1 | `object 2 + 0x158` |
| `0x30d3` | 1 | `object 2 + 0x8` |
| `0x30d4` | 1 | `object 2 + 0x9d70` |
| `0x59c7` | 4 | sum of the preceding `0x59c7` bytes, from `object 1 + 0x46608` |

`object 1 + 0x46608(buffer, length)` returns the sum of the first `length − 4` bytes. The save passes `0x59cb`, so the sum covers the bytes before the dword at `0x59c7`. The same walk restores the bytes. The writer sums the plain buffer and then walks it. The reader walks it and then sums it.

```
# object 1 + 0x46627, over the 0x59cb bytes
word = 0xa5
for each byte:
    word = word + 0x9014
    word = rotate_left(word, 3)
    byte = byte xor low_half(word)
```

`object 1 + 0x13df0` reads the same buffer back. A checksum that does not match the dword at `0x59c7` shows interface string `0x208` and the load continues. It copies the roster block, stores the scenario byte, and calls `object 1 + 0x127b0`. It then replaces the map block with the `0x8a3` bytes at the front and stores map byte 1 and byte 2 in `object 2 + 0x4118` and `object 2 + 0x410c`. The unit array is allocated to `0x1e00` bytes, 96 slots, and `count * 0x50` bytes are copied in. Each unit's byte `+2` is filled again from `ICON.CEL`. The turn counter, the camera, the cursor, the roster count, `object 2 + 0x43b8`, and the four option bytes are copied from `0x30c3` onward. `object 1 + 0x1e6a0` then advances the marked tiles, the map is redrawn, `PlyPhase.saf` plays, and the phase music is called with argument 0.

Empty-slot bytes `0xff` are written at `0x3b2b`, `0x4553`, `0x4f7b`, and `0x59a3` when the file did not already exist. Those are the scenario byte of four slots. `object 1 + 0x14460` reads a slot at `0x312b + slot * 0xa28`. It copies `0xa00` bytes into the roster at `object 2 + 0x4108`. The next byte is the scenario index. The byte after that is the roster count `object 2 + 0x4114`. The dword at `+2` is `object 2 + 0x43b8`. Bytes `+6` through `+9` are `object 2 + 0x158`, `object 2 + 0x10`, `object 2 + 0x8`, and `object 2 + 0x9d70`. When `object 2 + 0x70` is 0, the dword `0x14` bytes before the scenario byte is stored at `object 2 + 0x4110`. On the way out, `object 1 + 0x14605` calls `object 1 + 0x1f910` with the screen the loader was given. That is the same call that opened the picture. The reveal is below. Which title row calls that loader is in [Session](session.md). The unit array it restores is in [Units](units.md).

`object 1 + 0x141b0` is the writer of those four slots. It stores 0 at `object 2 + 0x4104`, opens `Save.cel`, and `object 1 + 0x14620` writes the chosen slot through its second argument. It returns 1 or −1. A return other than 1 leaves. Otherwise it reads `FDE.SAV` when the file opens and fills `0x59cb` bytes with `0xff` when it does not. The slot at `0x312b + slot * 0xa28` receives `0xa00` bytes from the roster. The last `0x14` bytes of that copy are five dwords, counted back from the scenario byte: the month, the day, the hour, the minute, and `object 2 + 0x4110`. The month and day come from `object 1 + 0x32ed0`. The hour and minute come from `object 1 + 0x32eef`, whose first byte is the hour and whose second is the minute. Each of those four is one byte stored as a dword. The flag dword is the bar-bonus flag in [Turns](turns.md). The day and month stored here are not the date that flag tests. The byte after the `0xa00` is the scenario index, the next byte is the roster count, the dword at `+2` is `object 2 + 0x43b8`, and bytes `+6` through `+9` are `object 2 + 0x158`, `object 2 + 0x10`, `object 2 + 0x8`, and `object 2 + 0x9d70`. The buffer is written back with mode `wb`, and the `Save.cel` menu runs again. The argument is blitted on the way out. The skipped-scenario call and the bar corner are in [Session](session.md) and [Turns](turns.md).

`object 1 + 0x14460` stores 1 at `object 2 + 0x4104` and opens `Load.cel`. Both screens are `object 1 + 0x14800`. It expands picture 0 of the named member of `MISC.VFS` at `(0, 0)` in a `0xfa00` buffer, pitch `0x140`. It then walks slots 0, 1, and 2. The fourth file slot is not a bar. A scenario byte of `0xff` stores 0 at `object 2 + 0x40f8 + slot * 4`. Any other byte stores 1. The bar is `object 1 + 0x14a10`, and its origin is `(13, slot * 52 + 26)`.

An empty bar draws interface string `0x209` at `(113, slot * 52 + 47)`, ink `0xd0`, fill 0, shadow `0x6d`. A filled bar takes byte `+7` of the roster block, the first member's character, through `object 1 + 0x13020`, and expands the picture at the cache base plus the dword at cache `+4`. That picture is 24×24, mode 0, at `(21, slot * 52 + 36)`. `COMMAND.CEL` through `object 1 + 0x5b80`, 25×22:

| Picture | Where |
| --- | --- |
| `0x2a` | `(19, slot * 52 + 52)` |
| `0x2b` | `(44, slot * 52 + 52)` |
| `0x37` | `(52, slot * 52 + 45)` |
| `0x38` | `(73, slot * 52 + 45)` |
| `0x39` | `(106, slot * 52 + 46)` |

The digits are `object 1 + 0x7520` with width 2. The level is byte `+0x21` of that first member, at `(80, slot * 52 + 45)`, in the row already stored at `object 2 + 0xc`. The function then stores 3 and draws the scenario index plus 1 at `(80, slot * 52 + 55)`. It stores 1 and draws the day at `(94, slot * 52 + 45)` and the month at `(113, slot * 52 + 45)`. It stores 2 and draws the hour at `(94, slot * 52 + 55)` and the minute at `(113, slot * 52 + 55)`. It stores 0 on the way out, so the next bar's level uses row 0. The chapter name is string 1 of `Field.vfs` member `fdetxt` plus the scenario index plus 1, two digits, then `.txt`, drawn at `(130, slot * 52 + 47)` with the same ink, fill, and shadow. The names are in [Names](names.md).

`object 1 + 0x14620` takes the composed screen and a pointer to the slot. The slot starts at 0. Each frame copies the screen, draws one picture of `LoadKon.cel` at `(10, slot * 52 + 25)`, and copies the buffer to `0xa0000`. The frame is `(object 2 + 0x9d64 >> 2) & 3`, and 3 is drawn as 1, so the cycle is 0, 1, 2, 1. A key byte above `0x7f` does not move. Up (`0x48`) and left (`0x4b`) store `(slot + 2) % 3`. Down (`0x50`) and right (`0x4d`) store `(slot + 1) % 3`. A move plays `Beep.wav`. Enter (`0x1c`) and space (`0x39`) return 1 and play `Sure.wav`, unless `object 2 + 0x4104` is nonzero and that slot's dword is 0. A save leaves the dword at 0, so any of the three confirms. A load sets it, so an empty bar does not. Escape (`0x01`) returns −1. The three cursor positions are `(10, 25)`, `(10, 77)`, and `(10, 129)`.

`object 1 + 0x1f910(src, srcPitch, dest, destPitch, width, height, columns, rows, blockWidth, blockHeight, wait)` opens and closes both screens. The four calls pass the composed screen, or the caller's screen on the way out, pitch `0x140`, destination `0xa0000`, pitch `0x140`, width `0x140`, height `0xc8`, 16 columns, 16 rows, a block of 4 by 3, and a wait of 1. It fills a list of the 256 cells and swaps each one with a random cell. Then, in that order, a cell copies 4×3 rectangles through `object 1 + 0x1f080` and calls `object 1 + 0x2d0e0(1)`. A cell at column `cx` and row `cy` writes x `16 * dx + cx` and y `3 * (16 * dy + cy)`, with `dx` and `dy` each running from 0 through 4, and skips a rectangle whose x is at least 320 or whose y is at least 200. The x values that are written run from 0 through 82. The y values cover the full 200 rows.
