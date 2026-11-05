# Gaps

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the list of what is still missing for a full account of the design and the implementation. A finding goes in the topic file. An address, file, or field that was seen and not read is added here, under that topic's heading. A row is removed when the topic file records it.

## Reconstruction

A reconstruction of the battle, the campaign, a character, and the town is possible from the topic files. The grid, placement, damage, the spell amount, the CPU walk, the phase scripts, the thirty successors, the fork at 26, the quit at 29, each index's win and loss, the five village menus, the shop prices, the four save slots, and the icon opcodes are written.

The original sample driver is the piece still outside that reconstruction. It becomes possible once `object 1 + 0x2da33` and `object 1 + 0x35cc0` are read. The first is the driver call that starts a sample with `0x401`. The second runs when the sample type changes. A new presentation can play the sample from the fields in [Pictures](pictures.md) without those two calls.

The original music is the other piece still outside. The track numbers and the CD-ROM request are in [File formats](formats.md). The audio itself is not among the files that were walked, so that piece stays outside until the disc's tracks are present. The studio movie is the same kind of gap: `FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud` are named in [Session](session.md) and were not among the files walked. The handoff is in [Opening](opening.md).

## Remake

A modernised remake is possible from the topic files. The battle rules, the campaign order, the win and loss of an index, the town, a character, and the screen are written, and the unread items below do not block a design. The original music is CD audio, in [File formats](formats.md), and a remake supplies its own. The screen a new engine keeps is the last section of [Pictures](pictures.md). Handler 21 is in [Scenario files](scenario.md). No map row selects it.

## Session

| Address | What it is |
| --- | --- |
| `object 1 + 0x34cbe`, `object 1 + 0x34e50`, `object 1 + 0x34d78` | The Miles bodies `object 1 + 0x2df06`, `object 1 + 0x2e15a`, and `object 1 + 0x2e323` forward to. The wrappers and the frequency `0x19` are in [Session](session.md). |
| `object 1 + 0x2f439` | Called when the register-timer wrapper logs. The body was not read. |
| `object 1 + 0x261d0` | Opens `Bonus-1.saf` and `Bonus.wav` from the bar menu. The clip's frames are in [Pictures](pictures.md). The playback body was not read. |

## Turns

| Address | What it is |
| --- | --- |
| `object 1 + 0x2bf87`, `object 1 + 0x2c16a`, `object 1 + 0x2c26f`, `object 1 + 0x2c316`, `object 1 + 0x2c51a` | Other device requests beside the CD play path in [File formats](formats.md). No direct call was found. The bodies were not read. |

## Map and scenario files

- Why `M630` has 288 `ATTR` records against 192 pictures, and why `ATTR151.DAT` has no section CEL. The counts are in [Map](map.md). `M31.DTL` is longer than `16 + width * height`. The 3265 bytes after the tiles have no reader, in [File formats](formats.md). `MAP31.DAT` holds thirteen 26-byte records and byte 2 is 2. No reader of the records past that byte was shown.
- Byte `+3` of an `MPL`, `ATTR`, and `DTL` header, and the bytes between that header and the payload: `ATTR` `+7` through `+0x10`, and `DTL` `+0x0b` through `+0x0f`. The structs name them. No reader was found.
- `object 1 + 0x1bfb0` and `object 1 + 0x1cfd0`, called by the map compose `object 1 + 0x1bcf0` around the range pictures. Bodies were not decompiled.

## Pictures

| Address | What it is |
| --- | --- |
| `object 1 + 0x2ec6b` / `object 1 + 0x2f26e` | Called on the sample slot before the address is set. Bodies not read. The order is in [Pictures](pictures.md). |
| `object 1 + 0x35cc0` | Called when the sample type at handle `+0x34` or `+0x38` changes. The stores are in [Pictures](pictures.md). |
| `object 1 + 0x2da33` | The driver call sample start issues with `0x401`. |
| `object 1 + 0x34cb2` / `object 1 + 0x2d3e6` / `object 1 + 0x34ef3` | The log gate around those wrappers. Bodies not read. |

- The `FACE.CEL` call at `object 1 + 0x6790`. The other portrait calls are in [Pictures](pictures.md) and [Text](text.md).
- `object 1 + 0x1fbd0` and `object 1 + 0x1ffc0` reveal the spell rectangle and were not decompiled. The message dismiss also calls `object 1 + 0x1ffc0`, with selectors 15, 13, 11, 9, 7, and 5, in [Pictures](pictures.md). `object 1 + 0x200f0` copies the rising experience strip and was not decompiled.
- `object 1 + 0x68d0` runs the status blit for steps 5 down through 0. The rest of that body was not read. Calls of `object 1 + 0x6e70` at `object 1 + 0x15a7a`, `object 1 + 0x15e77`, and `object 1 + 0x17ce0`, and calls of `object 1 + 0x68d0` at `object 1 + 0x15aab`, `object 1 + 0x15f6f`, and `object 1 + 0x17d11`, pass two screens that were not read. The status-sheet call is in [Pictures](pictures.md).
- The channel bytes of the scenario palette pulse, copied from `object 1 + 0x1b030`. The periods and the first indexes are in [Pictures](pictures.md). The bytes were not split per scenario.
- `object 1 + 0x2d0f3` is the heap walk `object 1 + 0x2d0e5` returns. A size of 0 returns 0. The rest of the body was not read.
- Rows 2 and 4 of `NUMBER.CEL`, and the stores of `object 2 + 0xc` other than the status sheet and the terrain panel. The row select is in [Pictures](pictures.md).
- The selection-bar blits at `object 1 + 0x1773a`, `object 1 + 0x226b7`, `object 1 + 0x22ea4`, and `object 1 + 0x25279`. Picture 0 and the roster's picture 2 are in [Pictures](pictures.md) and [Turns](turns.md).
- The call at `object 1 + 0x5b31` passes 2 to `object 1 + 0x2d0e0` just before the viewport copy. The wait is in [Session](session.md).

## Text

- The store that advances `object 3 + 0x1d`, the key ring's other index. The reader and the clear are in [Text](text.md).
- Calls of `object 1 + 0xff30` whose destination is computed and was not reduced to a pixel: `object 1 + 0x14fb5`, `object 1 + 0x177af`, `object 1 + 0x230e2`, `object 1 + 0x237e0`, `object 1 + 0x23b89`, `object 1 + 0x23bfe`, `object 1 + 0x23c34`, `object 1 + 0x25378`, `object 1 + 0x253b5`, and `object 1 + 0x29ea6`. Ink, fill, and shadow match the constant calls in [Text](text.md).

## Units

- Byte `+0x0a` of an `Item.dat` row. No reader was found. The other fields are the struct in [Units](units.md).

## Save

- The call at `object 1 + 0x14605`, inside the save loader in [Save](save.md). `object 2 + 0x4110` is written from the dword `0x14` bytes before the scenario byte when `object 2 + 0x70` is 0. Its other readers were not read.
