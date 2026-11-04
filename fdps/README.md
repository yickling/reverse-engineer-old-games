# FDPS analysis notes

Flame Dragon Plus (炎龙骑士团外传), a DOS/4GW game in `fdps/`. These notes are from static analysis of `FDPS.EXE` and the data files next to it. Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

The real entry was never turned into a Ghidra function, so the top-level loop in [Session](session.md) is from disassembly of the flat image. The same is true of the thirty openers, the thirty endings, the thirty after-action checks, and the step handlers: Ghidra had not created functions there, and those notes are disassembly. A body these notes do not call a disassembly was decompiled. A bare selector that is not already a function decompiles the wrong body, as below.

## How to reopen the binary

`FDPS.EXE` is a Watcom C/C++32 (1988–1994) Linear Executable inside an MZ stub. A tool that cannot load that container needs a flat image relocated at the object bases in the header. The object map and the CRT are in [Binary](binary.md).

An address in these notes is an offset from an object's own base in the executable: `object 1 + 0x33008` is the entry, wherever a tool places object 1. `0xa0000` is the VGA framebuffer, not one of those objects. A number that is not already inside a function can be taken as a file offset and open the wrong body. The real entry was not where analysis started, and no function was created at `object 1 + 0x191f0` or at the scenario-dispatch handlers around `object 1 + 0x2a180`.

`DOS4GW.EXE` is the extender. `SETSOUND.EXE` and the `.DIG` files are Miles AIL 3.02. `PlayGame.exe` and the NSIS pieces are a later Windows launcher. Game logic is only in `FDPS.EXE`.

## Notes

Read the file for the question in front of you. Add a finding to that file. When the finding is a function or a table, add the row to [Functions](functions.md). Add an address that is still unread to [Gaps](gaps.md), under the same heading.

| Note | What it holds |
| --- | --- |
| [Binary](binary.md) | LE objects, the real entry, and the CRT. |
| [Session](session.md) | Startup, the title, the session loop, the village, and the scenario openers. |
| [Opening](opening.md) | The reconstruction of the studio logo, the external movie, and the sequence before the first battle. |
| [Turns](turns.md) | Cursor, move, the phase change, and the after-action tables. |
| [Scenario files](scenario.md) | What a scenario index loads, the battle grid that index selects, and how units are placed on it. |
| [Map](map.md) | Camera, tiles, terrain bytes, movement cost, and what a section's order and highlight bytes do to a range. |
| [Units](units.md) | The 80-byte unit record. |
| [Combat](combat.md) | The map-to-fight handoff, the damage formula, and what a destroyed unit does. |
| [Pictures](pictures.md) | The picture decoder, `SAF` clips, battle playback, map sprites, the frame extractor, and the screen a new engine keeps. |
| [Text](text.md) | Glyph-index strings, the font cell, where a string is drawn, and the extracted reading. |
| [Archives](archives.md) | The VFS directory. |
| [File formats](formats.md) | On-disk layouts of sprites, scenario files, maps, strings, and sound. |
| [Save](save.md) | `FDE.SAV`, including the four load slots. |
| [Functions](functions.md) | Which bodies were decompiled, which were disassembled, and which were only seen, and the data tables. |
| [Gaps](gaps.md) | What is still missing for a full account of the design and the implementation. |

The extractors are in [scripts](scripts/). They write into [extract](extract/). `scripts/extract_fight_sprites.py` writes the fight frames, `scripts/extract_cel_pictures.py` writes the map and interface pictures, `scripts/extract_text.py` writes the scenario strings, and `scripts/extract_sounds.py` writes the named waves and the `SAF` samples, and `scripts/extract_videos.py` writes the cinematic `SAF` clips. What each one writes is in [Pictures](pictures.md), [Text](text.md), and [File formats](formats.md).

## Still open

The open list is [Gaps](gaps.md). Add an address, file, or field that was seen and not read there, under the same heading as the topic. Remove it when the topic file records the finding, and add the function or the table to [Functions](functions.md).
