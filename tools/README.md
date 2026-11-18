# Tools

Programs a later study can run on another game. Read this file before writing a program that opens a container or an asset. When a row already names it, use that program.

A script that only names one game's files stays in that game's `scripts/`. When the walk is a container or a format another program can have, the program goes here and the game script calls it. The procedure for that split is [procedure.md](../procedure.md).

| Program | When to use it |
| --- | --- |
| [unpack_lzexe.py](unpack_lzexe.py) | A DOS MZ executable whose bytes at file offset `0x1c` are `LZ91`. |

`python tools/unpack_lzexe.py INPUT OUTPUT` reads the compressed executable and writes the expanded MZ. Notes cite offsets from the start of that expanded image. The program does not write into the local copy.
