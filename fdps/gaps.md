# Gaps

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the list of what is still missing for a full account of the design and the implementation. A finding goes in the topic file. An address, file, or field that was seen and not read is added here, under that topic's heading. A row is removed when the topic file records it.

## What a reconstruction still cannot do

The battle grid, the opening placement, the unit record that combat reads, the damage formula, the spell mask, and which picture a character id uses are written in the topic files. The holes below are what is still in the way of rebuilding a scenario, a turn, a character, a spell, and the screen from those notes.

- A scenario's files do not yet make a playable battle. The roster prefix and group 0 are placed. The successor of each index is in [Session](session.md). The opener differences, the after-action checks, and the handlers a row names are in [Session](session.md), [Turns](turns.md), and [Scenario files](scenario.md). Twelve step-pair handlers are still unread, listed under Map and scenario files. The unread `COD` fields remain. Actor bytes `+2` and `+3` are in [Units](units.md). The `DTL` byte and map bytes `0x33`–`0x82` are in [Turns](turns.md).
- Town is the five menus in [Turns](turns.md). The slot writer is in [Save](save.md). The portrait call at `0x16790` is unread, and so is `0x312b0` past the file opens and the frames inside `FUN_000361d0`.
- A CPU turn's walk, its choice of target, the camera call before the walk, the script hooks, the phase music, and the per-scenario after-action checks are in [Turns](turns.md).
- A character's rows are the structs in [Units](units.md). What is still open is the unit bytes outside that file's table, and item types `0x16` through `0x27`.
- A spell's mask, its signed power, and the amount taken off the pool are written. The rest of the spell player, and the frames after the earthquake clip opens, are unread.
- The map window, the command icons, the message box, the expander modes, and icon-clip playback are in [Pictures](pictures.md). The two fight remap blocks, the `FIGBAR` blit, and where the remaining windows sit are unread.
- Text placement stops early. The calls written in [Text](text.md) and [Turns](turns.md) have a destination. The other calls, and the level-up number, are unread. The save writer and the load of that buffer are in [Save](save.md). The title-slot load's four flag bytes are in [Save](save.md). The call at `0x24605` was not read.

## What a modernised remake still has to decipher

A battle can be assembled from the notes that exist: the grid, the roster prefix and group 0, the unit fields combat reads, the damage formula, the spell mask, character id to pictures, and the CPU walk and its choice of target. The strings are read. The map window, command icons, message box, and fight frames can be drawn. The holes below are what still stops a playable campaign. Window coordinates, the original font, digit origins, selection bars, `FIGBAR`, the fight remap blocks, and the sound-driver startup can be replaced by a new presentation.

A scenario is not yet a script that can be replayed.

- `FUN_0001ba10`, called by endings 26 and 29. The stores of `0x640e9` are in [Session](session.md). The stores of `0x640e8` that a map can reach are in [Scenario files](scenario.md).

A turn's scripts, the search on the fourth command corner, the no-unit menu, and the five village menus are in [Turns](turns.md).

A character's rows are the structs in [Units](units.md). A spell's amount is in [Combat](combat.md).

- The unit bytes outside the table in [Units](units.md), and item types `0x16` through `0x27`.
- The spell player `0x1a4a0` past the pool cost and the amount, and the frames after an earthquake clip opens.
- The save writer and its load are in [Save](save.md). The title-slot load's four flag bytes are in [Save](save.md). The call at `0x24605` was not read. `0x312b0`, called when the bar's load returns 1, was not read past its file opens.

## Session

| Address | What it is |
| --- | --- |
| `0x291f0` | Session loop. Disassembled, still not a Ghidra function. |
| `0x60074` | Scenario opener, 30 pointers. The append argument and the other difference in each body are in [Session](session.md). |
| `0x60304` | Scenario ending, 30 pointers, called when the outcome dword is 2. The successor store and `FUN_00023950` are in [Session](session.md). `0x3a120` is the after-action handler, not one of these. |
| `0x1ba10` | Called by endings 26 and 29 before the quit byte. The two temp files and the `0x1d` branch are in [Session](session.md). The body was not read. |
| `0x640e8` | The stores a step can reach are in [Scenario files](scenario.md). Handler 21 at `0x378e0` also stores 1, and no map names it. The rest of that body was not written up. |
| `0x30540` | Called with `0x19` from sound startup. Not read. |
| `0x35a30` | Bar menu. The corners are in [Turns](turns.md). `FUN_000361d0` opens `Bonus-1.saf` and `Bonus.wav`. The frames inside that call were not walked. `0x312b0` is the call when the load returns 1. |

## Turns

| Address | What it is |
| --- | --- |
| `0x6028c` | After each action, one pointer per scenario. The thirty checks are in [Turns](turns.md). |
| `0x16120` | Draws the command diamond. The steps are in [Pictures](pictures.md). The body was disassembled, not decompiled. |
| `0x161f0` / `0x161a0` | Read and close the menu. The corners they return are in [Turns](turns.md). The bodies were not decompiled. |
| `0x15bd0` | Called after the six roster cells in `FUN_00033440`. Not decompiled. |
| `0x2a280` | Stores into `DAT_00060158` besides the title row that sets it to 1. Those stores were not read. The village saves the byte and the ending of index 29 sets it, in [Session](session.md). The panel is in [Turns](turns.md). |
| `0x1071f`, `0x1570d`, `0x15740`, `0x157cc`, `0x2d1ff`, `0x2d308`, `0x2d416`, `0x2d540` | Other calls of `FUN_0002ddc0`. The third argument was not reduced. |

## Map and scenario files

- Pair handlers 13, 22, 27, 30, 35, 37, 38, 39, 41, 45, 46, and 47. Which map pair names each one, and the six pair handlers that were read, are in [Scenario files](scenario.md). Bytes `0x33` through `0x82` of `MAP##.DAT` are the pairs and triples in that file.
- The short at `+4` of a `COD` record, and header byte 4 (1 or 16). Placement reads the coordinate shorts and not these.
- `FUN_00056523`, called at the end of the map load `FUN_00022720`. Body not read.
- The `.dat` members beside the icon clips were not read as anything beyond the opcode walk in [Scenario files](scenario.md). Opcode 6's player is in [Pictures](pictures.md).
- Why `M630` has 288 `ATTR` records and 192 pictures, and why `ATTR151.DAT` has no section CEL. `M310.CEL` is 192 pictures and does not expand with mode 0. `M31.DTL` is 51 by 64 and 6545 bytes, longer than `16 + width * height`. The bytes past the first `51 * 64` were not read.
- `FUN_0002bfb0` and `FUN_0002cfd0`, called by the map compose `FUN_0002bcf0` around the range pictures. Bodies were not decompiled.

## Units

- The unit bytes that are not in the table in [Units](units.md). The eight pairs at `+0x0a` are written there. A cast subtracts the spell row's byte `+5` from `+0x44`. `FUN_00027570` adds to it and caps it at `+0x46`.
- `FUN_000338f0` also looks up the equipped item whose type is `0x16` through `0x27`. The shop price itself is in [Scenario files](scenario.md). The rank change `FUN_00034310` is in [Units](units.md). The copies at `0x3ae8f` and `0x3b3df` are endings 18 and 23, in [Session](session.md).
- The loader `FUN_000293d0` was not decompiled. The rows it loads are the structs in [Units](units.md).

## Combat

| Address | What it is |
| --- | --- |
| `0x1a4a0` | Play a spell. It subtracts the spell row's byte `+5` through `FUN_00028590`, and `FUN_000282f0` applies the amount, in [Combat](combat.md). The rest of the body was not read. |
| `0x288c0` | Formats `Emg%02d.saf` and, for id `0x21`, opens `Emg33-1.saf`. At `0x28942` it subtracts the spell row's byte `+5` from `+0x44`. The frames after the open were not walked. |

`DAT_00060010` is flipped by the settings corner in [Turns](turns.md) and restored by the save load in [Save](save.md). It is also touched at `0x13d6d`, `0x15268`, `0x24363`, and `0x245af`. Those four were not separated. `Explo.saf` is a member of `BaseAni.vfs`, and `Miss.wav` is a member of `BaseWav.vfs`. Both archives are in [File formats](formats.md).

## File formats

- `Icon%04d.wav` is the name icon opcode 8 formats. No member of that name is in `ICONANI.VFS` or `BaseWav.vfs`.
- `%s\Pack.vfs` and `%s\%s.Aud` are named in the executable. The intro path names `FD1.Aud`. None of those files was among the data files walked. The track bytes the music call uses are in [Turns](turns.md).

## Pictures

| Address | What it is |
| --- | --- |
| `0x3edde` / `0x3f1f8` / `0x3eee2` | Called while a fight sample is started. Not decompiled. |

- `FACE.CEL` picture `n` is drawn by `FUN_000177c0` at 125×100. The call at `0x207d8` is inside `FUN_00020580` and passes that function's argument. The call at `0x20c1b` is the portrait finish in [Text](text.md). The call at `0x16790` was not read. `FUN_00042a68` is the call whose result, modulo 200, starts the mode-8 hop. Its body was not read.
- What the blocks at `DAT_000653f0` and `DAT_000643f0` hold. The fight replaces them from `FMer1.tmp` and `FMer2.tmp`, and restores `Mer1.tmp` and `Mer2.tmp` afterward.
- The blit of `FIGBAR.CEL`. `BaseWav.vfs` and `BaseAni.vfs` are the nested archives in [File formats](formats.md). The calls that play one named wave were not decompiled. `ADWin.cel` is the panel in [Turns](turns.md). `NUMBER.CEL` digits step by 6 inside `FUN_00017520`; the origin at each of its callers was not reduced. `SELBAR.CEL` picture 0 on the item list is in [Pictures](pictures.md). The other selection-bar blits, at `0x2773a`, `0x326b7`, `0x32ea4`, and `0x35279`, were not reduced. The roster picker uses picture 2, in [Turns](turns.md). The call at `0x15b31` passes 2 to `0x3d0e0` just before the viewport copy. That callee was not read.

## Text

- The destination, pitch, and palette indexes at the `FUN_0001ff30` calls other than the ones in [Text](text.md) and [Turns](turns.md).
- Stores of `DAT_00064030`, `DAT_00064034`, and `DAT_00064038` other than the ones already written. The chest, the sale, the gift, and the empty-list insert are in [Turns](turns.md). The drop stores `DAT_00064030` in [Combat](combat.md), and `FUN_00034310` stores one of each in [Units](units.md). Further stores sit in `FUN_000338f0`, the rest of `FUN_00034310`, `FUN_0001d960` (`DAT_00064038`), `FUN_0001e340`, and `FUN_0001fa00`.
- `FUN_00018340`, which supplies the three numbers on the loss window. `DAT_000643b8` is the eight-digit number drawn at `(87, 121)` there. The cursor search adds a short to it, and the save writes it at `0x30cd`. What `FUN_00018340` counts was not read.
- `FUN_00017520` draws the amount added on a level, with id `0xa4`. The 6×8 digit blit is in [Pictures](pictures.md). How the amount is split into digits was not read.

## Save

- `FUN_00024460` copies the scenario byte and the four bytes after the gold dword, in [Save](save.md). The call at `0x24605` was not read. `DAT_00064110` is written from the dword `0x14` bytes before the scenario byte when `DAT_00060070` is 0. Its other readers were not read.
