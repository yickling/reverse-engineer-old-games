# Executable layout

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

`e_lfanew` is `0x2a50`, signature `LE`. Objects, with virtual size, base, flags, page index, page count:

| Object | Base | Virtual size | Flags | Pages |
| --- | --- | --- | --- | --- |
| 1 code | `0x10000` | `0x479d0` | `0x2045` (32-bit, preload, executable, readable) | index 1, 72 pages |
| 2 data/stack | `0x60000` | `0xc3c0` | `0x2043` | index 73, 4 initialized pages |
| 3 tiny data | `0x70000` | `0x54` | `0x2043` | index 77, 1 page |

ESP is the top of object 2 (`0xc3c0`). EIP is object 1 + `0x33008`, so the entry address is `0x43008`. Those bytes are a short jump over the Watcom copyright banner into the CRT at `0x43080`.

Page-table entries are a 3-byte big-endian page number plus a flags byte. File offset of page `N` is `0xf000 + (N - 1) * 0x1000`. Fixup records sit between the fixup page-table dwords (table at LE+`0x248`, records at LE+`0x380`). 6836 fixups were applied when the flat image was built, plus one 16-bit selector fixup at VA `0x565af` in object 3. A source-type 7 record replaces the dword at the site with `object_base + target`. The stored dword is already the target offset; it is not added a second time.

The CRT at `0x43080` detects the extender with INT 21h AH=30h (high word `XD` = `0x4458` is DOS/4G). The C startup at `0x4dcbc` calls `0x4e402`, `0x54b2c`, then `call 0x291f0` with globals `0x6a3b8` and `0x6a3b4`, then exits through `0x42b7f`. There is no import table. DOS calls are INT 21h and DPMI INT 31h. VGA mode 13h (320×200×256) goes through a real-mode interrupt wrapper at `0x42fd8` with interrupt `0x10`. Exit restores text mode 03h. The framebuffer is `0xa0000`, 64000 bytes.

Watcom prologues are `53 56 57 55` (push ebx/esi/edi/ebp). At least 486 of them are in the image. FunctionID was not installed, so the CRT shows up as `FUN_`.
