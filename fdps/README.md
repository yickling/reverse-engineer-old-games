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
| `0x20c30` | Called by the two openers that were read, between the icon file and the camera. Not read. |
| `0x21620` | Loads `Icon##.dat`. Body not read. |
| `0x241b0` | Briefing shown when a scenario skips the village. Not read. |
| `0x35a30` | First village-menu action. Not read. The other four are `0x35810`, `0x355d0`, `0x35d40`, `0x35f80`. |

### Turns

| Address | What it is |
| --- | --- |
| `0x6028c` | After each action, one pointer per scenario. `0x3a120` was disassembled; the rest were not. |
| `0x10010` | What a side-`0` or side-`1` unit does on its phase. Not decompiled. |
| `0x27bf0` / `0x25280` | Menu slots 1 and 2 inside `FUN_00015cf0`. Not decompiled. |
| `0x16120` / `0x161f0` / `0x161a0` | Draw and read that menu. Not decompiled. |
| `0x2de50` / `0x1fa00` | Called with a side number around the phase change. Not decompiled. |
| `0x30a30` | Called with the scenario index and 0 or 1 at the phase change. Not decompiled. |

### Map and scenario files

- `MAP##.DAT` past byte 2, and the `COD` bytes past the x and y that spawn reads.
- What the `DTL` byte in `DAT_00069d06` changes. The readers are at `0x13e89`, `0x18527`, `0x2ddec`, and `0x2e727`.
- Which function writes occupancy bits `0x40` and `0x80`.
- The ten `ATTR` files whose record count is not the CEL directory count minus one.
- The tail after the counted pictures in `M190.CEL`, `M290.CEL`, and `M620.CEL`. `M310.CEL` is ordered to the end of the file and does not expand with mode 0.

### Units

- The unit bytes that are not in the table, and what the six item pairs mean. `+0x44` is inferred as a second pool, not measured against a spell.
- `ProMap.dat` and the other tables named in `FUN_00018920`, field by field. The 10-byte row stride is from the index, not from a walk of the file. The loader is `0x293d0` and was not decompiled.

### Combat

| Address | What it is |
| --- | --- |
| `0x1a4a0` | Play a spell. The sequence is in [Pictures](pictures.md); the body was not read past that. |
| `0x288c0` | The other spell player, for the ids listed in [Pictures](pictures.md). Not decompiled. |
| `0x29050` | Gate on the weapon status write inside `FUN_00019f60`. Not decompiled. |
| `0x13c90` / `0x27150` | The two actions `FUN_00012c10` takes instead of a swing. Not decompiled. |
| `0x12230` / `0x13420` / `0x13040` | Fill the three scores that choose among those actions. Not decompiled. |
| `0x1e340` / `0x28280` / `0x24d40` | The level-up stat write, the learned-row call, and the call beside them. Not decompiled. |
| `0x25cf0` / `0x25990` | Called from the death-record walk when the first byte is 0. Not decompiled. |

`DAT_00060010` is also touched at `0x13d6d`, `0x15268`, `0x18411`, `0x184ad`, `0x2414e`, `0x24363`, and `0x245af`. The stores were not separated from the reads. `Explo.Saf` and `Miss.wav` are named by the players. They were not among the top-level archive members already walked. `BASEWAV.VFS` inside `MISC.VFS` was not opened.

### Pictures

| Address | What it is |
| --- | --- |
| `0x567fd` | Expander modes other than 0 and 3. Mode 3 is the hit recolor in [Pictures](pictures.md). |
| `0x5738b` / `0x57503` | Expander modes 9 and 10, used when a tile is occupied. Not decompiled. |

- `ICONANI.VFS` playback, and the `Emg%02d` player at `0x28951`. `EMG33-1.SAF` is in `MISC.VFS`; that pattern does not name it. `FACE.CEL` is 160 pictures of 125×100; which screen draws one was not read.
- The calls that open `Fight.pal` (string at `0x61cd4`) and `Fde.pal` (string at `0x61a78`).
- Who plays `BONUS-1.SAF`, `CHAPTER.SAF`, `ENYPHASE.SAF`, `GAMEOVER.SAF`, and `PLYPHASE.SAF`. `LOGO.SAF` is the startup clip in [Session](session.md).

### Text

- The glyph destination rectangle inside `FUN_00017c90` (`0x17c90`). The 16×16 cell and the 32-byte stride are stored by the font loader.

### Save

- The save-slot bytes after the four flag bytes that the load row reads.
