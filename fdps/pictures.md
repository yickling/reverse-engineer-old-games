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

A frame record still has its hold count at `+2` and its hit marker at `+5`. The chunk count is the short at `+8`. Chunks start at `+10` and are 13 bytes: a `uint16` picture index, an `int16` x, an `int16` y, then a byte that is 0 or 1. When the blit record's mode dword is 0, byte 1 selects expander mode 9 and uses the short at chunk `+7` as `0x10` minus that short. A landed hit sets that dword to 3, and the chunk byte is then ignored. That path is under [Combat animation](#combat-animation). The picture is a short column count, a short row count, and then that many cell indexes. Each cell is expanded with `FUN_0005664b` at the chunk's x,y plus the cell's column and row times the cell size.

`FUN_0005664b` stores width, height, and pitch, then switches on a mode byte. Mode 0 is `FUN_0005677d`, and its body is hand-written: it has no prologue, and the source, destination, and per-row adjustment arrive in `ESI`, `EDI`, and `EDX`. `FUN_0005664b` sets that up before the call. It loads the pitch argument into `EDX` and subtracts the width, and the mode body adds `EDX` at the end of each row. Mode 0 and mode 3 both do this. The disassembly is at `0x56657`.

The opcodes, from the listing at `0x5677d`. `n` is `(opcode & 0x3f) + 1`. A row stops when the width counter reaches 0, then `EDI += EDX` and the height counter drops.

```
opcode in 0x00..0x3f: read one byte, repeat it n times
opcode in 0x40..0x7f: read one byte, then n times skip one pixel and write that byte
                      (consumes 2n from the width)
opcode in 0x80..0xbf: copy the next n bytes
opcode in 0xc0..0xff: skip n pixels
```

Mode 3 is the recolor used on a landed hit, disassembled under [Combat animation](#combat-animation). Modes 1, 2, and 4 through 12 (`0x567fd` onward, apart from mode 3 at `0x56927`) were not listed. Map tiles and `SAF` cells both enter through mode 0 when no palette argument is passed, so this is the decoder an extractor needs for those pictures. `ICON.CEL` frames go through the same function from `FUN_0002cb30`.

To pull the pictures out: walk the VFS directory as described in [Archives](archives.md), reject a member whose span passes the end of the archive, then run the decoder above into a buffer of `width * height` bytes. For a `SAF` clip, do that per cell and stamp the cells into the chunk's rectangle at the chunk's x,y. Hold, hit, and the mode byte stay beside the frame so a player can step it the way `FUN_00014540` does. Nothing here was checked by decoding a frame and looking at it.

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

`FUN_00014540(cursor, mode)`: mode 1 resets to frame 0. Mode 0 loops. Mode 2 stops on the last frame and returns 1. The cursor is a pair: frame index, then tick-within-frame. The `SAF` check in that function is written as three comparisons joined by `||`, so it accepts more than the three bytes `S`,`A`,`F`.

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
| Idle `STAND###` | 94 | 4 on 91 of them, 8 on `STAND060`, `STAND061`, `STAND062`. Loops. |
| Attack `ACT###` | 91 | 8 to 47, median 22. Every file has 1 to 6 hit frames. |
| Spell effect `MAGIC###` | 46 | 6 to 49, median 28. |
| Backdrop `BACK##` | 63 | 1 frame each. |

Spell attack, `FUN_0001a4a0(attacker, spellId, targetCount, targets)`. Spell ids `0x0a`, `0x0b`, `0x0e`–`0x16`, `0x18`, and `0x21` go to `FUN_000288c0` instead of the sequence below.

For every other id the player loads, using side prefix `E` or `M` from byte `+6` and the spell id:

1. `Stand%03d` for the caster and each target, `Magic%03d` for the caster, `Back%02d`.
2. `%sB%02d.saf` played to completion (begin).
3. `%sL%02d.saf` (strike). Hit frames inside it drive the HP write. Zero hit frames aborts.
4. `%sE%02d.saf` played to completion (end).
5. `%sS%02d.saf` as an extra overlay when the spell id is `0x0d`, or in `0x1a`–`0x1f`, `0x21`–`0x24`, or `0x26`–`0x27`.

Those phase files live in `MISC.VFS`. Counts: `MB`/`ME`/`ML` 25 ids each, `MS` 11, `EB`/`EE`/`EL` 12 each, `EMG` 24, `ES` 1. `Emg%02d.saf` is referenced from `0x28951`, which was not decompiled. While the strike plays, a target who is actually hit also cycles a small palette (`local_50` modulo 8) keyed by a 40-long table copied from `0x18cb0`.

## Map sprites

`ICON.CEL` header begins `CEL \x01`, and the words that follow are the directory offset `0x0f` and size 24×24, in the same zero-padded layout as the other CEL headers (`00 0f 00 18 00 18`). `FUN_00023020` seeks to `0x0f`, reads `0x2970` bytes (2652 dwords), and treats each character as 12 dwords of frame offsets. The end of character `i` is the first offset of character `i + 1`. 221 groups of 12 fill the directory exactly, so character 220 has no end offset inside the table. The loader copies one character's bytes into a cache at `DAT_00060138` and stores 12 adjusted offsets per loaded character. Frame bytes are compressed: character 0's frames are 334–424 bytes, not `24*24`. `FUN_0005664b` expands a frame onto the map buffer at 24×24. Mode 0 of that expander is the opcode loop above.

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
