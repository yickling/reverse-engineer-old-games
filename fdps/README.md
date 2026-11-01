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
| `+0`, `+1` | Tile x, y. `FUN_0002b790` reads the map cell there. Backdrop, terrain, and the detail byte all come from that query. |
| `+2` | Slot in the loaded `ICON.CEL` cache. `FUN_00023020` returns it. |
| `+3` | Facing, 0..3. See map sprites. |
| `+4` | Sub-tile progress. The drawer multiplies it by a per-facing pixel step. |
| `+5` | Flags. Bit 0: map drawer skips the unit. Bit `0x80`: map sprite locks to the middle walk frame, and the system menu treats the unit as eligible when bit 0 is clear. |
| `+6` | Side. `0` selects the `"E"` spell prefix and one mirror sign; any other value selects `"M"`. Spawn writes `2`. The cursor commands side `2`. The two phase walks use side `0` and side `1`. |
| `+7` | Character id. Indexes `STAND`, `ACT`, `MAGIC`, and the character inside `ICON.CEL`. `0x80` means "no sprite" on the map. |
| `+8` | Compared with `7` and `3` while a destination is being chosen. Not followed. |
| `+0x20` | Class. `FUN_00018b60` returns `DAT_00063fd0 + (class + 1) * 10`, a row of `ProMap.dat`. |
| `+0x21` | Byte used as the divisor of the experience term in `FUN_0001c4f0`. |
| `+0x25` | Written by a weapon whose byte `+9` is `4`. Regeneration skips the unit while this is nonzero. |
| `+0x26` | Nonzero freezes the map sprite on frame 0 of its facing and jitters x by one pixel. A weapon whose byte `+9` is `1` writes `2` or `3` here. The cursor will not command the unit while it is nonzero. |
| `+0x31` | Set to `0xff` at spawn. |
| `+0x3b` | Move budget, in tiles. The flood fill stops when the accumulated cost would pass it. |
| `+0x40` | Word reduced by the damage formula. At spawn it is copied from `+0x42`. Inferred to be current hit points: the bar and both attack paths treat it as the pool that reaches 0. |
| `+0x42` | Maximum of that pool. |
| `+0x44`, `+0x46` | Second current/max pair. At the start of `FUN_0001e3c0` a side-`2` unit gains `max / 5`, capped at max. Inferred to be a second pool, from that shape. |
| `+0x48` | Attack word, read by `FUN_0001c4f0` and `FUN_00019f60`. |
| `+0x4a` | Defense word. |
| `+0x4c` | Hit word. A roll of `rand % 100` lands when it is below this minus the defender's `+0x4e`. |
| `+0x4e` | Word subtracted from the attacker's hit word. |

`+0x37`, `+0x39`, `+0x3b`, `+0x3e` are filled from class tables (`FUN_00018aa0` / `FUN_00018ad0` below id `0x3c`, else `FUN_00018b00`). Six item slots start at `+0x0e` as byte pairs. `FUN_00018920` loads `ProMap.dat` to `DAT_00063fd0`, and beside it `Friaprda.dat`, `FriLevUp.dat`, `Item.dat`, `EnemyDat.dat`, `ProEqu.dat`, `MagicDat.dat`, `GetMgTab.dat`, and `RankUp.dat`. Those files were not decoded. The rest of the 80 bytes is still unmapped.

## Scenario load

`FUN_000227b0` runs off the scenario index in `DAT_00069cf4`.

| Pattern | Archive | What the code does with it |
| --- | --- | --- |
| `fdetxt%02d.txt` | `FIELD.VFS` | Loaded with index + 1. |
| `map%02d.dat` | `FIELD.VFS` | Byte 1 and byte 2 stored in `DAT_00064118` and `DAT_0006410c`. For `MAP00.DAT` those bytes are 1 and `0x16`. Byte 1 is the unit count. Byte 2 is added to the unit index before the `MAP##.COD` lookup below. Record layout past those two bytes is unread. |
| `M%02d.dtl` | `FIELD1.VFS` | Magic `DTL`. `M00.DTL` is 4112 bytes: a 16-byte header whose short at `+7` is `0x40`, then `64 * 64` bytes. `FUN_0002b790` stores one of those bytes in `DAT_00069d06`. What that byte changes is unread. |
| `dsc%02d.dat` | `FIELD2.VFS` | First dword is the section count. Each section is 8 dwords, then two trailing bytes stored separately. `DSC00.DAT` is 36 bytes: count 1, then `0, 0, 8, 8, 0, 0, 9, 1`. |
| `m%02d%d.mpl` | `FIELD1.VFS` | One per section. |
| `m%02d%d.cel` | `FIELD1.VFS` | Tile graphics for that section. |
| `attr%02d%d.dat` | `FIELD2.VFS` | Magic `ATR`. One 4-byte record per tile picture, starting at file offset `0x11`. See terrain. |

`M000.MPL` starts with `MPL`, is 1451 bytes, and stores width 30 and height 24 as little-endian shorts at offsets 7 and 9. An 11-byte header plus `30 * 24 * 2` bytes of cells is 1451, so the cells are 2 bytes. After loading, the game allocates `width * height * 2 + 4`, writes the two dimensions in front, and `FUN_00010b20` sets each cell's second byte to `0xff` and masks the first byte with `0x3f`. That runs on a fresh allocation, so it does not copy the MPL. The MPL remains the terrain; this buffer is a separate occupancy layer. Tile pixels are 24×24: the camera coordinates saved to disk are divided by `0x18`, and both map and combat sprites are blitted at 24×24.

`FUN_00022bb0` then opens `ICON.CEL` (the string at `0x61a03`, mode at `0x61a00`), loads `map%02d.cod` from `FIELD.VFS` into `DAT_00060140`, and builds the unit array. For each unit index `i` below `DAT_00064114` it copies 80 bytes from `DAT_00064108 + i * 0x50`, then overwrites x and y from a 6-byte `COD` record. The record is at `file + 0x0b + (DAT_0006410c + i) * 6`. Byte 0 of that record becomes x and byte 2 becomes y. `MAP00.COD` begins `COD` and is 147 bytes, so the 6-byte stride reaches the last record with only a few bytes left; the fields past byte 2 were not read. Units at or above `DAT_00064114` are zeroed and get flag bit 0 set. `FUN_00023800` runs at the end of that load.

## Map, camera, and terrain

The picture is mode 13h, 320×200. A map frame is composed by `FUN_0002bcf0` into a buffer of `0x15180` bytes at pitch `0x168` (360). `FUN_0002c0c0` paints one section as 14 columns by 9 rows of 24×24 tiles, which is the 320×200 window with a partial tile at the right and bottom edges. The camera origin is in pixels. `DAT_00069ce4` is the horizontal origin and `DAT_00069ce0` the vertical one. The same two axes for the cursor are `DAT_00069cd4` and `DAT_00069ccc`.

`FUN_0002c0c0` divides the camera by 24 and keeps the remainder, so the window can sit between tile boundaries. For each of the 9×14 cells it wraps the tile coordinate across the section width and height (the shorts at MPL `+7` and `+9`). The MPL cell is the little-endian short at `file + 0x0b + (y * width + x) * 2`. That short is the tile-picture index.

Tile pixels come from the section CEL. Its header matches `ICON.CEL`: `CEL`, version `1`, then three big-endian shorts. Those shorts are the directory offset, the width, and the height. On `M000.CEL` they are `0x0f`, 24, and 24. The directory is little-endian dwords. The first dword is the file offset where the pictures begin, so the number of directory entries is `(first_offset - directory_offset) / 4`, and the last entry is the end of the last picture rather than a picture of its own. `FUN_0005664b` expands the picture selected by `dword[directory + index * 4]`.

Drawing one cell, from `FUN_0002c0c0`:

```
tile = mpl_short(x, y)
if layer_mode == 0:
    blit picture[tile] with expander mode 0
else:
    attr = byte[attr_file + 0x11 + tile * 4]
    kind = attr & 7
    if kind == 1: tile = tile + blink          # blink is 0 or 1, flipped every 4 ticks
    if kind == 2: tile = tile + ((tick >> 2) & 3) * 0x60
    if attr & 0x80:
        blit picture[tile], expander mode 9, using attr byte +1
    else if occupancy_byte(x, y) == 0xff:
        blit picture[tile], mode 0
    else:
        blit picture[tile], mode 9 or 10       # 10 when layer_mode == 1, else 9
```

`tick` is `DAT_00069d64`. `blink` is `DAT_00060160`. Across the `ATTR` files, the low 3 bits are only ever 0 or 2, so the two-frame blink is unused on disk and the four-step `* 0x60` animation is the one that occurs. Mode 0 is the plain expander below. Modes 9 and 10 are `FUN_0005738b` and `FUN_00057503`; they were not decompiled. They are what paints a tile that a unit is standing on, or a tile whose attribute has bit `0x80`.

`FUN_0002bcf0` draws every section whose byte `DAT_00069cfe[i]` is below 10, then the units (`FUN_0002cfd0`), then sections above 10. A section can therefore paint over the units. The visible copy out of the map buffer is 320×200 from buffer+`0x21d8` in the phase transition, and the combat copy is buffer+`0x2298` at pitch `0x170`.

`FUN_0002b790(x, y)` is the tile query. It reads the MPL short into `DAT_00069d04`, then the 4-byte `ATR` record for that picture:

| Record byte | Stored at | Use |
| --- | --- | --- |
| 0 | `DAT_00069d08` | The animation byte the drawer reads. |
| 1 | `DAT_00069d0a` | Passed to the expander when bit `0x80` of byte 0 is set. |
| 2 | `DAT_00069d09` | Terrain kind. Movement cost and the attack/defense percents index by this. |
| 3 | `DAT_00069d0b` | Backdrop. Combat loads `Back%02d.saf` from it, after decrementing it when it is nonzero. |

On disk, byte 2 takes values 0, 1, 2, 5, and 6. Byte 3 takes 55 distinct values, the largest 63, which matches the 63 backdrop files. For 59 of the 69 `ATTR` files the record count equals the CEL directory count minus one. The other 10 do not, so that sentinel rule is not universal.

Movement is a flood fill in `FUN_00010de0`. The occupancy grid is `width * height` byte pairs in front of which `FUN_000227b0` writes the two dimensions. `FUN_00010b20` sets each pair's second byte to `0xff` and masks the first with `0x3f`. The fill then treats the first byte's bit `0x40` as "do not enter" and bit `0x80` as "entering spends the whole remaining budget". The second byte is the best cost found so far. Cost of a step is `cost_here + move_row[terrain]`, where `move_row` is the 10-byte `ProMap.dat` row for the unit's class. Who stamps bit `0x40` and bit `0x80` was not read. The percents applied to attack and defense are signed dwords:

| Terrain | Attack %, dwords at `0x60040` | Defense %, dwords at `0x60058` |
| --- | --- | --- |
| 0 | +5 | 0 |
| 1 | 0 | 0 |
| 2 | −5 | +10 |
| 3 | −5 | +10 |
| 4 | −5 | −5 |
| 5 | 0 | 0 |
| 6 | 0, because it reads the first defense dword | the dword at `0x60070`, not copied here |

`FUN_00012550` returning nonzero skips that percent for that fighter. What it tests was not read.

## Selection, turns, and outcomes

`FUN_0002b870` is the body of one visit to the map. It polls a byte from `FUN_00056509` and ignores a held value until it has been seen more than five times. The effects below are what the comparisons do. The names in parentheses are the BIOS scan codes for those bytes.

| Byte | What it does |
| --- | --- |
| `0x48`, `0x50`, `0x4b`, `0x4d` (arrows) | Move the cursor one tile, inside the map, and play `Beep.wav`. |
| `0x01`, `0x2c`, `0x4c`, `0x53` | Center on the next side-`2` unit whose flag byte has bits `0x85` clear. |
| `0x39`, `0x1c` (space, enter) | `FUN_0002d830` picks the unit under the cursor. None opens `FUN_00014aa0`. A side-`2` unit with bit `0x80` clear and `+0x26` clear goes to `FUN_00015460`, then `FUN_0002e7a0` if the outcome dword is still 0. Anything else goes to `FUN_00016a90`. |
| `0x3b` | `FUN_0002def0`. |
| `0x3c`, `0x47` | `FUN_00016a90` on the unit under the cursor. |

The camera follows the cursor, keeping it away from the edges by a margin of about two tiles (`0x18` on the near side, `0x108` horizontally and `0x90` vertically on the far side).

`FUN_00015460` is the move. It flood-fills from the unit with budget `+0x3b`, then asks for a destination. Cancelling recenters and leaves the loop. A destination whose path result is 0 opens a menu (`FUN_00015cf0`) without changing the tile. Any other accepted destination writes the new tile into bytes `+0` and `+1` unless `DAT_00060004` is set, in which case the unit stays and the action is committed through `FUN_000119b0`. After the loop, if `DAT_00069d90` is not `0xff`, it calls `(&DAT_000601c4)[DAT_00069d90](unit)`. It always then calls `(&DAT_0006028c)[scenario]()`.

`DAT_0006028c` is a table of code pointers indexed by the scenario, parallel to the start-of-scenario table at `0x60304` but not the same pointers. The first is `0x3a120`. These bodies were not created as functions. Disassembly of `0x3a120`, not a decompile: it calls `FUN_000109b0(2)`, and that function returns bit 0 of unit 2's flag byte. If the bit is set, it pushes the loaded text block and the constant `0xf` into a call, then writes `1` to `DAT_00069da0` and returns. The other scenarios were not disassembled. The outer loop already treats `1` as the `GameOver.saf` path and `2` as the per-scenario ending.

`FUN_0002e7a0` looks for a side-`2` unit that is still eligible (flag bits `0x81` clear, `+0x26` clear). If none remains, it calls `FUN_0001e3c0`, which is the turn change:

1. For each eligible side-`2` unit whose `+0x40` is not its `+0x42`, and whose `+0x25` and `+0x26` are 0, add `max / 5` to the second pool (`+0x44`), capped at `+0x46`. If any unit was changed, play `REST.WAV`.
2. `FUN_00012b20` walks side `1`. For each eligible unit it calls `FUN_00010010(unit, 1)`, then the same two callback tables as the player's action. It stops when `DAT_00069da0` becomes nonzero.
3. If the outcome is still 0, play `EnyPhase.saf`, then `FUN_00012960` walks side `0` the same way, with an extra distance test (`DAT_00063f88` and `DAT_00063f8c` against 5) in front of the call.
4. If the outcome is still 0, increment `DAT_00069ce8`, play `PlyPhase.saf`, and return to the cursor. A few item checks on the way back call `FUN_0001f4e0` when a carried byte has bit `0x40` and the second pool is not full.

`FUN_0002de50` and `FUN_0001fa00` are called with 1, then 0, then 2 around those walks. Their effect on the flag byte was not read. `FUN_00030a30(scenario, 0 or 1)` sits at the same points and was not read.

## Combat numbers

Two presentations share one formula. `FUN_00012e50` calls `FUN_00018d50` (the full `SAF` fight) when `DAT_00060010` is nonzero, and otherwise calls `FUN_0001c370`, which writes the pool immediately. The full fight computes the same number in `FUN_00019f60` and lets `FUN_000196b0` apply it on hit frames. `FUN_0001c4f0` is the immediate writer. The arithmetic in the two functions matches.

`rand` is `FUN_00042a68`. The equipped weapon is slot 0 through `FUN_00025110` and `FUN_000251d0`, then the record from `FUN_00018b30`. Weapon byte `+9` and byte `+10` are `kind` and `arg`.

```
attack  = attacker[+0x48]
defense = defender[+0x4a]
hp, max  = defender[+0x40], defender[+0x42]
hit      = attacker[+0x4c] - defender[+0x4e]
crit     = class_row[8]                 # ProMap.dat row for attacker[+0x20]

if terrain bonus applies to the attacker:
    attack  += attack  * attack_percent[terrain] / 100
if terrain bonus applies to the defender:
    defense += defense * defense_percent[terrain] / 100

if kind == 3: crit += arg
if kind == 4 and rand % 100 < arg: defender[+0x25] = rand % 4 + 2
if kind == 1 and rand % 100 < arg: defender[+0x26] = rand % 2 + 2
# the immediate path also refuses those two writes when class == 0x19
# the clip path asks FUN_00029050 instead

landed = rand % 100 < hit
if landed:
    if rand % 100 < crit: defense = defense / 2
    damage = (attack - defense) * 9 / 10
    if damage < 0: damage = 0
    if damage / 9 != 0: damage += rand % (damage / 9)
    hp = max(0, hp - damage)
```

Integer division is toward zero, as the compiled `/` on these ints does. A miss leaves the pool unchanged. `kind == 2`, or a roll below 3, makes `FUN_0001c370` run that whole resolution twice. The clip player has the same second-swing test.

On the immediate path, a side-`2` attacker and a defender whose character id is above `0x3b` also write `DAT_00069cec`:

```
row = FUN_00018b00(defender[+7] - 0x3c)
scale = attacker[+0x21]
if attacker[+7] > 10: scale += 0x1e
gain = defender[+0x21] * byte(row + 9) / scale
if hp != 0: gain = gain * damage / max
```

The clip path writes the same term only when the defender's side byte is `0`, which is a different condition. `FUN_0001e3c0` later does `DAT_00069cec = DAT_00069cec * 15 / 10` from `FUN_00012e50` before `FUN_0001dd00`. What the term is spent on was not followed. Inferred: it is the experience award, because it grows with damage dealt and shrinks against `scale`.

The bar drawn by `FUN_0001cad0` has `(hp * 0x29 + max - 1) / max` lit segments, so the bar is 41 steps. A counterattack happens when `FUN_000137e0` returns 1: the defender's `+0x26` is 0, the two units are one tile apart (absolute dx + dy equals 1), and the defender's equipped record has byte `+0xb == 1`.

## Drawing a battle, and extracting the pictures

`FUN_000194c0` slides the two standing clips in from the side over nine composed frames before `FUN_000196b0` plays the attack. Side byte `0` enters from the negative x direction (`-15` per frame) and any other side from the positive. The compose buffer is `0x16480` bytes, pitch `0x170`, and each frame is copied to `0xa0000` as 320×200 from buffer+`0x2298`, between two waits on bit 3 of the value `FUN_0003d254(0x3da)` returns. That is the vertical-retrace test. A landed hit still does the 6-step shake and the palette write described above.

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

To pull the pictures out: walk the VFS directory as already described, reject a member whose span passes the end of the archive, then run the decoder above into a buffer of `width * height` bytes. For a `SAF` clip, do that per cell and stamp the cells into the chunk's rectangle at the chunk's x,y. Hold, hit, and the mode byte stay beside the frame so a player can step it the way `FUN_00014540` does. Nothing here was checked by decoding a frame and looking at it.

## Extracting the text

`FDETXT##.TXT` is loaded to `DAT_00060124` for scenario index + 1. `FDETXT.FON` is 57344 bytes and is opened from `FUN_00029630`. The text block is not encoded characters. It is a table of 16-bit offsets into 16-bit glyph indexes, checked on `FDETXT00.TXT` (555 strings), `FDETXT01.TXT` (16), and `FDETXT02.TXT` (15):

```
count = first_u16 / 2
offset[i] = u16 at byte i*2, for i in 0 .. count-1
glyphs of string i = the u16s from offset[i] up to offset[i+1], or to EOF for the last
```

The offsets are nondecreasing and every span is an even number of bytes, so the strings tile the tail of the file. `FDETXT00.TXT` starts at byte `0x456`. The longest of those three files runs 371 glyphs.

57344 is `1792 * 32`. The first bytes of the font are `00 00 07 e0 1c 38 …`, which is the shape of 16-bit rows. Inferred: 1792 glyphs of 16×16 one bit per pixel, 32 bytes each, rows of two bytes. The function that references the loaded text block and was not decompiled is `FUN_00017c90`. Until that blit is read, the 16×16 cell is a size inference, not a measured destination rectangle.

An extractor walks the offset table, writes each string as a sequence of glyph indexes, and cuts the font into 32-byte cells in index order. It does not produce characters. The mapping from a glyph index to a character is the font bitmap, and a GBK scan of the text members still finds no Han bytes because the bytes were never encoded that way. The notes do not carry the strings.

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

`ICON.CEL` header begins `CEL \x01`, and the words that follow are the directory offset `0x0f` and size 24×24, in the same zero-padded layout as the other CEL headers (`00 0f 00 18 00 18`). `FUN_00023020` seeks to `0x0f`, reads `0x2970` bytes (2652 dwords), and treats each character as 12 dwords of frame offsets. The end of character `i` is the first offset of character `i + 1`. 221 groups of 12 fill the directory exactly, so character 220 has no end offset inside the table. The loader copies one character's bytes into a cache at `DAT_00060138` and stores 12 adjusted offsets per loaded character. Frame bytes are compressed: character 0's frames are 334–424 bytes, not `24*24`. `FUN_0005664b` expands a frame onto the map buffer at 24×24. Mode 0 of that expander is the opcode loop in the extraction section.

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
| `0x6028c` | After each action, one pointer per scenario. `0x3a120` was disassembled; the rest were not. |
| `0x60304` | Start-of-scenario dispatch, 30 pointers. Targets were not functions. |
| `0x10010` | What a side-`0` or side-`1` unit does on its phase. Not decompiled. |
| `0x12550` | Returns nonzero to skip the terrain percent. Not decompiled. |
| `0x15cf0` | Menu after a move. Not decompiled. |
| `0x17c90` | References the loaded text block. The glyph blit is in here and was not read. |
| `0x1a4a0` | Play a spell. |
| `0x288c0` | The other spell player, for the ids listed above. Not decompiled. |
| `0x293d0` | Loads `ProMap.dat` and the other `.dat` tables. Not decompiled. |
| `0x2de50` / `0x1fa00` | Called with a side number around the phase change. Not decompiled. |
| `0x30a30` | Called with the scenario index and 0 or 1 at the phase change. Not decompiled. |
| `0x567fd` | First of the expander modes other than 0. Not decompiled. |
| `0x5738b` / `0x57503` | Expander modes 9 and 10, used when a tile is occupied. Not decompiled. |

## Still unknown

- The unit bytes that are not in the table, and what the six item pairs mean. `+0x44` is inferred as a second pool, not measured against a spell.
- `MAP##.DAT` past byte 2, and the `COD` bytes past the x and y that spawn reads.
- What the `DTL` byte in `DAT_00069d06` changes. The readers are at `0x13e89`, `0x18527`, `0x2ddec`, and `0x2e727`.
- Which function writes occupancy bits `0x40` and `0x80`.
- The ten `ATTR` files whose record count is not the CEL directory count minus one.
- Expander modes other than 0, and the value of `EDX` at the mode-0 call.
- The glyph destination rectangle inside `FUN_00017c90`. The 16×16 cell is an inference from the file size.
- `ICONANI.VFS`, `FACE.CEL`, and the `Emg%02d` player at `0x28951`.
- The scenario bodies other than the disassembly of `0x3a120`, and the front end `0x2a280`.
- What the four `0xff` markers inside `FDE.SAV` delimit.
- `ProMap.dat` and the other tables named in `FUN_00018920`, field by field. The 10-byte row stride is from the index, not from a walk of the file.
