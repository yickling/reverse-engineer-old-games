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

Read the file for the question in front of you. Add a finding to that file. Add an address that is still unread to [Gaps](gaps.md), under the same heading.

| Note | What it holds |
| --- | --- |
| [Binary](binary.md) | LE objects, the real entry, and the CRT. |
| [Session](session.md) | Startup, the title, the session loop, the village, and the scenario openers. |
| [Turns](turns.md) | Cursor, move, the phase change, and the after-action tables. |
| [Scenario files](scenario.md) | What a scenario index loads, the battle grid that index selects, and how units are placed on it. |
| [Map](map.md) | Camera, tiles, terrain bytes, movement cost, and what a section's order and highlight bytes do to a range. |
| [Units](units.md) | The 80-byte unit record. |
| [Combat](combat.md) | The map-to-fight handoff, the damage formula, and what a destroyed unit does. |
| [Pictures](pictures.md) | The picture decoder, `SAF` clips, battle playback, map sprites, and the frame extractor. |
| [Text](text.md) | Glyph-index strings, the font cell, and where a string is drawn. |
| [Archives](archives.md) | The VFS directory. |
| [Save](save.md) | `FDE.SAV`, including the four load slots. |
| [Gaps](gaps.md) | What is still missing for a full account of the design and the implementation. |

## Still open

The open list is [Gaps](gaps.md). Add an address, file, or field that was seen and not read there, under the same heading as the topic. Remove it when the topic file records the finding.
