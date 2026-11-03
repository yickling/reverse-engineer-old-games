# Gaps

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the list of what is still missing for a full account of the design and the implementation. A finding goes in the topic file. An address, file, or field that was seen and not read is added here, under that topic's heading. A row is removed when the topic file records it.

## What a reconstruction still cannot do

A battle, the campaign order, a character, and the town can be rebuilt from the topic files. The grid, placement, damage, the spell amount, the CPU walk, the phase scripts, the thirty successors, the fork at 26, the quit at 29, and each index's win and loss are written. So are the five village menus, the shop prices, the four save slots, and the icon opcodes. What is still unread does not add a rule to those systems.

- Handler 21 at `0x378e0` stores 1 into `0x640e8`, and no map names it. The rest of that body was not read. `FUN_0001ba10`, called on the quit paths of indexes 26 and 29, was not read. `0x312b0`, called when the bar's load returns 1, was not read past its file opens.
- The `COD` short at `+4` and header byte 4 are not read by placement. `FUN_00056523`, at the end of the map load, was not read.
- The spell player `0x1a4a0` past the pool cost and the amount, and the frames after an earthquake clip opens, were not read.
- The unit bytes that the table and the paragraphs in [Units](units.md) do not name.
- The fight sample calls, the status bar's own blit, the nine status pages, and the text calls other than the ones in [Text](text.md), [Turns](turns.md), and [Pictures](pictures.md). A new presentation can replace these. The screen that presentation replaces is the last section of [Pictures](pictures.md).

## What a modernised remake still has to decipher

Nothing in the battle rules, the campaign order, the win and loss of an index, the town, a character, or the screen still has to be deciphered before a design starts. The screen a new engine keeps is the last section of [Pictures](pictures.md). The unread items below are one unnamed handler, the file call on two quit paths, the tail of a spell's animation, and a few blits a new presentation can replace.

## Session

| Address | What it is |
| --- | --- |
| `0x1ba10` | Called by endings 26 and 29 before the quit byte. The two temp files and the `0x1d` branch are in [Session](session.md). The body was not read. |
| `0x378e0` | Handler 21. Stores 1 into `0x640e8`. No row or pair of the map files selects it. The rest of the body was not written up. |
| `0x30540` | Called with `0x19` from sound startup. Not read. |
| `0x312b0` | Called when the bar's load returns 1. It frees the scenario text and opens that scenario's files, in [Turns](turns.md). The rest of the body was not read. |
| `0x361d0` | Opens `Bonus-1.saf` and `Bonus.wav` from the bar menu. The frames were not walked. |

## Turns

| Address | What it is |
| --- | --- |
| `0x16120` | Draws the command diamond. The steps are in [Pictures](pictures.md). The body was disassembled, not decompiled. |
| `0x161f0` / `0x161a0` | Read and close the menu. The corners they return are in [Turns](turns.md). The bodies were not decompiled. |
| `0x15bd0` | Called after the six roster cells in `FUN_00033440`. Not decompiled. |
| `0x2a280` | Stores into `DAT_00060158` besides the title row that sets it to 1. Those stores were not read. The village saves the byte and the ending of index 29 sets it, in [Session](session.md). The panel is in [Turns](turns.md). |

## Map and scenario files

- The short at `+4` of a `COD` record, and header byte 4 (1 or 16). Placement reads the coordinate shorts and not these.
- `FUN_00056523`, called at the end of the map load `FUN_00022720`. Body not read.
- The `.dat` members beside the icon clips were not read as anything beyond the opcode walk in [Scenario files](scenario.md). Opcode 6's player is in [Pictures](pictures.md).
- Why `M630` has 288 `ATTR` records and 192 pictures, and why `ATTR151.DAT` has no section CEL. `M310.CEL` is 192 pictures and does not expand with mode 0. `M31.DTL` is 51 by 64 and 6545 bytes, longer than `16 + width * height`. The bytes past the first `51 * 64` were not read.
- `FUN_0002bfb0` and `FUN_0002cfd0`, called by the map compose `FUN_0002bcf0` around the range pictures. Bodies were not decompiled.

## Units

- The unit bytes that the table and the paragraphs in [Units](units.md) do not name.
- The loader `FUN_000293d0` was not decompiled. The rows it loads are the structs in [Units](units.md).

## Combat

| Address | What it is |
| --- | --- |
| `0x1a4a0` | Play a spell. It subtracts the spell row's byte `+5` through `FUN_00028590`, and `FUN_000282f0` applies the amount, in [Combat](combat.md). The rest of the body was not read. |
| `0x288c0` | Formats `Emg%02d.saf` and, for id `0x21`, opens `Emg33-1.saf`. At `0x28942` it subtracts the spell row's byte `+5` from `+0x44`. The frames after the open were not walked. |

`DAT_00060010` is flipped by the settings corner in [Turns](turns.md), written at file offset `0x30d1` by the save in [Save](save.md), and compared at `0x13d6d` by the cast in [Combat](combat.md). `Explo.saf` is a member of `BaseAni.vfs`, and `Miss.wav` is a member of `BaseWav.vfs`. Both archives are in [File formats](formats.md).

- In `FUN_00013920`, a target whose byte `+8` is 0 replaces the spell band with the value left on the FPU stack. The value loaded before `FUN_0003d25c` was not separated.
- The line taken by the item scorer when range byte `+0x10` is at least `0x10`. The call is in [Combat](combat.md). The body was not decompiled.

## File formats

- `Icon%04d.wav` is the name icon opcode 8 formats. No member of that name is in `ICONANI.VFS` or `BaseWav.vfs`.
- `%s\Pack.vfs` and `%s\%s.Aud` are named in the executable. The intro path names `FD1.Aud`. None of those files was among the data files walked. The track bytes the music call uses are in [Turns](turns.md).

## Pictures

| Address | What it is |
| --- | --- |
| `0x3edde` / `0x3f1f8` / `0x3eee2` | Called while a fight sample is started. Not decompiled. |

- `FACE.CEL` picture `n` is drawn by `FUN_000177c0` at 125×100. The call at `0x207d8` is inside `FUN_00020580` and passes that function's argument. The call at `0x20c1b` is the portrait finish in [Text](text.md). The status sheet draws it at `(19, 4)`, in [Pictures](pictures.md). The call at `0x16790` was not read. `FUN_00042a68` is the call whose result, modulo 200, starts the mode-8 hop, and it is the `rand` the level roll uses. Its body was not read.
- `FUN_00017730` draws the two status fills. The width and the two origins are in [Pictures](pictures.md). The body was not read. `FUN_00016e70` runs nine times on that sheet and was not read. `FUN_0002fbd0` and `FUN_0002ffc0` reveal the spell rectangle and were not decompiled. `FUN_000300f0` copies the rising experience strip and was not decompiled.
- Rows 2 and 4 of `NUMBER.CEL`, and the stores of `DAT_0006000c` other than the status sheet and the terrain panel. `BaseWav.vfs` and `BaseAni.vfs` are the nested archives in [File formats](formats.md). The calls that play one named wave were not decompiled. `ADWin.cel` is the panel in [Turns](turns.md). `SELBAR.CEL` picture 0 on the item list is in [Pictures](pictures.md). The other selection-bar blits, at `0x2773a`, `0x326b7`, `0x32ea4`, and `0x35279`, were not reduced. The roster picker uses picture 2, in [Turns](turns.md). The call at `0x15b31` passes 2 to `0x3d0e0` just before the viewport copy. That callee was not read.

## Text

- The destination, pitch, and palette indexes at the `FUN_0001ff30` calls other than the ones in [Text](text.md), [Turns](turns.md), and the status sheet in [Pictures](pictures.md).
- Stores of `DAT_00064030`, `DAT_00064034`, and `DAT_00064038` other than the ones already written. The chest, the sale, the gift, and the empty-list insert are in [Turns](turns.md). The buy confirm stores all three, in [Scenario files](scenario.md). The drop stores `DAT_00064030` in [Combat](combat.md), and `FUN_00034310` stores one of each in [Units](units.md). `FUN_0001e340` stores the rolled level amount at `DAT_00064038`, in [Combat](combat.md). Further stores sit in the rest of `FUN_00034310`, `FUN_0001d960` (`DAT_00064038`), and `FUN_0001fa00`.

## Save

- `FUN_00024460` copies the scenario byte and the four bytes after the gold dword, in [Save](save.md). The call at `0x24605` was not read. `DAT_00064110` is written from the dword `0x14` bytes before the scenario byte when `DAT_00060070` is 0. Its other readers were not read.
