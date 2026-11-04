# Work log

Part of the [FDPS notes](README.md). This is extraction still to do for a scenario-0 demo. It is not a finding about the program. A finished item is checked here. Findings stay in the topic files.

Pictures, text, named waves, and `SAF` samples for one visit are already in [extract](extract/). Music is a later extract. Do not extract it here, and do not extract the pictures, text, or samples again.

`extract/` stays on disk and is not committed. The local copy of the program is only read. Do not create or change files there, and do not name that directory in a note. A new extractor goes in [scripts](scripts/) and takes the data directory as an argument.

## Open

## Done

- [x] Scenario-0 records

The pictures are not enough to play the visit. The grid indexes, the terrain byte on each picture, who stands where, the icon script that places them, and the stat rows are still only in the data files. A demo that reads [extract](extract/) and not those files needs the records below written out as JSON. The field names and the offsets are the packed structs in [File formats](formats.md), [Scenario files](scenario.md), and [Units](units.md). A field the struct marks unread stays in the JSON with no role added.

Write `extract/scenario/00/`:

| File | JSON |
| --- | --- |
| `MAP00.DAT` | `map.json`. Header bytes, the sixteen turn rows, the sixteen step pairs, the sixteen find triples, and each 26-byte actor. |
| `MAP00.COD` | `cod.json`. One record per slot: the id short and the two coordinate shorts. |
| `M000.MPL` | `grid.json`. Width, height, and the cell shorts in row-major order. Picture `N` is `extract/maps/tiles/M000/frame_NNN.png`. |
| `ATTR000.DAT` | `attr.json`. One object per 4-byte record, in order: `anim`, `tint`, `terrain`, `backdrop`. |
| `M00.DTL` | `dtl.json`. Width, height, and one byte per tile. Map 0 names no step handler. The byte is still the one a search reads. |
| `DSC00.DAT` | `dsc.json`. The section count and each section's eight dwords. |
| `ICON00.DAT` | `icon.json`. The opcode bytes, in order, each with the opcode and its operand bytes. Opcode 0 ends the file. The lengths are the table in [Scenario files](scenario.md). |

Write `extract/tables/` from the `MISC.VFS` members. One JSON array per file, one object per row, fields in file order:

| Member | Rows | Stride |
| --- | --- | --- |
| `FRIAPRDA.DAT` | 60 | `0x18` |
| `FRILEVUP.DAT` | 60 | `0x0b` |
| `ENEMYDAT.DAT` | 91 | `0x0a` |
| `ITEM.DAT` | 251 | `0x17` |
| `PROMAP.DAT` | 41 | `0x0a` |
| `PROEQU.DAT` | 36 | 6 |
| `MAGICDAT.DAT` | 40 | 7 |
| `GETMGTAB.DAT` | 60 | `0x0c` |
| `RANKUP.DAT` | 9 | `0x0c` |

`ITEM.DAT` is 5773 bytes, which is 251 times `0x17`. The visit uses character 0 from `FRIAPRDA` and the map actors. Ids 12, 74, 79, and 82 are the character ids `MAP00` stores. Ids at or above `0x3c` read `ENEMYDAT` at `id - 0x3c`. Write every row of each table anyway.

Leave `SHOP00.DAT` out. Leave the music out.

Done when both directories are on disk, each row ends at or before the end of its file, `grid.json` is 30 by 24, and `map.json` actor count matches `0x83 + count * 26` against the 703-byte file. Then check this item.

- [x] Map pictures for one visit to scenario 0

Scenario 0 is one section, `M000.CEL`, plus the twelve map frames of the units that visit draws, plus the windows that visit opens. Frame 0 of every character is already `extract/unit-ids/icons/`. A full sheet, four rows of three, exists there only for ids 0, 3, 10, and 60, and those sheets are scaled up. The visit needs the 24×24 frames.

Run the extractor that already implements this, `scripts/extract_cel_pictures.py`. Pass the data directory that contains `ICON.CEL`, `FACE.CEL`, `FIELD1.VFS`, and `MISC.VFS`. Pass `--out` as this game's `extract/` directory. Pass `--only icons`, `--only tiles`, and `--only ui`. Do not pass `--only faces`.

That write adds three trees next to the ones already there:

- `extract/maps/icons/CHAR###/` — twelve frames, `frame_000.png` through `frame_011.png`, and a sheet of four rows of three. The demo uses ids 0, 12, 74, 79, and 82. The script writes every character.
- `extract/maps/tiles/M000/` — that section's tiles. The script writes every section `.cel`. `M310.CEL` does not expand with mode 0 and is skipped. Scenario 0 does not use it.
- `extract/ui/` — every `.cel` in `MISC.VFS`. The visit opens `CUSOR`, `COMMAND`, `MESSAGE`, `SHADOW`, `ICONSTS`, `NUMBER`, and `ADWIN`.

Done when those three trees are on disk, `M000` is not recorded as skipped, and each of `CHAR000`, `CHAR012`, `CHAR074`, `CHAR079`, and `CHAR082` has twelve frames. Then check this item and leave the rest of the file as it is.
