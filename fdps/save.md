# Save file

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`object 1 + 0x4e90` is the system menu and the writer of `FDE.SAV`. The file is one 22987-byte buffer (`0x59cb`), which matches the copy on disk. Layout written in order:

| Offset | Size | Contents |
| --- | --- | --- |
| `0x0000` | `0x8a3` (2211) | current `MAP##.DAT` |
| `0x08a3` | `0xa00` (2560) | block at `object 2 + 0x4108` |
| `0x12a3` | `count * 0x50` | the unit array |
| `0x30a3` | `0x20` | flags at `object 2 + 0x40d8` |
| `0x30c3` | 1 | turn counter `object 2 + 0x9ce8` |
| `0x30c4` | 1 | unit count |
| `0x30c5` | 1 | scenario index |
| `0x30c6` | 4 | camera x, camera y, cursor x, cursor y, each already divided by 24 |
| `0x30ca` | 2 | both written 0 |
| `0x30cc` | 1 | roster count `object 2 + 0x4114` |
| `0x30cd` | 4 | `object 2 + 0x43b8` |
| `0x30d1` | 1 | `object 2 + 0x10` |
| `0x30d2` | 1 | `object 2 + 0x158` |
| `0x30d3` | 1 | `object 2 + 0x8` |
| `0x30d4` | 1 | `object 2 + 0x9d70` |
| `0x59c7` | 4 | checksum from `object 1 + 0x46608` over the first `0x59cb` bytes |

`object 1 + 0x13df0` reads the same buffer back. A checksum that does not match the dword at `0x59c7` shows interface string `0x208` and the load continues. It copies the roster block, stores the scenario byte, and calls `object 1 + 0x127b0`. It then replaces the map block with the `0x8a3` bytes at the front and stores map byte 1 and byte 2 in `object 2 + 0x4118` and `object 2 + 0x410c`. The unit array is allocated to `0x1e00` bytes, 96 slots, and `count * 0x50` bytes are copied in. Each unit's byte `+2` is filled again from `ICON.CEL`. The turn counter, the camera, the cursor, the roster count, `object 2 + 0x43b8`, and the four option bytes are copied from `0x30c3` onward. `object 1 + 0x1e6a0` then advances the marked tiles, the map is redrawn, `PlyPhase.saf` plays, and the phase music is called with argument 0.

Empty-slot bytes `0xff` are written at `0x3b2b`, `0x4553`, `0x4f7b`, and `0x59a3` when the file did not already exist. Those are the scenario byte of four slots. `object 1 + 0x14460` reads a slot at `0x312b + slot * 0xa28`. It copies `0xa00` bytes into the roster at `object 2 + 0x4108`. The next byte is the scenario index. The byte after that is the roster count `object 2 + 0x4114`. The dword at `+2` is `object 2 + 0x43b8`. Bytes `+6` through `+9` are `object 2 + 0x158`, `object 2 + 0x10`, `object 2 + 0x8`, and `object 2 + 0x9d70`. When `object 2 + 0x70` is 0, the dword `0x14` bytes before the scenario byte is stored at `object 2 + 0x4110`. The call at `object 1 + 0x14605` was not read. Which title row calls that loader is in [Session](session.md). The unit array it restores is in [Units](units.md).

`object 1 + 0x141b0` is the writer of those four slots. It opens `Save.cel`, and `object 1 + 0x14620` returns the chosen slot. A return other than 1 leaves. Otherwise it reads `FDE.SAV` when the file opens and fills `0x59cb` bytes with `0xff` when it does not. The slot at `0x312b + slot * 0xa28` receives `0xa00` bytes from the roster. The last `0x14` bytes of that copy are then overwritten: `object 2 + 0x4110`, then the minute and hour from DOS time function `0x2c`, then the day and month from DOS date function `0x2a`. The byte after the `0xa00` is the scenario index, the next byte is the roster count, the dword at `+2` is `object 2 + 0x43b8`, and bytes `+6` through `+9` are `object 2 + 0x158`, `object 2 + 0x10`, `object 2 + 0x8`, and `object 2 + 0x9d70`. The buffer is written back with mode `wb`, and the `Save.cel` menu runs again. The argument is blitted on the way out. The skipped-scenario call and the bar corner are in [Session](session.md) and [Turns](turns.md).
