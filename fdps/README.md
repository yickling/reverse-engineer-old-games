# FDPS analysis notes

Flame Dragon Plus (炎龙骑士团外传), a DOS/4GW game in `fdps/`. These notes are from static analysis of `FDPS.EXE` and the data files next to it. Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

The real entry was never turned into a Ghidra function (see below), so the top-level loop is from disassembly of the flat image. Everything else cited as a `FUN_` address was decompiled.

## How to reopen the binary

`FDPS.EXE` is a Watcom C/C++32 (1988–1994) Linear Executable inside an MZ stub. REA rejects that (`unsupported LE executable in MZ image`) before any provider runs. The analysis target is a relocated flat image, not the EXE.

- Image: `/tmp/fdps-flat.bin` (393269 bytes). SHA-256 `5f010ea722e0f449ce6d19dd1215ce01a7b39f45fdfdd8dd1b733ad6d66af291`.
- Open as raw-binary, architecture `x86`, entry `0x10000`, provider `ghidra`. File offset 0 is address `0x10000`. Address `A` is file offset `A - 0x10000`.
- Ghidra 12.1.4 at `~/.local/opt/ghidra_12.1.4_PUBLIC`, JDK 21 at `~/.local/opt/jdk-21.0.13+9`. Language `x86:LE:32:default`, compiler spec `gcc`, loader `BinaryLoader`.
- A bare `0x` selector that is not an existing function falls back to a file-offset mapping and decompiles the wrong body. Ask for `file-offset:0x…` of a byte that sits inside a function Ghidra already created.
- The image was seeded at `0x10000`, not the real entry `0x43008`. Auto-analysis did not create a function at main (`0x291f0`) or at the scenario-dispatch handlers around `0x3a180`.

`DOS4GW.EXE` is the extender. `SETSOUND.EXE` and the `.DIG` files are Miles AIL 3.02. `PlayGame.exe` and the NSIS pieces are a later Windows launcher. Game logic is only in `FDPS.EXE`.

## Executable layout

`e_lfanew` is `0x2a50`, signature `LE`. Objects, with virtual size, base, flags, page index, page count:

| Object | Base | Virtual size | Flags | Pages |
| --- | --- | --- | --- | --- |
| 1 code | `0x10000` | `0x479d0` | `0x2045` (32-bit, preload, executable, readable) | index 1, 72 pages |
| 2 data/stack | `0x60000` | `0xc3c0` | `0x2043` | index 73, 4 initialized pages |
| 3 tiny data | `0x70000` | `0x54` | `0x2043` | index 77, 1 page |

ESP is the top of object 2 (`0xc3c0`). EIP is object 1 + `0x33008`, so the entry address is `0x43008`. Those bytes are a short jump over the Watcom copyright banner into the CRT at `0x43080`.

Page-table entries are a 3-byte big-endian page number plus a flags byte. File offset of page `N` is `0xf000 + (N - 1) * 0x1000`. Fixup records sit between the fixup page-table dwords (table at LE+`0x248`, records at LE+`0x380`). 6836 fixups were applied when the flat image was built, plus one 16-bit selector fixup at VA `0x565af` in object 3. A source-type 7 record replaces the dword at the site with `object_base + target`. The stored dword is already the target offset; it is not added a second time.

The CRT at `0x43080` detects the extender with INT 21h AH=30h (high word `XD` = `0x4458` is DOS/4G). The C startup at `0x4dcbc` calls `0x4e402`, `0x54b2c`, then `call 0x291f0` with globals `0x6a3b8` and `0x6a3b4`, then exits through `0x42b7f`. There is no import table. DOS calls are INT 21h and DPMI INT 31h. VGA mode 13h (320×200×256) goes through a real-mode interrupt wrapper at `0x42fd8` with interrupt `0x10`. Exit restores text mode 03h. The framebuffer is `0xa0000`, 64000 bytes.

Watcom prologues are `53 56 57 55` (push ebx/esi/edi/ebp). At least 486 of them are in the image. FunctionID was not installed, so the CRT shows up as `FUN_`.

## Startup and the outer loop

Disassembly of `0x291f0` (frame `0x3c`), not a decompile:

1. `0x421a8` opens `DISK.NO`. Failure prints `Can't found file 'Disk.No'` and `Please use install function.`, then `exit(1)`.
2. Opens `Disk.no` in `"rt"` and scans one `%s`.
3. Calls `0x3c3a6`. The following compare against 1 falls into an unconditional jump that skips the CD-ROM failure strings at `0x61c3c` and `0x61c64`. This copy never reaches those messages. `DISK.NO` on disk is 19 bytes: `Cracked by JaSon \r\n`.
4. Calls `0x30270(0x19)`, `0x29630`, sets mode 13h, clears `0x69cf0`, `0x69cdc`, byte `0x643eb`, and dword `0x69da0`, then calls the front end `0x2a280`.
5. While byte `0x643eb` is 0: call `0x2b870`, then switch on dword `0x69da0`.
   - 1: call `0x2a920` (references `GameOver.saf`), then `0x2a280` again.
   - 2: `call dword [0x60304 + eax*4]`, where `eax` is dword `0x69cf4` (the scenario index), then `0x30f80`.
6. On quit: `0x29410`, `0x30330`, `0x3c217`, mode 03h, print the string at `0x61c80` (`Thank you for playing Flame Dragon Plus!!`), return.

`0x60304` is 30 code pointers and a trailing 0. The first entries are `0x3a180`, `0x3a1e0`, `0x3a290`, `0x3a300`, `0x3a370`, `0x3a3e0`, `0x3a440`, `0x3a570`, `0x3a5f0`, `0x3a6d0`, `0x3a740`, `0x3a7a0`. `Win12.dat`, `Win17.dat`, `WinGA26.dat`, and `Win26.dat` are referenced from this region. Those handlers were not decompiled.

## Unit record

`FUN_0002cfa0` returns `DAT_00069cd8 + id * 0x50`. The array is allocated to `count * 0x50`. Count lives in `DAT_00060150`.

Bytes filled by the spawners `FUN_00023280` and `FUN_00022bb0`, and read by the map drawer and the combat players:

| Offset | Role |
| --- | --- |
| `+0`, `+1` | Tile x, y. Combat also feeds these to `FUN_0002b790` to pick the battle backdrop. |
| `+2` | Slot in the loaded `ICON.CEL` cache. `FUN_00023020` returns it. |
| `+3` | Facing, 0..3. See map sprites. |
| `+4` | Sub-tile progress. The drawer multiplies it by a per-facing pixel step. |
| `+5` | Flags. Bit 0: map drawer skips the unit. Bit `0x80`: map sprite locks to the middle walk frame, and the system menu treats the unit as eligible when bit 0 is clear. |
| `+6` | Side. `0` selects the `"E"` spell prefix and one mirror sign; nonzero selects `"M"` and the other sign. Scenario load writes `2` here. |
| `+7` | Character id. Indexes `STAND`, `ACT`, `MAGIC`, and the character inside `ICON.CEL`. `0x80` means "no sprite" on the map. |
| `+0x26` | Nonzero freezes the map sprite on frame 0 of its facing and jitters x by one pixel. |
| `+0x40` | Word reduced when an attack frame is marked as a hit. At spawn it is copied from `+0x42`. |
| `+0x42` | Word. Holds the same value written to `+0x40` at spawn. |
| `+0x44`, `+0x46` | Same current/max pattern for a second stat. Not followed further. |

`+0x37`, `+0x39`, `+0x3b`, `+0x3e` are filled from class tables (`FUN_00018aa0` / `FUN_00018ad0` below id `0x3c`, else `FUN_00018b00`). Six item slots start at `+0x0e` as byte pairs. The rest of the 80 bytes is still unmapped.

## Scenario load

`FUN_000227b0` runs off the scenario index in `DAT_00069cf4`.

| Pattern | Archive | What the code does with it |
| --- | --- | --- |
| `fdetxt%02d.txt` | `FIELD.VFS` | Loaded with index + 1. |
| `map%02d.dat` | `FIELD.VFS` | Byte 1 and byte 2 stored in `DAT_00064118` and `DAT_0006410c`. For `MAP00.DAT` those bytes are 1 and `0x16`. The file is 703 bytes and the tail is mostly `0xff`. Record layout past the first three bytes is unread. |
| `M%02d.dtl` | `FIELD1.VFS` | Kept as a pointer. Not decoded. |
| `dsc%02d.dat` | `FIELD2.VFS` | First dword is the section count. Each section is 8 dwords, then two trailing bytes stored separately. `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. |
| `m%02d%d.mpl` | `FIELD1.VFS` | One per section. |
| `m%02d%d.cel` | `FIELD1.VFS` | Tile graphics for that section. |
| `attr%02d%d.dat` | `FIELD2.VFS` | Per-section attributes. Not decoded. |

`M000.MPL` starts with `MPL`, is 1451 bytes, and stores width 30 and height 24 as little-endian shorts at offsets 7 and 9. An 11-byte header plus `30 * 24 * 2` bytes of cells is 1451, so the cells are 2 bytes. After loading, the game allocates `width * height * 2 + 4`, writes the two dimensions in front, and `FUN_00010b20` sets each cell's second byte to `0xff` and masks the first byte with `0x3f`. That runs on a fresh allocation, so it does not copy the MPL. The MPL remains the terrain; this buffer is a separate occupancy layer. Tile pixels are 24×24: the camera coordinates saved to disk are divided by `0x18`, and both map and combat sprites are blitted at 24×24.

`FUN_00022bb0` then opens `ICON.CEL` (the string at `0x61a03`, mode at `0x61a00`), loads `map%02d.cod` from `FIELD.VFS` into `DAT_00060140`, and builds the unit array. `MAP##.COD` is a placement table the spawner indexes by `record * 0x1a` and by `record * 6`. It was not decoded field by field. `FUN_00023800` runs at the end of that load.

`FUN_0002bcf0` draws a frame of the map. Each tick it advances per-section scroll accumulators. Sections whose byte `DAT_00069cfe[i]` is below 10 are drawn, then units (`FUN_0002cfd0`), then sections above 10, so some layers paint over the units. `FUN_0002c0c0` blits one section from its MPL, CEL, occupancy buffer, and ATTR. That blit was not decompiled, so animated tiles are unknown.

## VFS archives

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
| `FIELD.VFS` | 223 | `FDETXT.FON`, 66 `FDETXT##.TXT`, 63 `MAP##.COD`, 93 `.dat` including `MAP##.DAT` |
| `FIELD1.VFS` | 201 | 64 `.dtl`, 69 `.cel`, 68 `.mpl` |
| `FIELD2.VFS` | 131 `.dat` | `DSC##.DAT`, `ATTR###.DAT` |
| `MISC.VFS` | 208 | window `.cel`, `.wav`, `.pal`, spell-phase `.saf`, `FIGBAR.CEL` |
| `ICONANI.VFS` | 133 | `ICON####.SAF` (67) and `.dat` (66). Playback not followed. |
| `ICON.CEL` | loose file, 630141 bytes | every map character |
| `FACE.CEL` | loose file, 679928 bytes | `CEL\x01`. Not followed. |

`FDETXT##.TXT` is a table of 16-bit offsets into 16-bit glyph indexes. `FDETXT.FON` is 57344 bytes and is the bitmap those indexes draw. A GBK scan of the text members found no Han characters.

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
- The act clip plays once. Frames with byte `+5` set subtract from the defender's word at `+0x40`, spread across the number of hit frames. A miss plays `Miss.wav` and skips the flash.
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

`ICON.CEL` header begins `CEL \x01`, and the words that follow are the directory offset `0x0f` and size 24×24, in the same zero-padded layout as the other CEL headers (`00 0f 00 18 00 18`). `FUN_00023020` seeks to `0x0f`, reads `0x2970` bytes (2652 dwords), and treats each character as 12 dwords of frame offsets. The end of character `i` is the first offset of character `i + 1`. 221 groups of 12 fill the directory exactly, so character 220 has no end offset inside the table. The loader copies one character's bytes into a cache at `DAT_00060138` and stores 12 adjusted offsets per loaded character. Frame bytes are compressed: character 0's frames are 334–424 bytes, not `24*24`. `FUN_0005664b` expands a frame onto the map buffer at 24×24.

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

## Save file

`FUN_00014e90` is the system menu and the writer of `FDE.SAV`. The file is one 22987-byte buffer (`0x59cb`), which matches the copy on disk. Layout written in order:

| Offset | Size | Contents |
| --- | --- | --- |
| `0x0000` | `0x8a3` (2211) | current `MAP##.DAT` |
| `0x08a3` | `0xa00` (2560) | block at `DAT_00064108` |
| `0x12a3` | `count * 0x50` | the unit array |
| `0x30a3` | `0x20` | flags at `DAT_000640d8` |
| `0x30c3` | | scenario byte, unit count, scenario index, then four camera values each already divided by 24 |
| `0x59c7` | 4 | checksum from `FUN_00056608` over the first `0x59cb` bytes |

Empty-slot bytes `0xff` are written at `0x3b2b`, `0x4553`, `0x4f7b`, and `0x59a3` when the file did not already exist. Those four addresses are `0xa28` apart. The slot structure around them was not read back.

## Functions worth opening next

| Address | What it is |
| --- | --- |
| `0x291f0` | Main. Not a Ghidra function until the entry is seeded at `0x43008` or this address is disassembled by hand. |
| `0x2a280` | Front end. Not decompiled. |
| `0x2b870` | Called at the top of every outer-loop iteration. Not decompiled. |
| `0x60304` | Scenario dispatch, 30 pointers. Targets were not functions in the session. |
| `0x227b0` | Scenario file load. |
| `0x22bb0` | `ICON.CEL` plus unit placement from `MAP##.COD`. |
| `0x23020` | Slice one character out of `ICON.CEL`. |
| `0x2cb30` | Draw one map unit. |
| `0x2c0c0` | Draw one map layer. Not decompiled. |
| `0x18d50` | Set up a physical fight. |
| `0x196b0` | Play an attack clip. |
| `0x1a4a0` | Play a spell. |
| `0x288c0` | The other spell player, for the ids listed above. Not decompiled. |
| `0x140e0` / `0x14540` / `0x14140` | SAF frame lookup, stepper, blit. |
| `0x39820` / `0x39940` | VFS open and member read. |
| `0x14e90` | System menu and save. |
| `0x5664b` | CEL/map-sprite expander. Not decompiled. |

## Still unknown

- The individual fields of the 80-byte unit past the offsets in the table above, including which word is MP and what the six item pairs mean.
- `MAP##.COD` and `MAP##.DAT` record layouts, `.dtl`, and `ATTR` files.
- Whether map tiles animate, which is inside `FUN_0002c0c0`.
- The compressed frame encoding inside SAF and inside `ICON.CEL` (the expander is `FUN_0005664b`).
- `ICONANI.VFS`, `FACE.CEL`, and the `Emg%02d` player at `0x28951`.
- The 30 scenario handlers and the front end `0x2a280`.
- What the four `0xff` markers inside `FDE.SAV` delimit.
