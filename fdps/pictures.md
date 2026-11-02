# Pictures

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. The damage number these clips apply is in [Combat](combat.md).

## Drawing a battle, and extracting the pictures

`FUN_000194c0` slides the two standing clips in from the side over nine composed frames before `FUN_000196b0` plays the attack. Side byte `0` enters from the negative x direction (`-15` per frame) and any other side from the positive. The compose buffer is `0x16480` bytes, pitch `0x170`, and each frame is copied to `0xa0000` as 320×200 from buffer+`0x2298`, between two waits on bit 3 of the value `FUN_0003d254(0x3da)` returns. That is the vertical-retrace test. A landed hit still does the 6-step shake and the palette write described in [Combat animation](#combat-animation).

A `SAF` frame is a list of chunks, and each chunk is a grid of compressed cells. From `FUN_00014140`, `FUN_00013fd0`, and `FUN_00013ed0`:

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

On `Back`, `Stand`, `Act`, and `Magic`, that short is 0 exactly when the mode byte is 0, and a mode byte of 1 stores 8 through 16. The effect members of `MISC.VFS` follow the same pairing, except four chunks of `MB29` and `MB31`, which store mode 1 and short 0. Their other mode-1 shorts run from 2 through 16. A landed hit sets the blit mode dword to 3, and the chunk byte is then ignored. That path is under [Combat animation](#combat-animation). The picture is a signed column count, a signed row count, and then that many cell indexes. None of those pictures has a negative count. Each cell is expanded with `FUN_0005664b` at the chunk's x,y plus the cell's column and row times the cell size.

`FUN_0005664b` stores width, height, and pitch, then switches on a mode byte. Mode 0 is `FUN_0005677d`, and its body is hand-written: it has no prologue, and the source, destination, and per-row adjustment arrive in `ESI`, `EDI`, and `EDX`. `FUN_0005664b` sets that up before the call. It loads the pitch argument into `EDX` and subtracts the width, and the mode body adds `EDX` at the end of each row. Mode 0 and mode 3 both do this. The disassembly is at `0x56657`.

The opcodes, from the listing at `0x5677d`. `n` is `(opcode & 0x3f) + 1`. At the start of a row the body loads the width into `BX` from the word at `0x70024`. Each opcode subtracts its count from `BX`, and the row ends when `BX` is 0. `EDI` is then increased by `EDX`, and the height word at `0x70022` is decremented.

```
opcode in 0x00..0x3f: read one byte, repeat it n times
opcode in 0x40..0x7f: read one byte, then n times skip one pixel and write that byte
                      (consumes 2n from the width)
opcode in 0x80..0xbf: copy the next n bytes
opcode in 0xc0..0xff: skip n pixels
```

`FUN_0005664b` stores the width, height, and pitch, then calls one body for the mode byte:

| Mode | Body | What the write does |
| --- | --- | --- |
| 0 | `0x5677d` | The four opcodes above, stored byte unchanged. |
| 1 | `0x567fd` | Same opcodes. Each stored byte is looked up in the 256-byte table passed as the sixth argument. |
| 2 | `0x56895` | Starts like mode 1. The bodies diverge; the difference was not listed. |
| 3 | `0x56927` | Hit recolor, under [Combat animation](#combat-animation). |
| 4–8 | `0x569ce`, `0x56b9a`, `0x56e84`, `0x572c1`, `0x5735d` | Not listed. |
| 9 | `0x5738b` | Blend onto the pixel already in the buffer. On a map, an attribute tint and a range whose highlight is neither 0 nor 1. |
| 10 | `0x57503` | Same tables as mode 9. The key is fixed for the blit, and the destination pixel is not read. On a map, the range on a highlight of 1. |
| 11–12 | `0x57686`, `0x577e4` | Not listed. |

Map tiles and `SAF` cells both enter through mode 0 when no palette argument is passed, so mode 0 is the decoder an extractor needs for the stored picture. `ICON.CEL` frames go through the same function from `FUN_0002cb30`.

Mode 9 reads a pointer of three dwords. The second selects a `0x400`-byte slot of the first, and swaps which of the two slots sits `0x2400` bytes higher when that selector is above 8 (`selector = 0x10 - selector` in that case). The third dword is a byte table. For a source sample and the pixel already at the destination:

```
mixed = (table_a[sample] + table_b[dest]) >> 4 & 0x0f0f0f
out = byte_table[(mixed & 0xffff) | (mixed >> 12)]
```

The four opcodes are unchanged. A skip does not read either table. The fight's two tables are the `0x4800`-byte and `0x1000`-byte files loaded at `DAT_000653f0` and `DAT_000643f0`, under [Combat animation](#combat-animation). Mode 9 cannot be replayed from the cell alone. Mode 10 was disassembled, not decompiled. It builds the same pair of tables, indexes the first once from the dword at struct+`0x0c`, and indexes the second from each source sample.

For a designer, the modes the map and the fight select are these. Mode 0 leaves the stored indexes. Mode 1 remaps each stored index through a 256-byte table. Mode 3, from the first landed hit, rewrites the defender and the attack clip as `(sample & 2) + 0x80`. Inferred: that is the strike flash. Mode 9 mixes the picture with the pixel already on screen. A fight chunk picks the ramp with `0x10` minus the short at chunk `+7`. A map plate picks it with an attribute byte, or with the pulse in [Map](map.md). Inferred: the pulse is a shimmer, and the mix is what lets a plate painted over units still show them. Mode 10 recolors the picture from itself. Inferred: a ground range highlight looks the same whatever was drawn underneath. Modes 2, 4 through 8, 11, and 12 were not given a role.

To pull the pictures out: walk the VFS directory as described in [Archives](archives.md), reject a member whose span passes the end of the archive, then run mode 0 into a buffer of `width * height` bytes. A cell's bytes run from its table offset to the next higher offset in that table, and the last cell runs to the end of the member. A picture is the column count, the row count, then that many cell indexes, one row at a time. Stamp cell (column, row) at `chunk_x + column * cell_width`, `chunk_y + row * cell_height`. Pixels the skip opcodes never write stay transparent. The chunk x and y are positions in the 368×248 compose buffer, so a tight sprite is the bounding box of the written pixels, not the cell size. Hold, hit, and the mode byte stay beside the frame so a player can step it the way `FUN_00014540` does.

`Fight.pal` and the other four `.pal` members of `MISC.VFS` (`Chapter.pal`, `Dynasty.pal`, `Fde.pal`, `Stboard.pal`) are 768 bytes with components 0 through 63. Shift each component left by 2 for an 8-bit channel. The string `Fight.pal` is at `0x61cd4`. `FUN_00029630` opens it into `0x643e4`, and the fight players install that buffer through `FUN_00022f10`, under [CEL pictures](#cel-pictures). Every cell in the fight clips below expanded with mode 0: each row's width counter landed on 0, and the cell size is 24×24 throughout. Colored from `Fight.pal`, frames of `BACK00`, `STAND000`, `ACT000`, `MAGIC000`, and `ML00` are readable pictures. `STAND000` frame 0's written pixels sit at compose `(181, 47)`. Chunk byte 1 still expands with mode 0. There are 44 such chunks in `FIGHT.VFS` (10 in `Stand`, 34 in `Magic`), 177 in `FIGACT.VFS`, none in `BACKGRND.VFS`, and 345 in the effect members of `MISC.VFS`. The fight paints those chunks with mode 9, so this recovers the stored indexes and not that blend. Chunk rectangles in `FIGHT.VFS` stay inside x 0..343 and y 0..223. `FIGACT.VFS` reaches x −1 and y 255. `BACKGRND.VFS` stays in y 28..150.

`extract_fight_sprites.py` is that walk. It writes one PNG per frame that has chunks, `sheet.png` for the clip, and a JSON record of hold, hit, sample, and the cropped origin. How the sheet is registered is under [SAF clips](#saf-clips). The folders are `backdrops/` (`Back##`), `stands/` (`Stand###`, the body drawn for the defender and for the attacker until the swing), `attacks/` (`Act###`), and `effects/`. A walk of the local archives wrote 63 backdrop frames, 388 standing frames, 2117 attack frames, and 3538 effect frames.

25 attack frames and 63 effect frames store a chunk count of 0. They are kept in the JSON and get no PNG, so the frame index still matches the file. The attack frames are in `ACT005` (3), `ACT020` (3), `ACT024` (2), `ACT060` (1), `ACT061` (1), `ACT062` (2), `ACT067` (2), `ACT070` (1), `ACT093` (3), `ACT094` (3), `ACT095` (3), and `ACT107` (1). Among the effect frames, `EE05`, `EE06`, `EE07`, `EE23`, `ME03`, `ME04`, `ME05`, `ME06`, `ME07`, `ME26`, `ME27`, `ME28`, `ME30`, `ME31`, `ME34`, and `ME35` are a whole file of one empty frame. The same `SAF` path covers the 67 `ICON####.SAF` members of `ICONANI.VFS`. Icon opcode 6 names `Icon%04d.saf` from the next script byte, in [Scenario files](scenario.md). Which frame `FUN_00022290` shows was not read.

## SAF clips

Combat, spell, and backdrop pictures are `SAF` version `0x06`. `FUN_000140e0(file, index)` returns one frame. `FUN_000144d0` is the frame count. `FUN_00014540` advances a cursor. `FUN_00014140` blits the current frame into a compose buffer.

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

`FUN_00014540(cursor, mode)`: mode 1 resets to frame 0. Mode 0 loops. Mode 2 stops on the last frame and returns 1. The cursor is a pair: frame index, then tick-within-frame. Each call adds one tick. When the tick reaches the hold at frame `+2`, the index moves. The `SAF` check in that function is written as three comparisons joined by `||`, so it accepts more than the three bytes `S`,`A`,`F`.

One member is one sequence. Frame `i` is the record at `file + dword[table + i*4]`. Nothing else groups the frames. The hit byte, the preamble on frame 0, and the sample index mark events in that pass. They do not reorder it. The mode is the immediate pushed with the cursor, not a field in the file. Forty-one call sites push 0 and twenty push 1. Six push 2, each `mov eax, 2` then the same cursor, at `0x1aad6`, `0x1ac89`, `0x1b12d`, `0x1b41b`, `0x1b619`, and `0x1b7e5`. The calls from the strike, `0x19874` through `0x19e8f`, push 0 or 1, so an attack cursor can wrap. A pass of the animation is still frame 0 through the last frame, each shown for its hold. `Stand` is the clip the idle row loops.

Cropped frames of one clip do not share an origin, so stacking the PNGs at (0, 0) moves the figure. `STAND000` has 3 origins inside a box at `(181, 47)` sized 132×152. `ACT000` has 12 origins inside a box at `(2, 42)` sized 318×158. The clamp is that box. Stamp frame `i` at `(x - box_x, y - box_y)`. `extract_fight_sprites.py` writes `sheet.png` on that grid, one cell per frame in table order, with a transparent cell where the chunk count is 0. The cell is the union of the written pixels. The last row can have unused cells after the frame count. Those are not frames. `clips.json` records the box and the grid.

`FUN_00014140` blits one frame. Its second argument, when nonzero, calls `FUN_000142d0` with the frame's sample index. That function returns unless `DAT_00069d70` and `DAT_00069d71` are both nonzero. It walks eight dwords at `DAT_00069d30` and keeps the first whose status call is not 4. The sample record is `file + dword[sample_table + index * 4]`:

| Offset | Field |
| --- | --- |
| 0, 1 | Two bytes. `01 08` selects 0, `01 10` selects 1, `02 08` selects 2, and anything else selects 3. That value is passed to `FUN_0003ee60` with a 2. |
| `+2` | `uint16` passed to `FUN_0003f096`. On `ACT000.SAF` the only sample stores 11025 here. |
| `+4` | `uint32` length of the bytes at `+8`. On that same sample the length is 4464 and the span fits in the file. |

`FUN_0003edde` receives the bytes at `+8` and that length. `FUN_0003f1f8` is then called with 1, and `FUN_0003eee2` starts the slot. Those four calls were not decompiled. Inferred: they are the Miles playback used everywhere else, because the slot table and the rate value have that shape. The five `ACT` files checked (`ACT000` through `ACT004`) use sample indexes −1, 0, and 1 only. `ACT000` has one sample and points frame 5 at it; its hit marker is on frame 6.

Hold counts actually stored: every `STAND` frame is 4. `ACT` frames are mostly 2 (1296) or 1 (743), with a few 3, 4, 6, 7. `MAGIC` is the same shape.

Compose buffer for combat is `0x16480` bytes, pitch `0x170` (368), origin size stored as `0xf8`. The visible copy to the VGA is 320×200 from buffer+`0x2298`. Map composition uses `0x15180` bytes, pitch `0x168` (360). Sprites are drawn at 24×24.

## Combat animation

`FUN_00018d50` builds the screen. `FUN_000196b0` steps it. The pool math those hit frames apply is in [Combat](combat.md).

Before any frame, the two remap tables are replaced. `FMer1.tmp` is read into `DAT_000653f0` (`0x4800` bytes) and `FMer2.tmp` into `DAT_000643f0` (`0x1000` bytes). Both files on disk are exactly those sizes. `FUN_00022f10` then writes VGA colors 0 through 255 from the block at `DAT_000643e4`. After the fight the screen at `0xa0000` is cleared for 64000 bytes, the `Mer1.tmp` / `Mer2.tmp` pair is read back over the same two tables, and `FUN_00022f10` writes the block at `DAT_000643cc`. What those two blocks hold was not read.

Files, by character byte `+7` and by the defender's terrain byte 3 (decremented when it is nonzero):

| Picture | Archive | Name |
| --- | --- | --- |
| Both standing clips | `FIGHT.VFS` | `Stand%03d.saf` |
| Attacker's swing | `FIGACT.VFS` | `Act%03d.saf` |
| Defender's swing | `FIGACT.VFS` | loaded only when `FUN_000137e0` returns 1 |
| Backdrop | `BACKGRND.VFS` | `Back%02d.saf` |
| Bars | `MISC.VFS` | `FIGBAR.CEL` |

`FIGBAR.CEL` uses the same header as `ICON.CEL`. Its three big-endian shorts are directory `0x0f`, width `0x91`, height `9`. The directory has eight pictures and a sentinel. Pictures 0..3 are about 213 bytes. Pictures 4..7 are 55 bytes. The fight copies 4..7 into a strip `0x7d` wide, each 5 pixels below the last. Pictures 0..3 are the frames drawn behind the fills.

If the attack clip's frame 0 has a nonzero byte at `+4`, the defender's backdrop is kept aside and a second backdrop is loaded from the attacker's tile. That byte is the preamble length. The intro then does not draw the defender.

Compose buffer is `0x16480` bytes, 368×248 at pitch `0x170`. Each displayed frame waits until bit 3 of port `0x3da` is clear and then set, copies 320×200 from buffer+`0x2298` to `0xa0000`, and waits until `DAT_00069d64` changes. Buffer+`0x2298` is pixel (24, 24). The pictures are placed at (24, 24) in the buffer, so they sit at the top-left of the VGA window, and the extra 24 pixels on the left and top are the room the slide uses.

One composed frame, back to front:

```
clear the buffer
blit backdrop at (24, y)
blit defender Stand at (x, y)          # omitted during the intro when a preamble is set
blit attacker Stand or Act at (x, y)
draw the two bars                        # FUN_000192f0
```

The blit record passed to `FUN_00014140` is 0x24 bytes: buffer, pitch, height `0xf8`, x, y, the `SAF`, the frame index, a dword, and a mode. While that mode dword is 0, a chunk whose byte is 0 uses expander mode 0 and a chunk whose byte is 1 uses mode 9. The mode-9 argument is `0x10` minus the short at chunk `+7`, and the two remap tables above are the pointers it is given. From the first landed hit onward the record's dword is `0x28000` and its mode is 3, for the defender's stand and for the attack clip.

Mode 3 is `FUN_00056927`. The body is hand-written, like mode 0, and was disassembled. It is the same four opcodes. Each byte it writes is `((sample + DH) & AH) + DL`, and those three registers are loaded from the three low bytes of the dword at the caller's `EBP+0x1c`. `FUN_0005664b` leaves that dword as its sixth argument, which this path sets to `0x28000`. The bytes are `00 80 02`, so the written index is `(sample & 2) + 0x80`. The row adjustment is `pitch - width`, saved from `EDX` and added after each row.

`FUN_000194c0` is nine frames, the counter running from 8 down to 0. The backdrop's y is `step * 0x14 + 24`, so it moves from 184 up to 24. The attacker's x is `step * sign + 24`. Side byte `0` uses sign −15 and enters from the left. Any other side uses +15 and enters from the right. The defender, when drawn, stays at (24, 24).

`FUN_000196b0` then plays the swing. A preamble, when frame 0's byte `+4` is nonzero, is that many attack frames drawn over the defender's backdrop with no standing clips. `FUN_0001a350` follows: eight frames slide one backdrop out and the other in by 40 pixels a frame, carrying the standing clip. Eight steps of 40 cover the 320-wide window. The sign is +1 for side `0` and −1 otherwise.

The strike loop clears the buffer and draws backdrop, shaking defender, then the attack frame. The defender's x offset is `sign * table[k]` and, when there was no preamble, the y offset is `sign * table2[k]`. `k` is set to 5 on a landed hit frame and then falls by 1 each composed frame until it stays at 0. The tables are six dwords:

| `k` | x at `0x18c50` | y at `0x18c68` |
| --- | --- | --- |
| 5 | 14 | 10 |
| 4 | 18 | 8 |
| 3 | 14 | 6 |
| 2 | 9 | 4 |
| 1 | 4 | 2 |
| 0 | 0 | 0 |

Side `0` uses sign +1. Any other side uses −1. The attack clip itself stays at (24, 24). The sample flag passed with it is 1 until a miss frame, which passes 0 and plays `Miss.wav` through `FUN_0002a1c0` instead. A crit (dword 1 from `FUN_00019f60`) also writes palette index 0 to `3f 3f 3f`, waits `0x32` on the same delay used before the fight, then writes index 0 as `00 00 00`.

Bars, from `FUN_000192f0`, use the defender during the strike and the attacker as well when there was no preamble. Side `0` is anchored at buffer `(0x1e, 199)`, which is screen `(6, 175)`, and uses `FIGBAR` pictures 2 and 3 plus strip slots 2 and 3. Any other side is anchored at buffer `(0xc3, 0x20)`, screen `(171, 8)`, and uses pictures 0 and 1 plus strip slots 0 and 1. Each anchor draws the frame, a second frame 10 pixels lower, then two fills. The fill width is `(current * 0x7d + max - 1) / max`, so 125 pixels, 5 pixels tall. The pool at `+0x40` is the upper fill, two rows under the anchor. The pool at `+0x44` is twelve rows under it. Slots 0 and 1 are right-aligned: the copy starts at `0x7d - width`. Slots 2 and 3 grow from the left. This is not the 41-step bar in `FUN_0001cad0`.

After the last attack frame both standing clips are held for 12 composed frames, the defender's bar always and the attacker's bar only when there was no preamble. A second swing, when the count in [Combat](combat.md) says so and the pool is still above 0, runs `FUN_0001a350` again if a preamble was set and then repeats the strike. A counterattack is the same function with the clips swapped.

Per character id the body clips are:

| Clip | Files | Frames |
| --- | --- | --- |
| Idle `STAND###` | 94 | 4 on 91 of them, 8 on `STAND060`, `STAND061`, `STAND062`. Loops. The number is the character id: 0–12, 15–33, 35, 59–116, 118, 119, and 128. |
| Attack `ACT###` | 91 | 8 to 47, median 22. Every file has 1 to 6 hit frames. The same ids as `STAND`, without 118, 119, and 128. |
| Spell effect `MAGIC###` | 46 | 6 to 49, median 28. Ids 0–11, 15–33, 61–67, 72, 73, 101–104, 113, and 115. |
| Backdrop `BACK##` | 63 | 1 frame each. |

Spell attack, `FUN_0001a4a0(attacker, spellId, targetCount, targets)`. Spell ids `0x0a`, `0x0b`, `0x0e`–`0x16`, `0x18`, and `0x21` go to `FUN_000288c0` instead of the sequence below.

For every other id the player loads, using side prefix `E` or `M` from byte `+6` and the spell id:

1. `Stand%03d` for the caster and each target, `Magic%03d` for the caster, `Back%02d`.
2. `%sB%02d.saf` played to completion (begin).
3. `%sL%02d.saf` (strike). Hit frames inside it drive the HP write. Zero hit frames aborts.
4. `%sE%02d.saf` played to completion (end).
5. `%sS%02d.saf` as an extra overlay when the spell id is `0x0d`, or in `0x1a`–`0x1f`, `0x21`–`0x24`, or `0x26`–`0x27`.

Those phase files live in `MISC.VFS`. Counts: `MB`/`ME`/`ML` 25 each, `MS` 11, `EB`/`EE`/`EL` 12 each, `EMG` 25, `ES` 1. The twenty-fifth `EMG` is `EMG33-1.SAF`, beside `EMG33.SAF`. `Emg%02d.saf` is formatted in `FUN_000288c0`. The id is passed through, except id `0x0b`, which is formatted as id−1. Id `0x21` instead opens the separate string `Emg33-1.saf` at `0x61bc8` (`0x2898d`). The same function names `EarQu.wav`. Its callers are `FUN_0001a4a0` and `FUN_00013c90`. The frames after the open were not walked. The same archive also holds `CURE.SAF`, `CUREMP.SAF`, `MAG11.SAF`, `MAGIC0BB.SAF`, `MAGIC0GG.SAF`, `POSEFF.SAF`, and `POSION.SAF`. They use the same `SAF` version `0x06` layout and are included with the effect clips above. Six further `.saf` members are not fight effects. `Logo.saf` is the startup clip in [Session](session.md). `Chapter.saf` is played by `FUN_00020c30`, which every scenario opener calls: one frame through `FUN_00014140`, then `Chapter.pal` fades in and out by steps of 4. `EnyPhase.saf` and `PlyPhase.saf` are played by `FUN_0001ead0` from the turn change in [Turns](turns.md). That player saves the screen, blends five steps through `FUN_0002fda0` with the tables at `DAT_000653f0` and `DAT_000643f0`, plays the clip, and blends back. When the name is `PLYPHASE.SAF` it calls `FUN_0001e810` first. `GameOver.saf` is played by `FUN_0002a920`: the clip steps with `FUN_00014540` until that call returns nonzero, then sixteen blend steps run and the function waits on a key. `Bonus-1.saf` is opened, with `Bonus.wav`, by `FUN_000361d0`, which the first village-menu action `FUN_00035a30` calls. The frames inside `FUN_000361d0` were not walked. While the strike plays, a target who is actually hit also cycles a small palette (`local_50` modulo 8) keyed by a 40-long table copied from `0x18cb0`.

## CEL pictures

Map sprites, portraits, and the interface windows are `CEL` files, not `SAF`. The header begins `CEL \x01`. On every file checked, byte 6 is 0 and byte 8 is 0 or 1. The bitmap width is byte 7, plus 256 when byte 8 is 1. The bitmap height is byte 9. When byte 8 is 0 this is the same pair of big-endian shorts [Map](map.md) calls width and height, so a section tile stays 24×24. When byte 8 is 1 those shorts read high: `VILLAGE.CEL` says 64×456 and the picture that mode 0 consumes is 320×200. The reader that applies the flag was not reopened. The size above is the one at which mode 0 consumes the picture.

The directory offset is the big-endian short at `+4`, and it is `0x0f` on every file checked. The dwords there are little-endian picture offsets. A picture is the bytes from one dword to the next. The uint16 at `+10` equals that picture count for every `.cel` in `MISC.VFS` and for `FACE.CEL`. It does not for `ICON.CEL`: the field is 128, and the ordered directory holds 1920 pictures.

`Fde.pal` is the palette the map and the shared interface are installed with. The name at `0x61a78` is opened at `0x23f05` into the global at `0x643cc`. `FUN_00029630` opens the second copy of that name, at `0x61ccc`, into the same global, and opens `Fight.pal` into `0x643e4`. `FUN_00022f10` writes one range of a 768-byte buffer to the DAC. For each index it adds the three bias arguments to the three component bytes, clamps each sum to 0..63, writes the index to port `0x3c8`, and writes the three bytes to port `0x3c9`. The standing installs of `0x643cc` and of `0x643e4` pass biases 0, 0, 0, so the file bytes are the DAC bytes. Other sites pass a bias on purpose. −64 on every channel, at `0x20cc6` and `0x30cdb`, clamps the palette to black. +63 on every channel, at `0x1c8d8`, `0x1c922`, and `0x2884f`, clamps it to white. `0x1c714`, and the same instruction at `0x1c75e`, `0x1c800`, and `0x1c84a`, passes −64, +64, −64. `Chapter.pal` is opened at `0x20c54` and installed at `0x20d74` with bias `-step * 4` on each channel.

The two palette files share 2 of 256 entries. Coloring these pictures from `Fight.pal` is what shifts them red. On `ICON.CEL` character 1, frame 0, index 143 is the most common written pixel: `Fde.pal` stores `03 03 03` there and `Fight.pal` stores `19 07 00`. The same substitution moves the other indexes those pictures use. `extract_cel_pictures.py` colors icons, tiles, portraits, and the interface from `Fde.pal`, and writes character sheets under `maps/icons`, section tiles under `maps/tiles`, portraits under `maps/faces`, and the interface files under `ui`. The labeled contact sheet of character id, portrait, and map frame 0 is [docs/fdps/unit-ids](../docs/fdps/unit-ids/index.html).

`STBOARD.CEL` is opened at `0x2a56e`. `StBoard.pal` is opened at `0x2a585` and installed at `0x2a5ac` with biases 0, 0, 0. That picture is colored from `StBoard.pal`. `FIGBAR.CEL` is opened at `0x18de6` and `0x1a5cb` into `0x64004`, inside the fight players that install `Fight.pal`. The blit of the bar was not read, so coloring `FIGBAR.CEL` from `Fight.pal` is an inference.

## Map sprites

`FUN_00023020` seeks to `0x0f` in `ICON.CEL` and reads `0x2970` bytes. The ordered dwords there increase through index 1920, where the dword equals the file size. 1920 / 12 = 160, so characters 0 through 159 each have 12 frames and a following offset. Frame `i` is `file[offset[i] : offset[i + 1]]`. The 1921 dwords end at file offset 7699, which is also where offset 0 points, so the `0x2970` read runs past the table into the first picture. There is no character 220 in the file. `FUN_00023020` is called with the character id as its first argument. At `0x23613` that push is the id just read from the scenario record. The other six call sites push the byte at `+7`. It multiplies that argument by 12 and copies pictures `id * 12` through `id * 12 + 11` into a cache at `DAT_00060138`. The byte it returns is the cache slot stored at unit `+2`, which is what the drawer multiplies, so the slot is not itself the character id. Frame bytes are compressed: character 0's frames are 334–424 bytes, not `24*24`, and frame 0 of that character expands with mode 0 to a 24×24 picture. `FUN_0005664b` expands a frame onto the map buffer at 24×24. Mode 0 of that expander is the opcode loop above. The string `Fde.pal` is at `0x61a78`. How it reaches the DAC is under [CEL pictures](#cel-pictures).

Ids 0 through 8, 15 through 23, and 24 through 32 expand to the same nine sheets, in that order. Id 33 and id 36 repeat id 0, and id 116 repeats id 3. Four further sheets are shared: 37 with 118, 38 with 119, 39 with 129, and 59 with 91. Mode 0 writes no pixel for ids 34, 40–51, 53–56, and 157–159. Every frame is already a 24×24 cell, so a character's sheet is four rows of three frames with no origin to correct. Row is the facing in the table below. The three columns are steps 0, 1, and 2. The walk shows 0, 1, 2, 1. Section tiles are the same 24×24 mode-0 pictures; which section files follow the packed directory is in [Map](map.md). `ICONANI.VFS` is a second set of icon clips. Icon opcode 6 names which file plays, in [Scenario files](scenario.md). Which frame `FUN_00022290` shows was not read.

`FUN_0002cb30` picks the picture:

```
index = slot * 12 + facing * 3 + step
```

`slot` is unit byte `+2`. `facing` is byte `+3`. `step` comes from a global tick `DAT_00069cc8`, which runs 0…15 and is divided by 4. The value 3 is replaced with 1, so the walk is frames **0, 1, 2, 1** of that facing.

| Facing | Movement applied to the sprite | Frame row |
| --- | --- | --- |
| 0 | +Y, 4 pixels times byte `+4` | 0–2 |
| 1 | −X | 3–5 |
| 2 | −Y | 6–8 |
| 3 | +X | 9–11 |

Bit `0x80` of byte `+5` draws `facing * 3 + 1` only, through a different blit mode. Byte `+0x26` nonzero forces step 0 and adds `tick % 2` to x. The first of the two draw passes paints a shared shadow from `DAT_000643e0` using the same 3-step cycle (or its second frame when the `0x80` flag is set). A 24×11 overlay from `DAT_000643d8` is drawn under the sprite when `FUN_0002ca60` returns a frame; that function was not read.

`FACE.CEL` is the same directory. Byte 8 is 0, the bitmap is 125×100, and the count at `+10` is 160, matching the directory. `FUN_000177c0(dest, pitch, index)` frees any picture it loaded before. An index of −1 stops there. Any other index reads the two dwords at file `0x0f + index * 4`, loads that span, and expands it with mode 0 at 125×100 onto `dest` at the given pitch. The call at `0x207d8` is inside `FUN_00020580`, and the index it passes is that function's argument. The chest reader passes unit `+7`. Calls that push an immediate use a value from 0 through `0x81`. Picture `n` is character `n`. Portraits of 3 and 116 match, as do 122 and 146, 125 and 139, and 137 and 159. Mode 0 writes no pixel for 34, 36–51, 53–58, 132–136, 141–145, and 147–158. The calls at `0x16790` and `0x20c1b` were not read.

## Interface pictures

`FUN_00029630` loads the shared interface from `MISC.VFS`. These are the `.cel` members. The bitmap is the size from [CEL pictures](#cel-pictures), and mode 0 consumes every picture.

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

Byte 8 is 1, and the bitmap is 320×200, for `VILLAGE.CEL`, `STATUS.CEL`, `STBOARD.CEL`, `LOAD.CEL`, `SAVE.CEL`, `BARSHOP.CEL`, `CHURCH.CEL`, `ITEM.CEL`, `WEAPON.CEL`, `SECRET.CEL`, and `RELIVE.CEL`. Each is one picture. `STBOARD.CEL` is colored from `StBoard.pal`, and `FIGBAR.CEL` from `Fight.pal`, as under [CEL pictures](#cel-pictures). The other files in this list are colored from `Fde.pal`. The startup list names the cursor, command window, shadow, status, message box, digits, selection bar, level-up picture, window, and bars. Which call opens which of these files was not separated.

`SHADOW.CEL` is 14 pictures of 24×24. `ICONSTS.CEL` is 5 pictures of 24×11. The map drawer paints a shadow from `DAT_000643e0` and a 24×11 overlay from `DAT_000643d8`. That these two files are those pictures is an inference from the sizes and the names.
