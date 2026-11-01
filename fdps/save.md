# Save file

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`FUN_00014e90` is the system menu and the writer of `FDE.SAV`. The file is one 22987-byte buffer (`0x59cb`), which matches the copy on disk. Layout written in order:

| Offset | Size | Contents |
| --- | --- | --- |
| `0x0000` | `0x8a3` (2211) | current `MAP##.DAT` |
| `0x08a3` | `0xa00` (2560) | block at `DAT_00064108` |
| `0x12a3` | `count * 0x50` | the unit array |
| `0x30a3` | `0x20` | flags at `DAT_000640d8` |
| `0x30c3` | | scenario byte, unit count, scenario index, then four camera values each already divided by 24 |
| `0x59c7` | 4 | checksum from `FUN_00056608` over the first `0x59cb` bytes |

Empty-slot bytes `0xff` are written at `0x3b2b`, `0x4553`, `0x4f7b`, and `0x59a3` when the file did not already exist. Those are the scenario byte of four slots. `FUN_00024460` reads a slot at `0x312b + slot * 0xa28`: `0xa00` bytes into the roster block, then the scenario byte, one more byte into the roster threshold, a dword, and four flag bytes. The bytes after that were not read. Which title row calls that loader is in [Session](session.md). The unit array it restores is in [Units](units.md).
