# Gaps

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the list of what is still missing for a full account of the design and the implementation. A finding goes in the topic file. An address, file, or field that was seen and not read is added here, under that topic's heading. A row is removed when the topic file records it.

## What a reconstruction still cannot do

A battle, the campaign order, a character, and the town can be rebuilt from the topic files. The grid, placement, damage, the spell amount, the CPU walk, the phase scripts, the thirty successors, the fork at 26, the quit at 29, and each index's win and loss are written. So are the five village menus, the shop prices, the four save slots, and the icon opcodes. What is still unread does not add a rule to those systems.

- The `COD` short at `+4` and header byte 4 are not read by placement.
- The Miles bodies the fight-sample wrappers forward to, and the text calls other than the ones in [Text](text.md), [Turns](turns.md), and [Pictures](pictures.md). A new presentation can replace these. The screen that presentation replaces is the last section of [Pictures](pictures.md).

## What a modernised remake still has to decipher

Nothing in the battle rules, the campaign order, the win and loss of an index, the town, a character, or the screen still has to be deciphered before a design starts. The screen a new engine keeps is the last section of [Pictures](pictures.md). The unread items below are a few blits a new presentation can replace. Handler 21 is in [Scenario files](scenario.md). No map row selects it.

## Session

| Address | What it is |
| --- | --- |
| `object 1 + 0x34cbe`, `object 1 + 0x34e50`, `object 1 + 0x34d78` | The Miles bodies `object 1 + 0x2df06`, `object 1 + 0x2e15a`, and `object 1 + 0x2e323` forward to. The wrappers and the frequency `0x19` are in [Session](session.md). |
| `object 1 + 0x2f439` | Called when the register-timer wrapper logs. The body was not read. |
| `object 1 + 0x261d0` | Opens `Bonus-1.saf` and `Bonus.wav` from the bar menu. The frames were not walked. |

## Turns

| Address | What it is |
| --- | --- |
| `object 1 + 0x6120` | Draws the command diamond. The steps are in [Pictures](pictures.md). The body was disassembled, not decompiled. |
| `object 1 + 0x2c458` | Called every 75 ticks before `object 1 + 0x2c5cb` restarts the track. The body was not read. The caller is in [Turns](turns.md). |
| `object 1 + 0x1a280` | Stores into `object 2 + 0x158` besides the title row that sets it to 1. Those stores were not read. The village saves the byte and the ending of index 29 sets it, in [Session](session.md). The panel is in [Turns](turns.md). |

## Map and scenario files

- The short at `+4` of a `COD` record, and header byte 4 (1 or 16). Placement reads the coordinate shorts and not these.
- The pointers at `object 2 + 0x9cb0`, `object 2 + 0x9c20`, and `object 2 + 0x9c98`, one triple per `object 2 + 0x9cdc` entry. `object 1 + 0x212b0` frees them. What they hold was not read.
- The `.dat` members beside the icon clips were not read as anything beyond the opcode walk in [Scenario files](scenario.md). Opcode 6's player is in [Pictures](pictures.md).
- Why `M630` has 288 `ATTR` records and 192 pictures, and why `ATTR151.DAT` has no section CEL. `M310.CEL` is 192 pictures and does not expand with mode 0. `M31.DTL` is 51 by 64 and 6545 bytes, longer than `16 + width * height`. The bytes past the first `51 * 64` were not read.
- `object 1 + 0x1bfb0` and `object 1 + 0x1cfd0`, called by the map compose `object 1 + 0x1bcf0` around the range pictures. Bodies were not decompiled.

## File formats

- `Icon%04d.wav` is the name icon opcode 8 formats. No member of that name is in `ICONANI.VFS` or `BaseWav.vfs`.
- `%s\Pack.vfs` and `%s\%s.Aud` are named in the executable. The intro path names `FD1.Aud`. None of those files was among the data files walked. The track bytes the music call uses are in [Turns](turns.md).

## Pictures

| Address | What it is |
| --- | --- |
| `object 1 + 0x2ec6b` / `object 1 + 0x2f26e` | Called on the sample slot before the address is set. Bodies not read. The order is in [Pictures](pictures.md). |
| `object 1 + 0x37010` / `object 1 + 0x37040` / `object 1 + 0x37080` / `object 1 + 0x37150` / `object 1 + 0x37160` | The bodies the five sample wrappers forward to. |
| `object 1 + 0x34cb2` / `object 1 + 0x2d3e6` / `object 1 + 0x34ef3` | The log gate around those wrappers. Bodies not read. |

- `FACE.CEL` picture `n` is drawn by `object 1 + 0x77c0` at 125×100. The call at `object 1 + 0x107d8` is inside `object 1 + 0x10580` and passes that function's argument. The call at `object 1 + 0x10c1b` is the portrait finish in [Text](text.md). The status sheet draws it at `(19, 4)`, in [Pictures](pictures.md). The call at `object 1 + 0x6790` was not read.
- `object 1 + 0x1fbd0` and `object 1 + 0x1ffc0` reveal the spell rectangle and were not decompiled. The message dismiss also calls `object 1 + 0x1ffc0`, with selectors 15, 13, 11, 9, 7, and 5, in [Pictures](pictures.md). `object 1 + 0x200f0` copies the rising experience strip and was not decompiled.
- `object 1 + 0x68d0` runs the status blit for steps 5 down through 0. The rest of that body was not read. Calls of `object 1 + 0x6e70` at `object 1 + 0x15a7a`, `object 1 + 0x15e77`, and `object 1 + 0x17ce0`, and calls of `object 1 + 0x68d0` at `object 1 + 0x15aab`, `object 1 + 0x15f6f`, and `object 1 + 0x17d11`, pass two screens that were not read. The status-sheet call is in [Pictures](pictures.md).
- The channel bytes of the scenario palette pulse, copied from `object 1 + 0x1b030`. The periods and the first indexes are in [Pictures](pictures.md). The bytes were not split per scenario.
- `object 1 + 0x2d0f3` is the heap walk `object 1 + 0x2d0e5` returns. A size of 0 returns 0. The rest of the body was not read.
- Rows 2 and 4 of `NUMBER.CEL`, and the stores of `object 2 + 0xc` other than the status sheet and the terrain panel. `BaseWav.vfs` and `BaseAni.vfs` are the nested archives in [File formats](formats.md). The calls that play one named wave were not decompiled. `ADWin.cel` is the panel in [Turns](turns.md). `SELBAR.CEL` picture 0 on the item list is in [Pictures](pictures.md). The other selection-bar blits, at `object 1 + 0x1773a`, `object 1 + 0x226b7`, `object 1 + 0x22ea4`, and `object 1 + 0x25279`, were not reduced. The roster picker uses picture 2, in [Turns](turns.md). The call at `object 1 + 0x5b31` passes 2 to `object 1 + 0x2d0e0` just before the viewport copy. The wait is in [Session](session.md).

## Text

- The store that advances `object 3 + 0x1d`, the key ring's other index. The reader and the clear are in [Text](text.md).
- The destination, pitch, and palette indexes at the `object 1 + 0xff30` calls other than the ones in [Text](text.md), [Turns](turns.md), and the status sheet in [Pictures](pictures.md).
- Stores of `object 2 + 0x4030`, `object 2 + 0x4034`, and `object 2 + 0x4038` other than the ones already written. The chest, the sale, the gift, and the empty-list insert are in [Turns](turns.md). The buy confirm stores all three, in [Scenario files](scenario.md). The drop stores `object 2 + 0x4030` in [Combat](combat.md), and `object 1 + 0x24310` stores one of each in [Units](units.md). `object 1 + 0xe340` stores the rolled level amount at `object 2 + 0x4038`, in [Combat](combat.md). Further stores sit in the rest of `object 1 + 0x24310`, `object 1 + 0xd960` (`object 2 + 0x4038`), and `object 1 + 0xfa00`.

## Save

- `object 1 + 0x14460` copies the scenario byte and the four bytes after the gold dword, in [Save](save.md). The call at `object 1 + 0x14605` was not read. `object 2 + 0x4110` is written from the dword `0x14` bytes before the scenario byte when `object 2 + 0x70` is 0. Its other readers were not read.
