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

A frame record still has its hold count at `+2` and its hit marker at `+5`. The chunk count is the short at `+8`. Chunks start at `+10` and are 13 bytes: a `uint16` picture index, an `int16` x, an `int16` y, then a byte that is 0 or 1. Byte 1 selects expander mode 9 and uses the short at chunk `+7` as `0x10` minus that short. The picture is a short column count, a short row count, and then that many cell indexes. Each cell is expanded with `FUN_0005664b` at the chunk's x,y plus the cell's column and row times the cell size.

`FUN_0005664b` stores width, height, and pitch, then switches on a mode byte. Mode 0 is `FUN_0005677d`, and its body is hand-written: it has no prologue, and the source, destination, and per-row adjustment arrive in `ESI`, `EDI`, and `EDX`. The mode-0 body never reads the pitch global, so the value of `EDX` is whatever the caller left. For a destination pitched wider than the picture, that adjustment has to be `pitch - width` or the next row starts in the wrong place. That is the arrangement the map buffer requires. It was not confirmed at the call.

The opcodes, from the listing at `0x5677d`. `n` is `(opcode & 0x3f) + 1`. A row stops when the width counter reaches 0, then `EDI += EDX` and the height counter drops.

```
opcode in 0x00..0x3f: read one byte, repeat it n times
opcode in 0x40..0x7f: read one byte, then n times skip one pixel and write that byte
                      (consumes 2n from the width)
opcode in 0x80..0xbf: copy the next n bytes
opcode in 0xc0..0xff: skip n pixels
```

Modes 1 through 12 are further expanders (`0x567fd` onward) and were not listed. Map tiles and `SAF` cells both enter through mode 0 when no palette argument is passed, so this is the decoder an extractor needs for those pictures. `ICON.CEL` frames go through the same function from `FUN_0002cb30`.

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
| `+2` | `int16` hold count, in ticks. The stepper increments a tick until it reaches this, then moves to the next frame. |
| `+4` | Byte read by the players. On frame 0 of an attack or spell clip, a nonzero value is how far to play a preamble before the hit sequence. |
| `+5` | Nonzero marks a hit frame. Damage is applied when the cursor lands on one. A clip whose strike phase has none of these aborts with `ERROR: No Hit Point`. |

`FUN_00014540(cursor, mode)`: mode 1 resets to frame 0. Mode 0 loops. Mode 2 stops on the last frame and returns 1. The cursor is a pair: frame index, then tick-within-frame. The `SAF` check in that function is written as three comparisons joined by `||`, so it accepts more than the three bytes `S`,`A`,`F`.

Hold counts actually stored: every `STAND` frame is 4. `ACT` frames are mostly 2 (1296) or 1 (743), with a few 3, 4, 6, 7. `MAGIC` is the same shape.

Compose buffer for combat is `0x16480` bytes, pitch `0x170` (368), origin size stored as `0xf8`. The visible copy to the VGA is 320×200 from buffer+`0x2298`. Map composition uses `0x15180` bytes, pitch `0x168` (360). Sprites are drawn at 24×24.

## Combat animation

Two players.

Physical attack, `FUN_00018d50` then `FUN_000196b0`:

- Loads `Stand%03d.saf` from `FIGHT.VFS` for each fighter, using byte `+7`.
- Loads `Act%03d.saf` from `FIGACT.VFS` for the attacker, and the defender's act clip only if `FUN_000137e0` returns 1.
- Loads `Back%02d.saf` from `BACKGRND.VFS`. `FIGBAR.CEL` from `MISC.VFS` is drawn four times as the combat bar.
- The act clip plays once. `FUN_00019f60` computes the damage, and frames with byte `+5` set subtract it from the defender's word at `+0x40`, spread across the number of hit frames. A miss plays `Miss.wav` and skips the flash.
- There is no hurt clip and no death clip. A landed hit runs a 6-step pixel offset (`local_54` counts down from 5) and, when a flag from the hit check is set, writes palette ports `0x3c8`/`0x3c9`.
- Afterwards both standing clips are held for 12 composed frames.
- A roll of `rand % 100 < 3`, or weapon byte `+9 == 2`, plays the swing a second time.

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
