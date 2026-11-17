#!/usr/bin/env python3
"""Write one PNG per cell of FDETXT.FON, and the cell indexes of each string.

The font is the FDETXT.FON member of FIELD.VFS. Cell n is 32 bytes, 16 rows
of two bytes, as in text.md. The high bit of a byte is the leftmost pixel.
A set bit is an opaque white pixel. A clear bit is transparent. The PNG is
a mask. The drawer supplies the ink.

The index files use the same "## <number>" sections as the decoded text.
A token that is a decimal integer is a cell. A stored newline is a new line
in the file. The other controls are the bracket marks extract_text.py writes.
These files do not contain the character reading.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path


CONTROLS = {
    0xFFFE: "\n",
    0xFFFD: "\n[page]\n",
    0xFFFC: "[insert-1]",
    0xFFFB: "[insert-2]",
    0xFFFA: "[number]",
}


def vfs_member(vfs: bytes, wanted: str) -> bytes | None:
    directory = struct.unpack_from("<H", vfs, 5)[0]
    count = struct.unpack_from("<I", vfs, 7)[0]
    for index in range(count):
        entry = directory + index * 26
        name = vfs[entry : entry + 13].split(b"\x00", 1)[0].decode("latin1")
        if name.upper() != wanted:
            continue
        size = struct.unpack_from("<I", vfs, entry + 13)[0]
        offset = struct.unpack_from("<I", vfs, entry + 22)[0]
        return vfs[offset : offset + size]
    return None


def text_members(vfs: bytes) -> list[tuple[str, bytes]]:
    directory = struct.unpack_from("<H", vfs, 5)[0]
    count = struct.unpack_from("<I", vfs, 7)[0]
    found = []
    for index in range(count):
        entry = directory + index * 26
        name = vfs[entry : entry + 13].split(b"\x00", 1)[0].decode("latin1").upper()
        if not (name.startswith("FDETXT") and name.endswith(".TXT")):
            continue
        size = struct.unpack_from("<I", vfs, entry + 13)[0]
        offset = struct.unpack_from("<I", vfs, entry + 22)[0]
        found.append((name, vfs[offset : offset + size]))
    return sorted(found)


def strings_of(blob: bytes) -> list[tuple[int, ...]]:
    count = struct.unpack_from("<H", blob, 0)[0] // 2
    offsets = [struct.unpack_from("<H", blob, index * 2)[0] for index in range(count)]
    strings = []
    for index in range(count):
        start = offsets[index]
        end = offsets[index + 1] if index + 1 < count else len(blob)
        words = (end - start) // 2
        strings.append(struct.unpack_from("<" + "H" * words, blob, start))
    return strings


def cell_rows(cell: bytes) -> list[list[int]]:
    rows = []
    for row in range(16):
        pair = cell[row * 2 : row * 2 + 2]
        bits = (pair[0] << 8) | pair[1]
        rows.append([(bits >> shift) & 1 for shift in range(15, -1, -1)])
    return rows


def png(rows: list[list[int]]) -> bytes:
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for bit in row:
            raw += b"\xff\xff\xff\xff" if bit else b"\x00\x00\x00\x00"

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")


def indexes_of(words: tuple[int, ...]) -> str:
    lines: list[list[str]] = [[]]
    cursor = 0
    while cursor < len(words):
        word = words[cursor]
        if word == 0xFFFF:
            break
        if word == 0xFFFE:
            lines.append([])
            cursor += 1
            continue
        if word == 0xFFFD:
            lines.append(["[page]"])
            lines.append([])
            cursor += 1
            continue
        if word in (0xFFEF, 0xFFEE):
            argument = words[cursor + 1] if cursor + 1 < len(words) else 0
            kind = "portrait" if word == 0xFFEF else "slot"
            lines[-1].append(f"[{kind}:{argument}]")
            cursor += 2
            continue
        if word in CONTROLS:
            lines[-1].append(CONTROLS[word])
            cursor += 1
            continue
        lines[-1].append(str(word))
        cursor += 1
    return "\n".join(" ".join(line) for line in lines).strip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains FIELD.VFS")
    parser.add_argument("--out", type=Path, required=True, help="extract/text directory to write into")
    args = parser.parse_args()
    archive = args.data_dir / "FIELD.VFS"
    if not archive.is_file():
        print(f"missing {archive}", file=sys.stderr)
        return 1
    vfs = archive.read_bytes()
    font = vfs_member(vfs, "FDETXT.FON")
    if font is None or len(font) != 57344:
        print("FDETXT.FON is missing or not 57344 bytes", file=sys.stderr)
        return 1
    glyphs = args.out / "glyphs"
    indexed = args.out / "indexed"
    glyphs.mkdir(parents=True, exist_ok=True)
    indexed.mkdir(parents=True, exist_ok=True)
    for index in range(1792):
        (glyphs / f"cell_{index:04d}.png").write_bytes(png(cell_rows(font[index * 32 : index * 32 + 32])))
    print(f"glyphs: 1792")
    for name, blob in text_members(vfs):
        number = int(name[6:8])
        dest = indexed / ("interface.txt" if number == 0 else f"scenario-{number - 1:02d}.txt")
        body = [f"## {index}\n{indexes_of(words)}\n" for index, words in enumerate(strings_of(blob))]
        dest.write_text("\n".join(body), encoding="utf-8")
        print(f"{dest.name}: {len(body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
