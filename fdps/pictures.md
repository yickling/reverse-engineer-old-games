# Pictures

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. The damage number these clips apply is in [Combat](combat.md).

## Drawing a battle, and extracting the pictures

`object 1 + 0x94c0` slides the two standing clips in from the side over nine composed frames before `object 1 + 0x96b0` plays the attack. Side byte `0` enters from the negative x direction (`-15` per frame) and any other side from the positive. The compose buffer is `0x16480` bytes, pitch `0x170`, and each frame is copied to `0xa0000` as 320×200 from buffer+`0x2298`, between two waits on bit 3 of the value `object 1 + 0x2d254(0x3da)` returns. That is the vertical-retrace test. A landed hit still does the 6-step shake and the palette write described in [Combat animation](#combat-animation).

A `SAF` frame is a list of chunks, and each chunk is a grid of compressed cells. From `object 1 + 0x4140`, `object 1 + 0x3fd0`, and `object 1 + 0x3ed0`:

| File offset | Field |
| --- | --- |
| `+7`, `+9` | `uint16` cell width and height. On `STAND000.SAF` both are 24. |
| `+0x0c` | `uint16` frame count. |
| `+0x0e` | `uint32` file offset of the frame-offset table. |
| `+0x16` | `uint16` limit on the chunk's picture index. |
| `+0x18` | `uint32` file offset of that picture table. |
| `+0x20` | `uint16` limit on a cell index. |
| `+0x22` | `uint32` file offset of the compressed-cell table. |
| `+0x2a` | `uint16` count of samples. |
| `+0x2c` | `uint32` file offset of the sample-offset table. |

A frame record still has its hold count at `+2` and its hit marker at `+5`. The chunk count is the short at `+8`. Chunks start at `+10` and are 13 bytes:

| Offset | Field |
| --- | --- |
| `+0` | `uint16` picture index |
| `+2` | `int16` x, in the compose buffer |
| `+4` | `int16` y |
| `+6` | Mode byte. On the fight clips below it is 0 or 1. |
| `+7` | `int16`. When the blit mode dword is 0, a mode byte of 1 selects expander mode 9 and this short is the value subtracted from `0x10`. |
| `+9` | Four bytes. They are 0 on every chunk of `Back`, `Stand`, `Act`, `Magic`, and the effect members of `MISC.VFS`. |

On `Back`, `Stand`, `Act`, and `Magic`, that short is 0 exactly when the mode byte is 0, and a mode byte of 1 stores 8 through 16. The effect members of `MISC.VFS` follow the same pairing, except four chunks of `MB29` and `MB31`, which store mode 1 and short 0. Their other mode-1 shorts run from 2 through 16. A landed hit sets the blit mode dword to 3, and the chunk byte is then ignored. That path is under [Combat animation](#combat-animation). The picture is a signed column count, a signed row count, and then that many cell indexes. None of those pictures has a negative count. Each cell is expanded with `object 1 + 0x4664b` at the chunk's x,y plus the cell's column and row times the cell size.

`object 1 + 0x4664b` stores width, height, and pitch, then switches on a mode byte. Mode 0 is `object 1 + 0x4677d`, and its body is hand-written: it has no prologue, and the source, destination, and per-row adjustment arrive in `ESI`, `EDI`, and `EDX`. `object 1 + 0x4664b` sets that up before the call. It loads the pitch argument into `EDX` and subtracts the width, and the mode body adds `EDX` at the end of each row. Mode 0 and mode 3 both do this. The disassembly is at `object 1 + 0x46657`.

The opcodes, from the listing at `object 1 + 0x4677d`. `n` is `(opcode & 0x3f) + 1`. At the start of a row the body loads the width into `BX` from the word at `object 3 + 0x24`. Each opcode subtracts its count from `BX`, and the row ends when `BX` is 0. `EDI` is then increased by `EDX`, and the height word at `object 3 + 0x22` is decremented.

```
opcode in 0x00..0x3f: read one byte, repeat it n times
opcode in 0x40..0x7f: read one byte, then n times skip one pixel and write that byte
                      (consumes 2n from the width)
opcode in 0x80..0xbf: copy the next n bytes
opcode in 0xc0..0xff: skip n pixels
```

`object 1 + 0x4664b` stores the width, height, and pitch, then calls one body for the mode byte:

| Mode | Body | What the write does |
| --- | --- | --- |
| 0 | `object 1 + 0x4677d` | The four opcodes above, stored byte unchanged. |
| 1 | `object 1 + 0x467fd` | The three write opcodes look up each stored byte in the 256-byte table passed as the sixth argument. Opcode `0xc0` does not skip: it reads the pixels already at the destination, runs each through that table, and writes them back. |
| 2 | `object 1 + 0x46895` | The same three writes as mode 1. Opcode `0xc0` skips `n` pixels and does not read the destination. |
| 3 | `object 1 + 0x46927` | Hit recolor, under [Combat animation](#combat-animation). |
| 4 | `object 1 + 0x469ce` | Scale. The sixth argument is two words, output width then output height. A source pixel is kept when a counter that starts at the output width has reached the source width; the counter then subtracts the source width and adds the output width on a source pixel that is dropped. Output stops after the output width pixels. `object 1 + 0x46b39`, disassembled at `object 1 + 0x46b39`, skips one compressed source row. It runs while a second counter, starting at the output height, is still within the source height, adding the output height each time. |
| 5 | `object 1 + 0x46b9a` | Two signed words in the sixth argument, a horizontal step and a vertical step, in units of 1/4096 of a pixel. Each written source pixel adds the horizontal step to an x counter and the vertical step to a y counter. A counter that passes `0x1000` loses `0x1000` and the destination moves one pixel on that axis. After a source row the vertical step is applied to x and the horizontal step to y. A negative word reverses that axis. A horizontal step of `0x1000` and a vertical step of 0 copies one pixel right and one row down. |
| 6 | `object 1 + 0x46e84` | The sixth argument is a pointer to four words: output width, output height, then the two signed steps of mode 5. The width test is mode 4's, and each kept pixel then takes mode 5's step. The row skip is `object 1 + 0x46b39` again. |
| 7 | `object 1 + 0x472c1` | Mirror left to right. Disassembled. The destination starts at the right edge of the row, and each write moves one pixel left. No remap. |
| 8 | `object 1 + 0x4735d` | Mirror top to bottom. Disassembled. The destination starts on the last row, and the row step passed into mode 0 is `-(pitch + width)`, so mode 0 then walks upward. |
| 9 | `object 1 + 0x4738b` | Blend onto the pixel already in the buffer. On a map, an attribute tint and a range whose highlight is neither 0 nor 1. |
| 10 | `object 1 + 0x47503` | Same tables as mode 9. The key is fixed for the blit, and the destination pixel is not read. On a map, the range on a highlight of 1. |
| 11 | `object 1 + 0x47686` | Same tables as mode 9. The added term is one dword chosen once from the fourth dword of the blend record, not the pixel already in the buffer. The `0x40` opcode still writes every other pixel. The map sprite uses it when flag `0x80` of byte `+5` is set. |
| 12 | `object 1 + 0x477e4` | Mode 9's blend, limited to a range of indexes. The sixth argument is the blend record, and two further words at `+0x0c` and `+0x10` are the low and high index. A sample inside that range, inclusive, is blended. A sample outside it is stored unchanged. Opcode `0xc0` still skips. |

Map tiles and `SAF` cells both enter through mode 0 when no palette argument is passed, so mode 0 is the decoder an extractor needs for the stored picture. `ICON.CEL` frames go through the same function from `object 1 + 0x1cb30`.

Mode 9 reads a pointer of three dwords. The second selects a `0x400`-byte slot of the first, and swaps which of the two slots sits `0x2400` bytes higher when that selector is above 8 (`selector = 0x10 - selector` in that case). The third dword is a byte table. For a source sample and the pixel already at the destination:

```
mixed = (table_a[sample] + table_b[dest]) >> 4 & 0x0f0f0f
out = byte_table[(mixed & 0xffff) | (mixed >> 12)]
```

The four opcodes are unchanged. A skip does not read either table. The fight's two tables are the `0x4800`-byte and `0x1000`-byte files loaded at `object 2 + 0x53f0` and `object 2 + 0x43f0`, under [Combat animation](#combat-animation). Mode 9 cannot be replayed from the cell alone. Mode 10 was disassembled, not decompiled. It builds the same pair of tables, indexes the first once from the dword at struct+`0x0c`, and indexes the second from each source sample.

For a designer, the modes the map and the fight select are these. Mode 0 leaves the stored indexes. Mode 1 remaps each stored index through a 256-byte table. Mode 3, from the first landed hit, rewrites the defender and the attack clip as `(sample & 2) + 0x80`. Inferred: that is the strike flash. Mode 9 mixes the picture with the pixel already on screen. A fight chunk picks the ramp with `0x10` minus the short at chunk `+7`. A map plate picks it with an attribute byte, or with the pulse in [Map](map.md). Inferred: the pulse is a shimmer, and the mix is what lets a plate painted over units still show them. Mode 10 recolors the picture from itself. Inferred: a ground range highlight looks the same whatever was drawn underneath. Mode 11 recolors the picture from itself the same way, and a `0x40` run still leaves every other pixel unwritten. The map sprite takes that path when flag `0x80` of byte `+5` is set, with selector 8, and the frame is the next one in the facing. Mode 2 is mode 1 with a real skip on opcode `0xc0`. Mode 4 scales to an output width and height. Mode 5 applies two 4.12 steps, and the row step swaps the axes. Inferred: that pair is a rotation. Mode 6 runs mode 4's size test and then mode 5's step on each kept pixel. Mode 7 mirrors a row left to right. Mode 8 mirrors the picture top to bottom; the map wait below is the call that passes 8. Mode 12 blends only the indexes inside the two extra words and copies the rest. No direct call of `object 1 + 0x4664b` pushes 2, 5, 6, 7, or 12. `object 1 + 0x10a40` passes 4 through `object 1 + 0x1d930` while a portrait opens, in [Text](text.md). The direct calls that were separated push 0, 8, 9, or 11.

To pull the pictures out: walk the VFS directory as described in [Archives](archives.md), reject a member whose span passes the end of the archive, then run mode 0 into a buffer of `width * height` bytes. A cell's bytes run from its table offset to the next higher offset in that table, and the last cell runs to the end of the member. A picture is the column count, the row count, then that many cell indexes, one row at a time. Stamp cell (column, row) at `chunk_x + column * cell_width`, `chunk_y + row * cell_height`. Pixels the skip opcodes never write stay transparent. The chunk x and y are positions in the 368×248 compose buffer, so a tight sprite is the bounding box of the written pixels, not the cell size. Hold, hit, and the mode byte stay beside the frame so a player can step it the way `object 1 + 0x4540` does.

`Fight.pal` and the other four `.pal` members of `MISC.VFS` (`Chapter.pal`, `Dynasty.pal`, `Fde.pal`, `Stboard.pal`) are 768 bytes with components 0 through 63. Shift each component left by 2 for an 8-bit channel. The string `Fight.pal` is at `object 2 + 0x1cd4`. `object 1 + 0x19630` opens it into `object 2 + 0x43e4`, and the fight players install that buffer through `object 1 + 0x12f10`, under [CEL pictures](#cel-pictures). Every cell in the fight clips below expanded with mode 0: each row's width counter landed on 0, and the cell size is 24×24 throughout. Colored from `Fight.pal`, frames of `BACK00`, `STAND000`, `ACT000`, `MAGIC000`, and `ML00` are readable pictures. `STAND000` frame 0's written pixels sit at compose `(181, 47)`. Chunk byte 1 still expands with mode 0. There are 44 such chunks in `FIGHT.VFS` (10 in `Stand`, 34 in `Magic`), 177 in `FIGACT.VFS`, none in `BACKGRND.VFS`, and 345 in the effect members of `MISC.VFS`. The fight paints those chunks with mode 9, so this recovers the stored indexes and not that blend. Chunk rectangles in `FIGHT.VFS` stay inside x 0..343 and y 0..223. `FIGACT.VFS` reaches x −1 and y 255. `BACKGRND.VFS` stays in y 28..150.

`scripts/extract_fight_sprites.py` is that walk. It writes one PNG per frame that has chunks, `sheet.png` for the clip, and a JSON record of hold, hit, sample, and the cropped origin. How the sheet is registered is under [SAF clips](#saf-clips). The folders are `backdrops/` (`Back##`), `stands/` (`Stand###`, the body drawn for the defender and for the attacker until the swing), `attacks/` (`Act###`), and `effects/`. A walk of the local archives wrote 63 backdrop frames, 388 standing frames, 2117 attack frames, and 3538 effect frames.

25 attack frames and 63 effect frames store a chunk count of 0. They are kept in the JSON and get no PNG, so the frame index still matches the file. The attack frames are in `ACT005` (3), `ACT020` (3), `ACT024` (2), `ACT060` (1), `ACT061` (1), `ACT062` (2), `ACT067` (2), `ACT070` (1), `ACT093` (3), `ACT094` (3), `ACT095` (3), and `ACT107` (1). Among the effect frames, `EE05`, `EE06`, `EE07`, `EE23`, `ME03`, `ME04`, `ME05`, `ME06`, `ME07`, `ME26`, `ME27`, `ME28`, `ME30`, `ME31`, `ME34`, and `ME35` are a whole file of one empty frame. The same `SAF` path covers the 67 `ICON####.SAF` members of `ICONANI.VFS`. Icon opcode 6 names `Icon%04d.saf` from the next script byte and plays the whole file, under [Map sprites](#map-sprites).

## SAF clips

Combat, spell, and backdrop pictures are `SAF` version `0x06`. `object 1 + 0x40e0(file, index)` returns one frame. `object 1 + 0x44d0` is the frame count. `object 1 + 0x4540` advances a cursor. `object 1 + 0x4140` blits the current frame into a compose buffer.

Header, little-endian:

| Offset | Field |
| --- | --- |
| 0 | `SAF` |
| 3 | version byte `0x06` |
| `0x0c` | `uint16` frame count |
| `0x0e` | `uint32` file offset of the frame-offset table (`count` dwords) |

Frame `i` begins at `file + dword[table + i*4]`. Inside a frame record:

| Offset | Field |
| --- | --- |
| `+0` | `int16` sample index. Below 0, or at or past the sample count, plays nothing. |
| `+2` | `int16` hold count, in ticks. The stepper increments a tick until it reaches this, then moves to the next frame. |
| `+4` | Byte read by the players. On frame 0 of an attack or spell clip, a nonzero value is how far to play a preamble before the hit sequence. |
| `+5` | Nonzero marks a hit frame. Damage is applied when the cursor lands on one. A clip whose strike phase has none of these aborts with `ERROR: No Hit Point`. |

`object 1 + 0x4540(cursor, mode)`: mode 1 resets the frame index and the tick to 0 and returns 0. Any other mode adds one tick. When the tick reaches the hold at frame `+2`, the index moves. When the index reaches the frame count, the call returns 1. Mode 0 then stores index 0. Any other mode stores the last frame. A frame count of 0 returns −1. The cursor is a pair: frame index, then tick-within-frame. The `SAF` check in that function is written as three comparisons joined by `||`, so it accepts more than the three bytes `S`,`A`,`F`.

One member is one sequence. Frame `i` is the record at `file + dword[table + i*4]`. Nothing else groups the frames. The hit byte, the preamble on frame 0, and the sample index mark events in that pass. They do not reorder it. The mode is the immediate pushed with the cursor, not a field in the file. Forty-one call sites push 0 and twenty push 1. Six push 2, each `mov eax, 2` then the same cursor, at `object 1 + 0xaad6`, `object 1 + 0xac89`, `object 1 + 0xb12d`, `object 1 + 0xb41b`, `object 1 + 0xb619`, and `object 1 + 0xb7e5`. The calls from the strike, `object 1 + 0x9874` through `object 1 + 0x9e8f`, push 0 or 1, so an attack cursor can wrap. A pass of the animation is still frame 0 through the last frame, each shown for its hold. `Stand` is the clip the idle row loops.

Cropped frames of one clip do not share an origin, so stacking the PNGs at (0, 0) moves the figure. `STAND000` has 3 origins inside a box at `(181, 47)` sized 132×152. `ACT000` has 12 origins inside a box at `(2, 42)` sized 318×158. The clamp is that box. Stamp frame `i` at `(x - box_x, y - box_y)`. `scripts/extract_fight_sprites.py` writes `sheet.png` on that grid, one cell per frame in table order, with a transparent cell where the chunk count is 0. The cell is the union of the written pixels. The last row can have unused cells after the frame count. Those are not frames. `clips.json` records the box and the grid.

`object 1 + 0x4140` blits one frame. Its second argument, when nonzero, calls `object 1 + 0x42d0` with the frame's sample index. That function returns unless `object 2 + 0x9d70` and `object 2 + 0x9d71` are both nonzero. It walks eight dwords at `object 2 + 0x9d30` and keeps the first whose status call is not 4. The sample record is `file + dword[sample_table + index * 4]`:

| Offset | Field |
| --- | --- |
| 0, 1 | Two bytes. `01 08` selects 0, `01 10` selects 1, `02 08` selects 2, and anything else selects 3. |
| `+2` | `uint16`. On `ACT000.SAF` the only sample stores 11025 here. |
| `+4` | `uint32` length of the bytes at `+8`. On that same sample the length is 4464 and the span fits in the file. |

The kept slot is one of the eight dwords at `object 2 + 0x9d30`. `object 1 + 0x2f26e` and `object 1 + 0x2ec6b` are called on that slot first. Those two bodies were not read. Then, in order: `object 1 + 0x2edde` is passed the slot, the bytes at `+8`, and the length, and the string it logs names `AIL_set_sample_address`. `object 1 + 0x2ee60` is passed the slot, the selector, and 2, and names `AIL_set_sample_type`. `object 1 + 0x2f1f8` is passed the slot and 1, and names `AIL_set_sample_loop_count`. `object 1 + 0x2f096` is passed the slot and the `uint16`, and names `AIL_set_sample_playback_rate`. `object 1 + 0x2eee2` is passed the slot and names `AIL_start_sample`. Each of the five increments `object 2 + 0x9e6c` and decrements it on the way out. When `object 2 + 0x9e80` is nonzero, and the count is 1 or `object 2 + 0x9e84` is nonzero, a zero from `object 1 + 0x34cb2` and a nonzero from `object 1 + 0x2d3e6` logs through `object 1 + 0x34ef3`. The same arguments are then forwarded: address to `object 1 + 0x37010`, type to `object 1 + 0x37040`, the loop count to `object 1 + 0x37150`, the rate to `object 1 + 0x37080`, and the start to `object 1 + 0x37160`. The three log calls were not read.

On a nonzero handle, `object 1 + 0x37010` stores the address at `+8` and the length at `+0x10`, and stores 0 at `+0xc` and `+0x14`. `object 1 + 0x37040` stores the selector at `+0x34` and the 2 at `+0x38`, and calls `object 1 + 0x35cc0` with the handle when either dword changes. That body was not read. `object 1 + 0x37080` stores the rate at `+0x3c`. `object 1 + 0x37150` stores the loop count at `+0x30`. Those two were disassembled. `object 1 + 0x37160` was disassembled. A zero handle returns. So does a handle whose dword `+4` is 1. Otherwise the dword at `+0x28` is an index, the entry is `handle + index * 4`, and a zero at `entry + 8` or `entry + 0x10` returns. The start stores 0 at `entry + 0x18` and 4 at `handle + 4`. The dword at `handle + 0` is the driver. When the driver's dword `+0x54` is 0, the start calls `object 1 + 0x2da33` with that driver's first dword, `0x401`, the words at driver `+0x14` and `+0x18`, and 0, then stores 1 at driver `+0x54`. The body of `object 1 + 0x2da33` was not read. The five `ACT` files checked (`ACT000` through `ACT004`) use sample indexes −1, 0, and 1 only. `ACT000` has one sample and points frame 5 at it; its hit marker is on frame 6.

Hold counts actually stored: every `STAND` frame is 4. `ACT` frames are mostly 2 (1296) or 1 (743), with a few 3, 4, 6, 7. `MAGIC` is the same shape.

Compose buffer for combat is `0x16480` bytes, pitch `0x170` (368), origin size stored as `0xf8`. The visible copy to the VGA is 320×200 from buffer+`0x2298`. Map composition uses `0x15180` bytes, pitch `0x168` (360). Sprites are drawn at 24×24.

## Combat animation

`object 1 + 0x8d50` builds the screen. `object 1 + 0x96b0` steps it. The pool math those hit frames apply is in [Combat](combat.md).

Before any frame, the two remap tables are replaced. `FMer1.tmp` is read into `object 2 + 0x53f0` (`0x4800` bytes) and `FMer2.tmp` into `object 2 + 0x43f0` (`0x1000` bytes). Both files on disk are exactly those sizes. `object 1 + 0x12f10` then writes VGA colors 0 through 255 from the block at `object 2 + 0x43e4`. After the fight the screen at `0xa0000` is cleared for 64000 bytes, the `Mer1.tmp` / `Mer2.tmp` pair is read back over the same two tables, and `object 1 + 0x12f10` writes the block at `object 2 + 0x43cc`.

Each `*1` file is 18 slots of 256 little-endian dwords, two banks of nine. That is the pair mode 9 swaps when the selector is above 8. Dword 0 of every slot is 0. The low byte of the other dwords takes 16 distinct values in a slot. Many dwords are not the same byte repeated three times. `Mer1.tmp` and `FMer1.tmp` differ in 10914 bytes. On the fight file, 43 entries of each slot are 0, and the other low bytes are multiples of that slot's step. On the map file, the low byte at index 1 is that step: 1 through 8 in the first bank, then 16 down to 8. Each `*2` file is the 4096-byte mixer the formula indexes. The two mixers differ in 4094 bytes. Index 0 contributing nothing is what leaves a stored 0 unmixed. Inferred: the other zero entries are palette indexes that do not take the tint, and the 16 steps are the blend weights.

Files, by character byte `+7` and by the defender's terrain byte 3 (decremented when it is nonzero):

| Picture | Archive | Name |
| --- | --- | --- |
| Both standing clips | `FIGHT.VFS` | `Stand%03d.saf` |
| Attacker's swing | `FIGACT.VFS` | `Act%03d.saf` |
| Defender's swing | `FIGACT.VFS` | loaded only when `object 1 + 0x37e0` returns 1 |
| Backdrop | `BACKGRND.VFS` | `Back%02d.saf` |
| Bars | `MISC.VFS` | `FIGBAR.CEL` |

`FIGBAR.CEL` uses the same header as `ICON.CEL`. Its three big-endian shorts are directory `0x0f`, width `0x91`, height `9`. The directory has eight pictures and a sentinel. Pictures 0..3 are about 213 bytes. Pictures 4..7 are 55 bytes. The fight copies 4..7 into a strip `0x7d` wide, each 5 pixels below the last. Pictures 0..3 are the frames drawn behind the fills.

If the attack clip's frame 0 has a nonzero byte at `+4`, the defender's backdrop is kept aside and a second backdrop is loaded from the attacker's tile. That byte is the preamble length. The intro then does not draw the defender.

Compose buffer is `0x16480` bytes, 368×248 at pitch `0x170`. Each displayed frame waits until bit 3 of port `0x3da` is clear and then set, copies 320×200 from buffer+`0x2298` to `0xa0000`, and waits until `object 2 + 0x9d64` changes. Buffer+`0x2298` is pixel (24, 24). The pictures are placed at (24, 24) in the buffer, so they sit at the top-left of the VGA window, and the extra 24 pixels on the left and top are the room the slide uses.

`object 1 + 0xba10` uses that same buffer, wait, and copy for the ending reel in [Session](session.md). It loads the fight remap tables first. Nine steps, counted from 8 down to 0, draw the backdrop at `(24, step * 20 + 24)` and the stand clip at `(step * 15 + 24, 24)`. Fifty frames then hold both at `(24, 24)` while the stand cursor advances. The act clip is drawn at `(24, 24)` until `object 1 + 0x4540` returns nonzero, which is one pass. The next 251 frames clear the buffer, draw the stand, and draw the scenario string at buffer `(24, 26)` through `object 1 + 0xff30` with pitch `0x170`, ink `0xd0`, fill 0, and shadow `0x6d`. The first eight of those frames also draw the backdrop in mode 9, with the selector equal to the frame number times 2. Nine further frames draw only the stand, in mode 9, with the selector equal to that frame number times 2. Each pass allocates the buffer. The free of that pointer runs once, after the loop.

One composed frame, back to front:

```
clear the buffer
blit backdrop at (24, y)
blit defender Stand at (x, y)          # omitted during the intro when a preamble is set
blit attacker Stand or Act at (x, y)
draw the two bars                        # object 1 + 0x92f0
```

The blit record passed to `object 1 + 0x4140` is 0x24 bytes: buffer, pitch, height `0xf8`, x, y, the `SAF`, the frame index, a dword, and a mode. While that mode dword is 0, a chunk whose byte is 0 uses expander mode 0 and a chunk whose byte is 1 uses mode 9. The mode-9 argument is `0x10` minus the short at chunk `+7`, and the two remap tables above are the pointers it is given. From the first landed hit onward the record's dword is `0x28000` and its mode is 3, for the defender's stand and for the attack clip.

Mode 3 is `object 1 + 0x46927`. The body is hand-written, like mode 0, and was disassembled. It is the same four opcodes. Each byte it writes is `((sample + DH) & AH) + DL`, and those three registers are loaded from the three low bytes of the dword at the caller's `EBP+0x1c`. `object 1 + 0x4664b` leaves that dword as its sixth argument, which this path sets to `0x28000`. The bytes are `00 80 02`, so the written index is `(sample & 2) + 0x80`. The row adjustment is `pitch - width`, saved from `EDX` and added after each row.

`object 1 + 0x94c0` is nine frames, the counter running from 8 down to 0. The backdrop's y is `step * 0x14 + 24`, so it moves from 184 up to 24. The attacker's x is `step * sign + 24`. Side byte `0` uses sign −15 and enters from the left. Any other side uses +15 and enters from the right. The defender, when drawn, stays at (24, 24).

`object 1 + 0x96b0` then plays the swing. A preamble, when frame 0's byte `+4` is nonzero, is that many attack frames drawn over the defender's backdrop with no standing clips. `object 1 + 0xa350` follows: eight frames slide one backdrop out and the other in by 40 pixels a frame, carrying the standing clip. Eight steps of 40 cover the 320-wide window. The sign is +1 for side `0` and −1 otherwise.

The strike loop clears the buffer and draws backdrop, shaking defender, then the attack frame. The defender's x offset is `sign * table[k]` and, when there was no preamble, the y offset is `sign * table2[k]`. `k` is set to 5 on a landed hit frame and then falls by 1 each composed frame until it stays at 0. The tables are six dwords:

| `k` | x at `object 1 + 0x8c50` | y at `object 1 + 0x8c68` |
| --- | --- | --- |
| 5 | 14 | 10 |
| 4 | 18 | 8 |
| 3 | 14 | 6 |
| 2 | 9 | 4 |
| 1 | 4 | 2 |
| 0 | 0 | 0 |

Side `0` uses sign +1. Any other side uses −1. The attack clip itself stays at (24, 24). The sample flag passed with it is 1 until a miss frame, which passes 0 and plays `Miss.wav` through `object 1 + 0x1a1c0` instead. A crit (dword 1 from `object 1 + 0x9f60`) also writes palette index 0 to `3f 3f 3f`, waits `0x32` on the same delay used before the fight, then writes index 0 as `00 00 00`.

Bars, from `object 1 + 0x92f0`, use the defender during the strike and the attacker as well when there was no preamble. Side `0` is anchored at buffer `(0x1e, 199)`, which is screen `(6, 175)`, and uses `FIGBAR` pictures 2 and 3 plus strip slots 2 and 3. Any other side is anchored at buffer `(0xc3, 0x20)`, screen `(171, 8)`, and uses pictures 0 and 1 plus strip slots 0 and 1. Each anchor draws the frame, a second frame 10 pixels lower, then two fills. The fill width is `(current * 0x7d + max - 1) / max`, so 125 pixels, 5 pixels tall. The pool at `+0x40` is the upper fill, two rows under the anchor. The pool at `+0x44` is twelve rows under it. Slots 0 and 1 are right-aligned: the copy starts at `0x7d - width`. Slots 2 and 3 grow from the left. This is not the 41-step bar in `object 1 + 0xcad0`.

After the last attack frame both standing clips are held for 12 composed frames, the defender's bar always and the attacker's bar only when there was no preamble. A second swing, when the count in [Combat](combat.md) says so and the pool is still above 0, runs `object 1 + 0xa350` again if a preamble was set and then repeats the strike. A counterattack is the same function with the clips swapped.

Per character id the body clips are:

| Clip | Files | Frames |
| --- | --- | --- |
| Idle `STAND###` | 94 | 4 on 91 of them, 8 on `STAND060`, `STAND061`, `STAND062`. Loops. The number is the character id: 0–12, 15–33, 35, 59–116, 118, 119, and 128. |
| Attack `ACT###` | 91 | 8 to 47, median 22. Every file has 1 to 6 hit frames. The same ids as `STAND`, without 118, 119, and 128. |
| Spell effect `MAGIC###` | 46 | 6 to 49, median 28. Ids 0–11, 15–33, 61–67, 72, 73, 101–104, 113, and 115. |
| Backdrop `BACK##` | 63 | 1 frame each. |

Spell attack, `object 1 + 0xa4a0(attacker, spellId, targetCount, targets)`. Spell ids `0x0a`, `0x0b`, `0x0e`–`0x16`, `0x18`, and `0x21` go to `object 1 + 0x188c0` instead of the sequence below.

For every other id the player loads, using side prefix `E` or `M` from byte `+6` and the spell id:

1. `Stand%03d` for the caster and each target, `Magic%03d` for the caster, `Back%02d`.
2. `%sB%02d.saf` played to completion (begin).
3. `%sL%02d.saf` (strike). Hit frames inside it drive the HP write. Zero hit frames aborts.
4. `%sE%02d.saf` played to completion (end).
5. `%sS%02d.saf` as an extra overlay when the spell id is `0x0d`, or in `0x1a`–`0x1f`, `0x21`–`0x24`, or `0x26`–`0x27`.

Those phase files live in `MISC.VFS`. Counts: `MB`/`ME`/`ML` 25 each, `MS` 11, `EB`/`EE`/`EL` 12 each, `EMG` 25, `ES` 1. The twenty-fifth `EMG` is `EMG33-1.SAF`, beside `EMG33.SAF`. `Emg%02d.saf` is formatted in `object 1 + 0x188c0`. The id is passed through, except id `0x0b`, which is formatted as id−1. Id `0x21` instead opens the separate string `Emg33-1.saf` at `object 2 + 0x1bc8` (`object 1 + 0x1898d`). The same function names `EarQu.wav`. Its callers are `object 1 + 0xa4a0` and `object 1 + 0x3c90`. The frames after the open are in [Combat](combat.md): ids `0x0a` and `0x0b` shake the camera for 25 redraws, id `0x0b` plays `Mag11.saf` first, and `object 1 + 0x16dd0` then draws the formatted clip on the map, twice per frame, at each target. The same archive also holds `CURE.SAF`, `CUREMP.SAF`, `MAG11.SAF`, `MAGIC0BB.SAF`, `MAGIC0GG.SAF`, `POSEFF.SAF`, and `POSION.SAF`. They use the same `SAF` version `0x06` layout and are included with the effect clips above. Six further `.saf` members are not fight effects. `Logo.saf` is the startup clip in [Session](session.md). `Chapter.saf` is played by `object 1 + 0x10c30`, which every scenario opener calls: one frame through `object 1 + 0x4140`, then `Chapter.pal` fades in and out by steps of 4. `EnyPhase.saf` and `PlyPhase.saf` are played by `object 1 + 0xead0` from the turn change in [Turns](turns.md). That player saves the screen, blends five steps through `object 1 + 0x1fda0` with the tables at `object 2 + 0x53f0` and `object 2 + 0x43f0`, plays the clip, and blends back. When the name is `PLYPHASE.SAF` it calls `object 1 + 0xe810` first. `GameOver.saf` is played by `object 1 + 0x1a920`: the clip steps with `object 1 + 0x4540` until that call returns nonzero, then sixteen blend steps run and the function waits on a key. `Bonus-1.saf` is opened, with `Bonus.wav`, by `object 1 + 0x261d0`, which the first village-menu action `object 1 + 0x25a30` calls. The frames inside `object 1 + 0x261d0` were not walked. While the strike plays, a target who is actually hit also cycles a small palette (`local_50` modulo 8) keyed by a 40-long table copied from `object 1 + 0x8cb0`.

## CEL pictures

Map sprites, portraits, and the interface windows are `CEL` files, not `SAF`. The header begins `CEL \x01`. On every file checked, byte 6 is 0 and byte 8 is 0 or 1. The bitmap width is byte 7, plus 256 when byte 8 is 1. The bitmap height is byte 9. When byte 8 is 0 this is the same pair of big-endian shorts [Map](map.md) calls width and height, so a section tile stays 24×24. When byte 8 is 1 those shorts read high: `VILLAGE.CEL` says 64×456 and the picture that mode 0 consumes is 320×200. `object 1 + 0x1d930(cel, index, dest, pitch, x, y, remap, mode)` is the blit that reads the size. It expands the picture at `dword[cel + index * 4 + 0x0f]` through `object 1 + 0x4664b`, with the width taken from the little-endian short at `cel + 7` and the height from the little-endian short at `cel + 9`. That width is byte 7 plus 256 times byte 8. The destination is `dest + x + y * pitch`. The size in the tables below is the one at which mode 0 consumes the picture.

The directory offset is the big-endian short at `+4`, and it is `0x0f` on every file checked. The dwords there are little-endian picture offsets. A picture is the bytes from one dword to the next. The uint16 at `+10` equals that picture count for every `.cel` in `MISC.VFS` and for `FACE.CEL`. It does not for `ICON.CEL`: the field is 128, and the ordered directory holds 1920 pictures.

`Fde.pal` is the palette the map and the shared interface are installed with. The name at `object 2 + 0x1a78` is opened at `object 1 + 0x13f05` into the global at `object 2 + 0x43cc`. `object 1 + 0x19630` opens the second copy of that name, at `object 2 + 0x1ccc`, into the same global, and opens `Fight.pal` into `object 2 + 0x43e4`. `object 1 + 0x12f10` writes one range of a 768-byte buffer to the DAC. For each index it adds the three bias arguments to the three component bytes, clamps each sum to 0..63, writes the index to port `0x3c8`, and writes the three bytes to port `0x3c9`. The standing installs of `object 2 + 0x43cc` and of `object 2 + 0x43e4` pass biases 0, 0, 0, so the file bytes are the DAC bytes. Other sites pass a bias on purpose. −64 on every channel, at `object 1 + 0x10cc6` and `object 1 + 0x20cdb`, clamps the palette to black. +63 on every channel, at `object 1 + 0xc8d8`, `object 1 + 0xc922`, and `object 1 + 0x1884f`, clamps it to white. `object 1 + 0xc714`, and the same instruction at `object 1 + 0xc75e`, `object 1 + 0xc800`, and `object 1 + 0xc84a`, passes −64, +64, −64. `Chapter.pal` is opened at `object 1 + 0x10c54` and installed at `object 1 + 0x10d74` with bias `-step * 4` on each channel.

The two palette files share 2 of 256 entries. Coloring these pictures from `Fight.pal` is what shifts them red. On `ICON.CEL` character 1, frame 0, index 143 is the most common written pixel: `Fde.pal` stores `03 03 03` there and `Fight.pal` stores `19 07 00`. The same substitution moves the other indexes those pictures use. `scripts/extract_cel_pictures.py` colors icons, tiles, portraits, and the interface from `Fde.pal`, and writes character sheets under `maps/icons`, section tiles under `maps/tiles`, portraits under `maps/faces`, and the interface files under `ui`. The labeled contact sheet of character id, portrait, and map frame 0 is [extract/unit-ids](extract/unit-ids/index.html).

`STBOARD.CEL` is opened at `object 1 + 0x1a56e`. `StBoard.pal` is opened at `object 1 + 0x1a585` and installed at `object 1 + 0x1a5ac` with biases 0, 0, 0. That picture is colored from `StBoard.pal`. `FIGBAR.CEL` is opened at `object 1 + 0x8de6` and `object 1 + 0xa5cb` into `object 2 + 0x4004`, inside the fight players that install `Fight.pal`. The blit is under [Combat animation](#combat-animation). Coloring the bar from `Fight.pal` follows that install. No separate palette is opened for the bar.

## Map sprites

`object 1 + 0x13020` seeks to `0x0f` in `ICON.CEL` and reads `0x2970` bytes. The ordered dwords there increase through index 1920, where the dword equals the file size. 1920 / 12 = 160, so characters 0 through 159 each have 12 frames and a following offset. Frame `i` is `file[offset[i] : offset[i + 1]]`. The 1921 dwords end at file offset 7699, which is also where offset 0 points, so the `0x2970` read runs past the table into the first picture. There is no character 220 in the file. `object 1 + 0x13020` is called with the character id as its first argument. At `object 1 + 0x13613` that push is the id just read from the scenario record. The other six call sites push the byte at `+7`. It multiplies that argument by 12 and copies pictures `id * 12` through `id * 12 + 11` into a cache at `object 2 + 0x138`. The byte it returns is the cache slot stored at unit `+2`, which is what the drawer multiplies, so the slot is not itself the character id. Frame bytes are compressed: character 0's frames are 334–424 bytes, not `24*24`, and frame 0 of that character expands with mode 0 to a 24×24 picture. `object 1 + 0x4664b` expands a frame onto the map buffer at 24×24. Mode 0 of that expander is the opcode loop above. The string `Fde.pal` is at `object 2 + 0x1a78`. How it reaches the DAC is under [CEL pictures](#cel-pictures).

Ids 0 through 8, 15 through 23, and 24 through 32 expand to the same nine sheets, in that order. Id 33 and id 36 repeat id 0, and id 116 repeats id 3. Four further sheets are shared: 37 with 118, 38 with 119, 39 with 129, and 59 with 91. Mode 0 writes no pixel for ids 34, 40–51, 53–56, and 157–159. Every frame is already a 24×24 cell, so a character's sheet is four rows of three frames with no origin to correct. Row is the facing in the table below. The three columns are steps 0, 1, and 2. The walk shows 0, 1, 2, 1. Section tiles are the same 24×24 mode-0 pictures; which section files follow the packed directory is in [Map](map.md). `ICONANI.VFS` is a second set of icon clips. Icon opcode 6 names which file plays, in [Scenario files](scenario.md). `object 1 + 0x12290` plays that file on the map. It allocates the `0x15180` compose buffer and builds the blit record as buffer, pitch `0x168`, height `0xf0`, origin `(0x18, 0x18)`, the file, then the frame index. The mode dword stays 0, so a chunk byte of 0 uses expander mode 0 and a chunk byte of 1 uses mode 9, the same choice as a fight frame. For every frame, and for every tick of the hold at frame `+2`, it recomposes the map, blits that frame with the sample flag set, waits until bit 3 of port `0x3da` falls and rises, copies the 312×192 window, and waits until `object 2 + 0x9d64` changes.

`object 1 + 0x1cb30` picks the picture:

```
index = slot * 12 + facing * 3 + step
```

`slot` is unit byte `+2`. `facing` is byte `+3`. `step` comes from a global tick `object 2 + 0x9cc8`, which runs 0…15 and is divided by 4. The value 3 is replaced with 1, so the walk is frames **0, 1, 2, 1** of that facing.

| Facing | Movement applied to the sprite | Frame row |
| --- | --- | --- |
| 0 | +Y, 4 pixels times byte `+4` | 0–2 |
| 1 | −X | 3–5 |
| 2 | −Y | 6–8 |
| 3 | +X | 9–11 |

Bit `0x80` of byte `+5` draws the next frame of that facing through mode 11, selector 8. A character id of `0x24` through `0x27`, `0x69`, or `0x6a` draws the ordinary frame through mode 9, selector 7. Any other id uses mode 0. Byte `+0x26` nonzero forces step 0 and adds `tick % 2` to x.

The pass before the sprite paints `SHADOW.CEL` from `object 2 + 0x43e0`. The picture is the step, 0, 1, or 2, except that flag `0x80` forces picture 1. It is 24×24, expander mode 9, selector 10, and its top is two rows below the sprite's top. The file holds 14 pictures. This pass uses the first three.

`object 1 + 0x1ca60` (unit, `object 2 + 0x168`) then picks a 24×11 mark from `ICONSTS.CEL` at `object 2 + 0x43d8`. `object 2 + 0x168` increases by 1 at the start of each sprite. The five bytes tested, in picture order, are `+0x23`, `+0x22`, `+0x24`, `+0x25`, and `+0x27`. A byte of 0 is skipped. No nonzero byte returns −1 and nothing is drawn. Otherwise the tick modulo the nonzero count selects one of those bytes, and the returned index is its place in that list. The mark is mode 0, 24 wide and 11 tall, and its top is 12 rows below the sprite's top.

`FACE.CEL` is the same directory. Byte 8 is 0, the bitmap is 125×100, and the count at `+10` is 160, matching the directory. `object 1 + 0x77c0(dest, pitch, index)` frees any picture it loaded before. An index of −1 stops there. Any other index reads the two dwords at file `0x0f + index * 4`, loads that span, and expands it with mode 0 at 125×100 onto `dest` at the given pitch. The call at `object 1 + 0x107d8` is inside `object 1 + 0x10580`, and the index it passes is that function's argument. The chest reader passes unit `+7`. Calls that push an immediate use a value from 0 through `0x81`. Picture `n` is character `n`. Portraits of 3 and 116 match, as do 122 and 146, 125 and 139, and 137 and 159. Mode 0 writes no pixel for 34, 36–51, 53–58, 132–136, 141–145, and 147–158. The call at `object 1 + 0x10c1b` is the portrait finish in [Text](text.md). The call at `object 1 + 0x6790` was not read.

## Interface pictures

`object 1 + 0x19630` loads the shared interface from `MISC.VFS`. These are the `.cel` members. The bitmap is the size from [CEL pictures](#cel-pictures), and mode 0 consumes every picture.

| File | Pictures | Bitmap | What the name lines up with |
| --- | --- | --- | --- |
| `CUSOR.CEL` | 20 | 24×24 | cursor |
| `COMMAND.CEL` | 76 | 25×22 | command window |
| `NUMBER.CEL` | 65 | 6×8 | digits |
| `SELBAR.CEL` | 3 | 151×17 | selection bar |
| `MESSAGE.CEL` | 1 | 302×73 | message box |
| `SHOPWIN.CEL` | 1 | 312×76 | window |
| `LOADKON.CEL` | 3 | 300×49 | |
| `SHADOW.CEL` | 14 | 24×24 | shadow |
| `ICONSTS.CEL` | 5 | 24×11 | |
| `LEVUP.CEL` | 1 | 164×66 | level-up picture |
| `BAR.CEL` | 3 | 117×8 | bars |
| `EASYBAR.CEL` | 3 | 43×6 | bars |
| `FIGBAR.CEL` | 8 | 145×9 | fight bars, under [Combat animation](#combat-animation) |
| `STSEL.CEL` | 12 | 85×8 | |
| `CANBAN.CEL` | 7 | 72×24 | |
| `ADWIN.CEL` | 1 | 43×55 | |
| `WINFAIL.CEL` | 1 | 209×133 | |

`object 1 + 0x19630` stores the open result at the global named beside the file:

| File | Global | What uses it |
| --- | --- | --- |
| `Fde.pal` | `object 2 + 0x43cc` | Map and interface palette. |
| `Fight.pal` | `object 2 + 0x43e4` | Fight palette. |
| `Cusor.cel` | `object 2 + 0x43c8` | Cursor and the range marks in [Combat](combat.md). |
| `Command.cel` | `object 2 + 0x43c4` | Command window. |
| `Shadow.cel` | `object 2 + 0x43e0` | The map shadow above. |
| `IconSts.cel` | `object 2 + 0x43d8` | The 24×11 mark above. |
| `Message.cel` | `object 2 + 0x43b4` | Message box. |
| `Number.cel` | `object 2 + 0x43dc` | Digits. |
| `SelBar.cel` | `object 2 + 0x43a8` | Selection bar. |
| `LevUp.cel` | `object 2 + 0x43a0` | Level-up picture. |
| `ADWin.cel` | `object 2 + 0x43c0` | The terrain panel in [Turns](turns.md). |
| `BaseWav.vfs` | `object 2 + 0x43ac` | |
| `BaseAni.vfs` | `object 2 + 0x43bc` | |
| `EasyBar.cel` | `object 2 + 0x43a4` | Decoded 43×6 picture. |
| `Bar.cel` | `object 2 + 0x43b0` | Decoded 117×8 picture. |

The other windows are opened later. `object 1 + 0x6830` opens `Status.cel`. `object 1 + 0x7c90` names `WinFail.Cel` at `object 1 + 0x7d30`. `object 1 + 0x141b0` opens `Save.cel`. `object 1 + 0x14460` opens `Load.cel`. `object 1 + 0x14620` opens `LoadKon.cel`. `object 1 + 0x1a280` opens `StSel.cel` and `StBoard.cel`. `object 1 + 0x20f80` opens `ShopWin.Cel` and `Village.cel`. `object 1 + 0x21930` opens `CanBan.cel`. `object 1 + 0x255d0` opens `Item.cel`. `object 1 + 0x25810` opens `Church.cel`. `object 1 + 0x25a30` opens `BarShop.cel`. `object 1 + 0x25d40` opens `Weapon.cel`. `object 1 + 0x25f80` opens `Secret.cel`. `object 1 + 0x29be0` opens `Relive.cel`. `FIGBAR.CEL` is opened at `object 1 + 0x8de6` and `object 1 + 0xa5cb`, inside the fight players.

Byte 8 is 1, and the bitmap is 320×200, for `VILLAGE.CEL`, `STATUS.CEL`, `STBOARD.CEL`, `LOAD.CEL`, `SAVE.CEL`, `BARSHOP.CEL`, `CHURCH.CEL`, `ITEM.CEL`, `WEAPON.CEL`, `SECRET.CEL`, and `RELIVE.CEL`. Each is one picture. `STBOARD.CEL` is colored from `StBoard.pal`, and `FIGBAR.CEL` from `Fight.pal`, as under [CEL pictures](#cel-pictures). The other files in this list are colored from `Fde.pal`.

## The map window

`object 1 + 0x1f080(src, srcPitch, dest, destPitch, width, height)` copies `height` rows of `width` bytes. A source pitch of 0 repeats the same source row. Any other source pitch advances both pointers by their pitches. After the command icons, and again on the message path, the call is `object 1 + 0x1f080(buffer + 0x21d8, 0x168, 0xa0504, 0x140, 0x138, 0xc0)`. `0x21d8` is column 24 of row 24 in the 360-wide compose buffer. `0xa0504` is column 4 of row 4 on the 320-wide surface at `0xa0000`. The copied rectangle is 312×192, so four pixels remain on each side of the 320×200 picture. A point at buffer `(x, y)` lands on that surface at `(x - 20, y - 20)`. The phase transition's 320×200 copy of the same origin is in [Map](map.md).

`object 1 + 0x107f0` dismisses the message box after the confirm in handler 21, in [Scenario files](scenario.md). `object 1 + 0x2d0e5` returns a block of the size it is passed: the map block is `0x15180`, two screen blocks are 64000, and the box is `0x561e`. `object 1 + 0x1bcf0` composes the map block. `object 1 + 0x1f080` copies the 312×192 window from that block at `+0x21d8` into the first screen block at `+0x504`. `object 1 + 0x1d930` expands picture 0 of `Message.cel`, the pointer at `object 2 + 0x43b4`, into the `0x561e` block at pitch `0x12e`, so the picture is 302×73. `object 1 + 0x32a40` fills a block with the byte it is passed, and `object 1 + 0x2d284` copies its count from the second pointer onto the first. `object 1 + 0x2d1e8` releases each block. The six y values at `object 1 + 0xfd38` are 190, 170, 150, 135, 127, and 120, and the loop reads them from the last back to the first. The blended height is the smaller of `200 − y` and `0x49`. Each step calls `object 1 + 0x1ffc0` with the two remap tables, selector 15, 13, 11, 9, 7, then 5, at screen x 9. That blitter was not decompiled. Each step waits until bit 3 of port `0x3da` is set and then clear, and copies the screen to `0xa0000`. After the six steps the plain window is copied there.

`object 1 + 0x5bd0` writes palette indexes 8 through 15. It waits until bit 3 of port `0x3da` is set. When `object 2 + 0x3fbc` differs from the tick `object 2 + 0x9d64`, it stores the tick and writes eight entries. The phase at `object 2 + 0x14` selects the first of those eight bytes, then decreases, and −1 wraps to 15. The three channels are 24 bytes each, at `object 1 + 0x4730`, `object 1 + 0x4748`, and `object 1 + 0x4760`. Byte 23 of each run is past the window. The bytes are:

| Channel | 24 bytes |
| --- | --- |
| 0 | `0e 0b 08 05 03 02 00 00 00 00 03 05 08 0b 0e 0e 0b 08 05 03 02 00 00 00` |
| 1 | `2a 25 21 1e 1a 15 12 0e 0e 12 15 1a 1e 21 25 2a 2a 25 21 1e 1a 15 12 0e` |
| 2 | `1a 15 10 0c 08 04 02 00 00 02 04 08 0c 10 15 1a 1a 15 10 0c 08 04 02 00` |

`object 1 + 0x32a28` writes one byte to a port. The index goes to port `0x3c8` and the three channel bytes go to port `0x3c9`.

`object 1 + 0x1e840` is the other pulse on that poll. It returns when `object 2 + 0x9d20` already equals the tick, and otherwise stores the tick there. It also calls `object 1 + 0x209c0`, in [Turns](turns.md). The phase at `object 2 + 0x9d24` increments once per tick and wraps at the period below. The step is that phase divided by 4. `object 1 + 0x1efd0` waits until bit 3 of port `0x3da` is set, then writes that many entries from the first index, three bytes a step. Indexes other than the ones in this table store the tick and write nothing. The channel bytes are copied from `object 1 + 0x1b030` and were not split per scenario.

| Scenario | Period | Entries | First index |
| --- | --- | --- | --- |
| 0, `0x1a` | `0x14` | 5 | `0xf0` |
| 2, `0x14`, `0x16`, `0x1d` | `0x3c` | `0xf` | `0xf0` |
| 8 | `0x24` | 9 | `0xf6` |
| `0x15` | `0x1c` | 7 | `0xf8` |
| `0x17` | `0x2c` | `0xb` | `0xf0` |
| `0x1b`, `0x1c` | `0x28` | `0xa` | `0xf5` |

`object 1 + 0x5850` draws the four command pictures around the cursor, into that buffer, then performs this copy. It calls `object 1 + 0x1bcf0` first, so the icons sit on a fresh map frame. The step argument is multiplied by the float `0.06544979` stored by the `mov` at `object 1 + 0x585a`. The call at `object 1 + 0x5887` reaches `fcos` at `object 1 + 0x329aa`, and the call at `object 1 + 0x58b1` reaches `fsin` at `object 1 + 0x329b4`. Each result is multiplied by the step again and rounded by `frndint` in the callee at `object 1 + 0x2d25c`. With `cos` and `sin` those rounded offsets, and with the cursor minus the camera (`object 2 + 0x9cd4` − `object 2 + 0x9ce4`, `object 2 + 0x9ccc` − `object 2 + 0x9ce0`), the four corners are:

| Corner | Position |
| --- | --- |
| 0 | `(cx − cos, cy − sin)` |
| 1 | `(cx − sin, cy + cos)` |
| 2 | `(cx + sin, cy − cos)` |
| 3 | `(cx + cos, cy + sin)` |

A picture is drawn when its x is from −24 through 334 and its y is from −24 through 214. Both pictures come from `COMMAND.CEL` at `object 2 + 0x43c4`, 25×22, expander mode 0. The top-left in the compose buffer is the corner plus `(24, 24)`, which is the corner plus `(4, 4)` on the 320-wide surface. The frame index is `0x1a` when the highlight argument equals the corner, and `0x1b` otherwise, plus the corner's entry in the second table. The glyph index is the first table's entry plus the second table's entry times `0x24`.

The body at `object 1 + 0x6120` was disassembled. It calls `object 1 + 0x5850` with steps 1, 5, 9, 13, 17, `0x18`, and `0x19`, and each call recomposes the map and copies the window. The close, `object 1 + 0x61a0` in [Turns](turns.md), walks the same circle back through steps `0x17`, `0x13`, `0x0f`, `0x0b`, `0x07`, and `0x03`. Step `0x18` rounds to a right angle, so the offsets are 0 and 24 and the four pictures sit up, left, right, and down from the cursor. The second table copied by each menu below is four zeros, so the frame is picture 26 or 27 and the glyph is the first table as listed, in corner order:

| Menu | Glyphs (up, left, right, down) | Where it is opened |
| --- | --- | --- |
| `object 1 + 0x4aa0` | 22, 11, 12, 19 | No unit under the cursor, in [Turns](turns.md). The four dwords are at `object 1 + 0x46d0`. |
| `object 1 + 0x4e90` | 23, 9, 10, 8 | Called from `object 1 + 0x4aa0` at `object 1 + 0x4b64`. The dwords are at `object 1 + 0x46f0`. |
| `object 1 + 0x5460` | 3, 2, 1, 0 | The player's unit, in [Turns](turns.md). The dwords are at `object 1 + 0x4710`. |
| `object 1 + 0x15280` | 7, 4, 6, 5 | Called from `object 1 + 0x5cf0` at `object 1 + 0x6056`. The dwords are at `object 1 + 0x14d20`. |

When `object 1 + 0x1d830` does not return −1, that unit is redrawn with `object 1 + 0x1cb30` before the copy.

`object 1 + 0x70b0` waits while text is up, and it is the call that passes expander mode 8. The key read is in [Text](text.md). While `object 1 + 0x78e0` returns a value above `0x7f`, and when `object 1 + 0x32a68() % 200` is 0, a counter runs up from 0 and the speaker's map sprite is drawn into a 64000-byte scratch at x `0xa1`. The generator is in [Combat](combat.md). For counter values 0 through 14 the picture is mode 8 at y taken from the fifteen dwords at `object 1 + 0x4808`: 15, 30, 70, 105, 140, 170, 150, 130, 150, 170, 160, 165, 165, 160, 170. Values 15 through 24 stay on mode 8 at `(0xa1, 170)`. Later values use mode 0: the frame `0x24` bytes further into that icon's cache, then the frame `0x0c` bytes further, then the frame `0x18` bytes further while y starts at `0xaa` and falls by 4. The icon cache stride `param * 0x30` is the 12-frame set, so those three distances are facings 3, 1, and 2.

At `object 1 + 0x10002`, inside `object 1 + 0xff30`, `object 1 + 0x1d930` draws picture 0 of `MESSAGE.CEL` at buffer `(29, 140)`, pitch `0x168`, mode 0. That draw is the page word `0xfffd` in [Text](text.md). The file is 302×73, so on the 320-wide surface the box is `(9, 120)`. The same function then expands a 125×100 picture from `object 2 + 0x120` at buffer `+ 0x9ad0`, which is buffer `(32, 110)` and surface `(12, 90)`, mode 0, and copies the window with the call above.

`object 1 + 0x7520(dest, pitch, value, width, signed)` expands `NUMBER.CEL`. The arithmetic is that function. The template at `object 1 + 0x4844` is the five bytes `%.3d`. The `"%d"` is at `object 2 + 0x15a8` and the `"+"` is at `object 2 + 0x15ac`.

```
if width == 0:
    text = sprintf("%d", value)
else if value < 10 ** width:
    fmt = "%.3d"
    fmt[2] = '0' + width          # "%.Nd", zero-padded to width digits
    text = sprintf(fmt, value)
else:
    text = "?" * width
if signed and value >= 0:
    text = "+" + text
for i, ch in enumerate(text):
    glyph = ch - '0'              # '0'..'9'
    if ch == '+': glyph = 10
    if ch == '-': glyph = 11
    if ch == '?': glyph = 12
    if ch is none of those: glyph = 0
    picture = object 2 + 0xc * 13 + glyph
    expand that picture at dest + i * 6, 6×8, mode 0
```

`NUMBER.CEL` has 65 pictures, five rows of those 13 glyphs. `object 2 + 0xc` is the row. The status sheet below sets row 3 while a pool is not at its maximum, and row 1 while the matching count byte is nonzero, and puts the row back to 0 after the number. Rows 2 and 4 are not selected there. Other stores of the byte were not walked.

The item-list drawer at `object 1 + 0x14e70` draws `SELBAR.CEL` picture 0 at `object 1 + 0x14eb3`: x is 0, y is `8 + row * 17`, mode 0, and the pitch and destination are that function's arguments. The picture is 151×17, so the step is the picture height.

## The status sheet

`object 1 + 0x6a90` is the status window. It returns at once for character ids `0x24` through `0x27`. Otherwise `object 1 + 0x6830` opens `Status.cel`, the 320×200 picture, `OpWin1.wav` is played, and the VGA screen is saved. `object 1 + 0x62f0` stamps the sheet onto that picture at pitch `0x140`. The coordinates are pixels on the 320-wide picture.

| What | Where | Digits |
| --- | --- | --- |
| Map frame 0 of the icon cache | `(161, 10)` | 24×24, mode 0 |
| Portrait, character id `+7` | `(19, 4)` | `FACE.CEL`, 125×100 |
| Interface string `byte +8 + 1` | `(201, 5)` | ink `0xd0`, shadow `0x6d` |
| Interface string `+0x20 + 0xa1` | `(192, 23)` | class |
| Interface string `+0x1f + 0x97` | `(263, 23)` | the byte drawn as string `value + 0x97` in [Units](units.md) |
| Word `+0x40`, then word `+0x42` | `(88, 122)`, `(117, 122)` | 4. Row 3 while they differ |
| Word `+0x44`, then word `+0x46` | `(88, 141)`, `(117, 141)` | 4. Row 3 while they differ |
| Byte `+0x21` | `(62, 155)` | 2 |
| Byte `+0x3b` | `(118, 155)` | 2 |
| Byte `+0x3c` | `(56, 164)` | 3. A stored `0xff` is replaced with 1000, which does not fit three digits, so the drawer writes `???` |
| Word `+0x3e` | `(112, 164)` | 3. Row 1 while byte `+0x24` is nonzero |
| Word `+0x4e` | `(56, 173)` | 3, same row |
| Word `+0x4c` | `(56, 182)` | 3, same row |
| Word `+0x48` | `(112, 173)` | 3. Row 1 while byte `+0x22` is nonzero |
| Word `+0x4a` | `(112, 182)` | 3. Row 1 while byte `+0x23` is nonzero |

`object 1 + 0x7730(dest, pitch, picture, width)` draws one bar from `BAR.CEL`, the pointer at `object 2 + 0x43b0`. A picture is `0x3a8` bytes, 117 by 8. When `width` is above 0, `object 1 + 0x1f120` copies the left `width` columns of that picture, source pitch `0x75`. A negative width is stored as 0. When `width` is below `0x75`, the same call copies picture 0 from column `width`, for `0x75 − width` columns, onto `dest + width`. `object 1 + 0x1f120(src, srcPitch, dest, destPitch, width, height)` writes a source byte only when it is not 0. The width is `(current * 0x75 + maximum - 1) / maximum` when the maximum is at least 1, and 0 otherwise. The first pool uses picture 1 at `(22, 118)`. The second uses picture 2 at `(22, 137)`.

A 151×149 rectangle at `(152, 47)` is kept aside, and `object 1 + 0x14e70` draws the eight item pairs there with the selection row set to −1, so no bar is drawn. `object 1 + 0x6e70` then runs for steps 0 through 8. The first argument is the saved VGA screen. The second is the picture `object 1 + 0x6830` returned. The third is the step. The body copies the first argument into a 64000-byte block, then copies four rectangles of the second argument onto it with `object 1 + 0x1f080`, calls `object 1 + 0x33a20(0xf)`, waits until bit 3 of port `0x3da` is set and then clear, copies the block to `0xa0000`, and frees it. Pitch is `0x140`.

The left upper piece is `0x6c` rows. The nine dwords at `object 1 + 0x4778` are `−0x78`, `−0x64`, `−0x46`, `−0x28`, `−0xf`, `0xf`, `0xe`, `0xe`, `0xf`. A negative entry sets the width to `entry + 0x85` and the destination x to 0, and the source x is `0x94 − width`. Any other entry sets the width to `0x85`, the destination x to the entry, and the source x to `0xf`.

The left lower piece uses the nine dwords at `object 1 + 0x479c`: `0xbe`, `0xaf`, `0xa0`, `0x8c`, `0x7d`, `0x6c`, `0x6d`, `0x6d`, `0x6c`. The source is `(15, 108)`. The destination is `(15, entry)`. The width is `0x85`. The height is `200 − entry`.

The right body is `0x9c` rows. The nine dwords at `object 1 + 0x47c0` are `0x12c`, `0x10e`, `0xf0`, `0xd7`, `0xaf`, `0x94`, `0x95`, `0x95`, `0x94`. The source is `(148, 44)`. The destination x is the entry and the destination y is 44. The width is the smaller of `0x140 − entry` and `0x9e`.

The right header is `0x9e` columns. The nine dwords at `object 1 + 0x47e4` are `−0x24`, `−0x20`, `−0x18`, `−0x10`, `−8`, `0`, `−1`, `−1`, `0`. The height is `entry + 0x2c`. The source is `(148, 0x2c − height)`. The destination is `(148, 0)`.

`object 1 + 0x70b0` waits, which is the key read in [Text](text.md). On the way out, `object 1 + 0x68d0` is called with the status picture and the saved screen, and that call runs this blit for steps 5, 4, 3, 2, 1, and 0. The rest of `object 1 + 0x68d0` was not read.

When the unit has spells, that rectangle is revealed on the VGA screen at the same `(152, 47)` through `object 1 + 0x1fbd0`, the margin stepping 2, 4, 6, 8, 10. `object 1 + 0x176c0` draws the list, and the same margins run back down. More than eight spells blends a second page through `object 1 + 0x1ffc0` with selectors 1, 3, …, 15 and the two remap tables. Both of those blitters were not decompiled.

## The level-up card

The rising number and the card are `object 1 + 0xdd00`, whose level rule is in [Combat](combat.md). Before the card, `COMMAND.CEL` picture `0x23` is drawn into a buffer of pitch `0x28`, and `object 1 + 0x7520` writes the experience term at x `0x12` with width 0. For steps 6, 8, …, 34 a 40×8 strip of that buffer is copied onto the map. The x is the unit's sprite x. The y is the sprite's y plus 8, minus the step, and the step stops at 24. The copy passes the two remap tables and the selector `min(step, 24) / 3 + 8`. `object 1 + 0x200f0`, which does that copy, was not decompiled.

`LevUp.cel` is one 164×66 picture, drawn at pitch `0xa4`. It is copied to map buffer `(98, 88)`, which is screen `(78, 68)`, and held while `object 1 + 0x4652e` returns a byte of `0x80` or above, for at most 250 ticks. The unit's map frame is drawn at buffer `(168, 101)`, screen `(148, 81)`, and the frame steps 0, 1, 2, 1 from `tick % 16 / 4`.

On the card, from `object 1 + 0xdd00` and `object 1 + 0xe340`:

| What | Card pixel |
| --- | --- |
| New level, byte `+0x21`, width 0 | `(38, 16)` |
| Amount added to `+0x37`, class-row bytes 0 and 1 | `(147, 16)` |
| Amount added to `+0x42`, bytes 6 and 7 | `(38, 26)` |
| Amount added to `+0x39`, bytes 2 and 3 | `(147, 25)` |
| Amount added to `+0x46`, bytes 8 and 9 | `(38, 35)` |
| Amount added to `+0x3e`, bytes 4 and 5 | `(147, 34)` |
| Interface string `learned id + 0x1be`, when a pair matches the level | `(72, 45)` |

Each amount is the roll in [Combat](combat.md), stored at `object 2 + 0x4038` and drawn with width 0. The pitch of those draws is `0xa4`.

## A screen a new engine can keep

This section is a design reading of the layout above. It is not code in the program, and the game was not run.

The program has one 320×200 indexed picture. A new engine keeps that logical size and scales it, nearest-neighbor, so a 24×24 tile stays a tile. It does not keep the VGA ports or the retrace wait. The compose buffers are larger than the picture only so a slide and a camera have room: the map shows 312×192 from buffer `(24, 24)` at screen `(4, 4)`, and the fight shows 320×200 from buffer `(24, 24)`.

Three pictures, back to front.

A map visit is the terrain, then the shadow, the unit, and the 24×11 mark, then the range and the cursor, then whatever window is up. The command diamond is four 25×22 pictures on a circle of radius 24 around the cursor. The seven steps are the circle closing; the resting position is up, left, right, and down. A new menu can keep the four corners and drop the spin. The message is a 302×73 box at screen `(9, 120)` and a 125×100 portrait at `(12, 90)`. The terrain panel is the 43×55 picture in [Turns](turns.md), and it moves to the other side of the cursor so it does not cover the unit.

A fight is a cleared buffer, the backdrop, the defender's stand, the attacker's stand or swing, then the two bars. Each bar is a frame, a second frame 10 pixels lower, and two fills 125 pixels wide. The fill width is `(current * 125 + maximum - 1) / maximum`. One side grows from the left at screen `(6, 175)`. The other grows from the right at `(171, 8)`. The slide, the shake, and the white flash on a critical hit are the motion. The hit marker on a frame is when the number changes, not a separate picture.

A town screen, the status sheet, and the save slots replace the picture with one 320×200 `CEL` and stamp text and digits at fixed pixels. The status pixels are the table above. The spell list is the 151×149 rectangle at `(152, 47)`; the wipe is the list appearing, and a second page is the same rectangle again. Nothing in these screens reflows. A wider window is the same 320×200 picture scaled up, not a new layout.

What stays data:

- A frame is a texture. Pixels the skip opcodes never write are transparent. The extracted PNG is that texture.
- Three palettes, chosen by the screen: `Fde.pal` for the map and the interface, `Fight.pal` for the fight, `StBoard.pal` for the board that opens with it. Components in the file are 0 through 63.
- A clip is the frame list already in the `SAF`: hold ticks, the hit marker, the sample index. One member is one sequence. Cropped frames of one clip share the box recorded by the extractor, not the origin `(0, 0)`.
- Glyphs are a 16×16 atlas, advance 16, line step 18, shadow one pixel down and right. The control words in [Text](text.md) are still the string format. A page is the message box. A portrait word is the portrait at `(12, 90)`.
- Digits are the 6×8 atlas, five rows of thirteen glyphs. Row 0 is the ordinary number. Row 1 marks a count that is changing a stat. Row 3 marks a pool that is not full.
- The tick those hold counts use becomes a fixed timestep. A sample starts when its frame is shown.

What the blend tables were doing, and what replaces them. Mode 9 mixes a source index with the pixel already there, and the selector from 0 through 16 picks the ramp. A new engine can use a straight alpha of `selector / 16` on the texture, and keep index 0 transparent. That matches the selector the map pulse, the fight chunk, and the rising number already pass. The 18 ramps and the 4096-byte mixer are the pixel-identical version of that mix. A remake does not need them. The strike flash, mode 3, is the written index `(sample & 2) + 0x80` for the frames after the first hit. A white flash of the same sprites is the same moment.

The sample wrappers are in [SAF clips](#saf-clips). A player that starts that span when the frame says so is the sound the clip carries. Named waves such as `Miss.wav` and `Levup.wav` are separate cues, not frames.
