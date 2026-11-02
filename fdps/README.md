# FDPS analysis notes

Flame Dragon Plus (炎龙骑士团外传), a DOS/4GW game in `fdps/`. These notes are from static analysis of `FDPS.EXE` and the data files next to it. Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

The real entry was never turned into a Ghidra function, so the top-level loop in [Session](session.md) is from disassembly of the flat image. Everything else cited as a `FUN_` address was decompiled.

## How to reopen the binary

`FDPS.EXE` is a Watcom C/C++32 (1988–1994) Linear Executable inside an MZ stub. REA rejects that (`unsupported LE executable in MZ image`) before any provider runs. The analysis target is a relocated flat image, not the EXE. The object map and the CRT are in [Binary](binary.md).

- Image: `/tmp/fdps-flat.bin` (393269 bytes). SHA-256 `5f010ea722e0f449ce6d19dd1215ce01a7b39f45fdfdd8dd1b733ad6d66af291`.
- Open as raw-binary, architecture `x86`, entry `0x10000`, provider `ghidra`. File offset 0 is address `0x10000`. Address `A` is file offset `A - 0x10000`.
- Ghidra 12.1.4 at `~/.local/opt/ghidra_12.1.4_PUBLIC`, JDK 21 at `~/.local/opt/jdk-21.0.13+9`. Language `x86:LE:32:default`, compiler spec `gcc`, loader `BinaryLoader`.
- A bare `0x` selector that is not an existing function falls back to a file-offset mapping and decompiles the wrong body. Ask for `file-offset:0x…` of a byte that sits inside a function Ghidra already created.
- The image was seeded at `0x10000`, not the real entry `0x43008`. Auto-analysis did not create a function at main (`0x291f0`) or at the scenario-dispatch handlers around `0x3a180`.

`DOS4GW.EXE` is the extender. `SETSOUND.EXE` and the `.DIG` files are Miles AIL 3.02. `PlayGame.exe` and the NSIS pieces are a later Windows launcher. Game logic is only in `FDPS.EXE`.

## Notes

Read the file for the question in front of you. Add a finding to that file. Add an address that is still unread to the list below, under the same heading.

| Note | What it holds |
| --- | --- |
| [Binary](binary.md) | LE objects, the real entry, and the CRT. |
| [Session](session.md) | Startup, the title, the session loop, the village, and the scenario openers. |
| [Turns](turns.md) | Cursor, move, the phase change, and the after-action tables. |
| [Scenario files](scenario.md) | What a scenario index loads, and how units are placed. |
| [Map](map.md) | Camera, tiles, terrain bytes, and movement cost. |
| [Units](units.md) | The 80-byte unit record. |
| [Combat](combat.md) | The map-to-fight handoff, the damage formula, and what a destroyed unit does. |
| [Pictures](pictures.md) | The picture decoder, `SAF` clips, battle playback, map sprites, and the frame extractor. |
| [Text](text.md) | Glyph-index strings and the font cell. |
| [Archives](archives.md) | The VFS directory. |
| [Save](save.md) | `FDE.SAV`, including the four load slots. |

## Still open

### Session

| Address | What it is |
| --- | --- |
| `0x291f0` | Session loop. Disassembled, still not a Ghidra function. |
| `0x60074` | Scenario opener, 30 pointers. `0x20e60` and `0x20ec0` were read; the rest were not. |
| `0x60304` | Scenario ending, 30 pointers, called when the outcome dword is 2. Bodies were not decompiled. `0x3a120` is the after-action handler, not one of these. |
| `0x30540` | Called with `0x19` from sound startup. Not read. |
| `0x21620` | Loads `Icon##.dat`. Body not read. |
| `0x241b0` | Briefing shown when a scenario skips the village. Not read. |
| `0x35a30` | First village-menu action. It calls `FUN_000361d0`, which opens `Bonus-1.saf` and `Bonus.wav`. The rest of either body was not read. `0x35810` is the action that calls `FUN_00034310`. `0x355d0`, `0x35d40`, and `0x35f80` pass shop groups 0, 1, and 2. The rest of those four bodies was not read. |

### Turns

| Address | What it is |
| --- | --- |
| `0x6028c` | After each action, one pointer per scenario. `0x3a120` was disassembled; the rest were not. `FUN_00028280` is also called at `0x3a190`. |
| `0x184e0` | Called after the menu's rest slot. At `0x186d8` it opens the item list with the second argument 0. The rest of the body was not decompiled. |
| `0x33d70` / `0x33f80` | Also open that item list, both with the second argument 0. Not decompiled. |
| `0x24e70` | Draws the rows of the item list. Not decompiled. |
| `0x11460` | Picks the destination of the budget-100 walk. Not decompiled. |
| `0x2d9b0` | Looks up the unit id in byte `+0x35` for scripts 3 and 9. Not decompiled. |
| `0x13e10` | Returns the tile script 5 walks to. Not decompiled. |
| `0x10760` / `0x26dd0` | Called for character ids `0x3c`..`0x3e` on script 11, and for the `Posion.saf` play on script 7. Not decompiled. |
| `0x2ddc0` | Called with the unit's tile at the end of every script except 8. Not decompiled. |
| `0x16120` / `0x161f0` / `0x161a0` | Draw, read, and close the menu inside slot 2. Not decompiled. |
| `0x2de50` | Called with a side number around the phase change, beside `FUN_0001fa00`. Not decompiled. |
| `0x30a30` | Called with the scenario index and 0 or 1 at the phase change. Not decompiled. |

### Map and scenario files

- `MAP##.DAT` past byte 2, and the `COD` bytes past the x and y that spawn reads.
- What the `DTL` byte in `DAT_00069d06` changes. The readers are at `0x13e89`, `0x18527`, `0x2ddec`, and `0x2e727`.
- Which function writes occupancy bits `0x40` and `0x80`.
- Why `M630` has 288 `ATTR` records and 192 pictures, and why `ATTR151.DAT` has no section CEL. `M310.CEL` is 192 pictures and does not expand with mode 0.

### Units

- The unit bytes that are not in the table. The eight pairs at `+0x0a` are in [Units](units.md). A cast subtracts the spell row's byte `+5` from `+0x44`. `FUN_00027570` adds to it and caps it at `+0x46`.
- Bytes `+2` and `+8` through `+0x11` of `Friaprda.dat`, and bytes `+8` and `+9` of `EnemyDat.dat`. The `RankUp.dat` read at `0x351e1` was not separated. `FUN_0002de50`, called beside the status countdown, was not read.
- The 26-byte roster record at `DAT_0006013c + index * 0x1a + 0x83`, past the scale byte at `+4` that spawn multiplies with.
- `FUN_000338f0` also looks up the equipped item whose type is `0x16` through `0x27`. The shop price itself is in [Scenario files](scenario.md).
- `FUN_00034310` adds byte `+9` to `+0x44` and is called from the village action at `0x35810`. The rest of the body was not decompiled. The copies of `+0x46` into `+0x44` at `0x3ae8f` and `0x3b3df` clear byte `+5`. The functions around those stores were not read.
- `MagicDat.dat` is 40 rows of 7 bytes. Byte `+2` is the chance read by `FUN_00028f40`. Byte `+3` is the spell budget and byte `+5` is the pool cost. The other bytes were not walked. `ProMap.dat` is 41 rows of 10. The bytes past the move lookup and the crit byte at `+8` were not walked. The loader is `0x293d0` and was not decompiled.

### Combat

| Address | What it is |
| --- | --- |
| `0x1a4a0` | Play a spell. It subtracts the spell row's byte `+5` through `FUN_00028590`. The sequence is in [Pictures](pictures.md); the body was not read past that cost and the call into `FUN_000288c0`. |
| `0x288c0` | Formats `Emg%02d.saf` and, for id `0x21`, opens `Emg33-1.saf`. At `0x28942` it subtracts the spell row's byte `+5` from `+0x44`. The frames after the open were not walked. |
| `0x118f0` / `0x11da0` / `0x13670` | Called while a score lists stand tiles and targets. Not decompiled. |

`DAT_00060010` is also touched at `0x13d6d`, `0x15268`, `0x18411`, `0x184ad`, `0x2414e`, `0x24363`, and `0x245af`. The stores were not separated from the reads. `Explo.Saf` and `Miss.wav` are named by the players. They were not among the top-level archive members already walked. `BASEWAV.VFS` inside `MISC.VFS` was not opened.

### Pictures

| Address | What it is |
| --- | --- |
| `0x56895` | Expander mode 2. It starts like mode 1 and then diverges. |
| `0x569ce` | Expander modes 4 through 8, at `0x569ce`, `0x56b9a`, `0x56e84`, `0x572c1`, `0x5735d`. |
| `0x57686` | Expander modes 11 and 12. Mode 12 is `0x577e4`. |

- `ICONANI.VFS` playback. `FUN_00021620` loads `Icon##.dat` and is called from each scenario opener; its body was not read. `FACE.CEL` picture `n` is drawn by `FUN_000177c0` at 125×100. The calls are at `0x16790`, `0x207d8`, and `0x20c1b`, and those callers were not read.

### Text

- The glyph destination rectangle inside `FUN_00017c90` (`0x17c90`). The 16×16 cell and the 32-byte stride are stored by the font loader. `FUN_00017520` draws the amount added on a level, with id `0xa4`. Its body was not read.

### Save

- The save-slot bytes after the four flag bytes that the load row reads.
