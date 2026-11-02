# Gaps

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the list of what is still missing for a full account of the design and the implementation. A finding goes in the topic file. An address, file, or field that was seen and not read is added here, under that topic's heading. A row is removed when the topic file records it.

## What a reconstruction still cannot do

The battle grid, the opening placement, the unit record that combat reads, the damage formula, the spell mask, and which picture a character id uses are written in the topic files. The holes below are what is still in the way of rebuilding a scenario, a turn, a character, a spell, and the screen from those notes.

- A scenario's files do not yet make a playable battle. The roster prefix and group 0 are placed. Most of the 26-byte actor record is unread, as are map bytes `0x33`–`0x52`, the unread `COD` fields, the `DTL` byte, the event-row handlers, 28 of the 30 opener bodies, the ending table, and the after-action table past the first scenario.
- Town is only partly described. The forced joins are known. The village actions, the path that skips the village, the item list, and two portrait callers are unread.
- A CPU turn's walk and its choice of target are written. The call that runs before the walk, the per-script hooks, the phase-change call, and the per-scenario after-action pointers are unread.
- A character cannot yet be built from the tables alone. Unit bytes outside the written table, the unread columns of `Friaprda.dat`, `EnemyDat.dat`, `MagicDat.dat`, and `ProMap.dat`, and the rank-up read are still open.
- A spell's mask is written. The body that plays the spell, the frames after the earthquake clip opens, and `MagicDat` bytes `+0` and `+1` are unread.
- The screen's windows and the map sprite are named in [Pictures](pictures.md). Expander modes 2, 4–8, and 12 still have no role. Icon-clip playback, the two fight remap blocks, the `FIGBAR` blit, and the reader of `CEL` byte 8 are unread.
- Text placement and the save record stop early. The glyph rectangle, the level-up number, and the save bytes after the four slot flags are unread.

## Session

| Address | What it is |
| --- | --- |
| `0x291f0` | Session loop. Disassembled, still not a Ghidra function. |
| `0x60074` | Scenario opener, 30 pointers. The append argument at each call site is in [Session](session.md). `0x20e60` and `0x20ec0` were read; the other bodies were not. |
| `0x60304` | Scenario ending, 30 pointers, called when the outcome dword is 2. Bodies were not decompiled. `0x3a120` is the after-action handler, not one of these. |
| `0x30540` | Called with `0x19` from sound startup. Not read. |
| `0x241b0` | Called when a scenario skips the village. Names `Save.cel` and `FDE.SAV`. The body was not read. |
| `0x35a30` | First village-menu action. It calls `FUN_000361d0`, which opens `Bonus-1.saf` and `Bonus.wav`. The rest of either body was not read. `0x35810` is the action that calls `FUN_00034310`. `0x355d0`, `0x35d40`, and `0x35f80` pass shop groups 0, 1, and 2. The rest of those four bodies was not read. |

## Turns

| Address | What it is |
| --- | --- |
| `0x6028c` | After each action, one pointer per scenario. `0x3a120` was disassembled; the rest were not. `FUN_00028280` is also called at `0x3a190`. |
| `0x184e0` | Called after the menu's rest slot. At `0x186d8` it opens the item list with the second argument 0. The rest of the body was not decompiled. |
| `0x33d70` / `0x33f80` | Also open that item list, both with the second argument 0. Not decompiled. |
| `0x24e70` | Draws the rows of the item list. Not decompiled. |
| `0x2d7e0` | Called with the unit before `FUN_000119e0` plays a CPU walk. Not decompiled. |
| `0x2dd20` | Called at the start of each unit in the first side-0 pass. Not decompiled. |
| `0x2d9b0` | Looks up the unit id in byte `+0x35` for scripts 3 and 9. Not decompiled. |
| `0x13e10` | Returns the tile script 5 walks to. Not decompiled. |
| `0x10760` / `0x26dd0` | Called for character ids `0x3c`..`0x3e` on script 11, and for the `Posion.saf` play on script 7. Not decompiled. |
| `0x2ddc0` | Called with the unit's tile at the end of every script except 8. Not decompiled. |
| `0x16120` / `0x161f0` / `0x161a0` | Draw, read, and close the menu inside slot 2. Not decompiled. |
| `0x30a30` | Called with the scenario index and 0 or 1 at the phase change. Not decompiled. |

## Map and scenario files

- `MAP##.DAT` bytes `0x33` through `0x52`. Bytes 3 through `0x32` are the sixteen event rows in [Scenario files](scenario.md). The handler bodies called from `0x601c4` were not read. The first pointer is `0x36920`.
- The short at `+4` of a `COD` record, and header byte 4 (1 or 16). Placement reads the coordinate shorts and not these.
- `FUN_00056523`, called at the end of the map load `FUN_00022720`. Body not read.
- `0x36920` calls `FUN_00023800`. The argument it passes, and the rest of the body, were not read. Icon opcodes 5, 9, 14, and 15 call `FUN_00021e00`, `FUN_000221b0`, `FUN_000223e0`, and `FUN_00022450`. Opcode 6 calls `FUN_00022290`, and opcode 97 calls `FUN_00023950`. Those six were not read. `FUN_00023a90` runs at the end of the roster append and was not read.
- What the `DTL` byte in `DAT_00069d06` changes. The readers are at `0x13e89`, `0x18527`, `0x2ddec`, and `0x2e727`.
- Why `M630` has 288 `ATTR` records and 192 pictures, and why `ATTR151.DAT` has no section CEL. `M310.CEL` is 192 pictures and does not expand with mode 0.
- `FUN_0002bfb0` and `FUN_0002cfd0`, called by the map compose `FUN_0002bcf0` around the range pictures. Bodies were not decompiled.

## Units

- The unit bytes that are not in the table in [Units](units.md). The eight pairs at `+0x0a` are written there. A cast subtracts the spell row's byte `+5` from `+0x44`. `FUN_00027570` adds to it and caps it at `+0x46`.
- Bytes `+2` and `+8` through `+0x11` of `Friaprda.dat`, and bytes `+8` and `+9` of `EnemyDat.dat`. The `RankUp.dat` read at `0x351e1` was not separated.
- The 26-byte record at `DAT_0006013c + index * 0x1a + 0x83`, past byte 0, byte `+1`, the scale byte at `+4`, and the group byte at `+0x15`.
- `FUN_000338f0` also looks up the equipped item whose type is `0x16` through `0x27`. The shop price itself is in [Scenario files](scenario.md).
- `FUN_00034310` adds byte `+9` to `+0x44` and is called from the village action at `0x35810`. The rest of the body was not decompiled. The copies of `+0x46` into `+0x44` at `0x3ae8f` and `0x3b3df` clear byte `+5`. The functions around those stores were not read.
- `MagicDat.dat` is 40 rows of 7 bytes. Byte `+2` is the chance read by `FUN_00028f40`. Byte `+3` is the spell budget, byte `+4` is the target `shape`, byte `+5` is the pool cost, and byte `+6` is the target side. How `+3` and `+4` mark tiles is in [Combat](combat.md). Bytes `+0` and `+1` were not walked. `ProMap.dat` is 41 rows of 10. The bytes past the move lookup and the crit byte at `+8` were not walked. The loader is `0x293d0` and was not decompiled.

## Combat

| Address | What it is |
| --- | --- |
| `0x1a4a0` | Play a spell. It subtracts the spell row's byte `+5` through `FUN_00028590`. The sequence is in [Pictures](pictures.md); the body was not read past that cost and the call into `FUN_000288c0`. |
| `0x288c0` | Formats `Emg%02d.saf` and, for id `0x21`, opens `Emg33-1.saf`. At `0x28942` it subtracts the spell row's byte `+5` from `+0x44`. The frames after the open were not walked. |

`DAT_00060010` is also touched at `0x13d6d`, `0x15268`, `0x18411`, `0x184ad`, `0x2414e`, `0x24363`, and `0x245af`. The stores were not separated from the reads. `Explo.Saf` and `Miss.wav` are named by the players. They were not among the top-level archive members already walked. `BASEWAV.VFS` inside `MISC.VFS` was not opened.

## Pictures

| Address | What it is |
| --- | --- |
| `0x56895` | Expander mode 2. It starts like mode 1 and then diverges. |
| `0x569ce` | Expander modes 4 through 8, at `0x569ce`, `0x56b9a`, `0x56e84`, `0x572c1`, `0x5735d`. |
| `0x577e4` | Expander mode 12. |
| `0x3edde` / `0x3f1f8` / `0x3eee2` | Called while a fight sample is started. Not decompiled. |

- `ICONANI.VFS` playback inside `FUN_00022290`, which opcode 6 calls. The opcode switch is in [Scenario files](scenario.md). `FACE.CEL` picture `n` is drawn by `FUN_000177c0` at 125×100. The call at `0x207d8` is inside `FUN_00020580` and passes that function's argument. The calls at `0x16790` and `0x20c1b` were not read.
- What the blocks at `DAT_000653f0` and `DAT_000643f0` hold. The fight replaces them from `FMer1.tmp` and `FMer2.tmp`, and restores `Mer1.tmp` and `Mer2.tmp` afterward.
- The blit of `FIGBAR.CEL`. The reader that applies `CEL` byte 8 was not reopened. What `BaseWav.vfs` and `BaseAni.vfs` play, and what `ADWin.cel` is drawn as, were not read. Where `Command.cel`, `Message.cel`, `Number.cel`, and `SelBar.cel` sit on the 320×200 screen was not read. The readers of `0x643c4` start at `0x15a62`.

## Text

- The glyph destination rectangle inside `FUN_00017c90` (`0x17c90`). The 16×16 cell and the 32-byte stride are stored by the font loader. `FUN_00017520` draws the amount added on a level, with id `0xa4`. Its body was not read.

## Save

- The save-slot bytes after the four flag bytes that the load row reads.
