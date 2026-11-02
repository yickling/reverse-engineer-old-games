#!/usr/bin/env python3
"""Read the FDETXT members out as text.

Each string is a run of glyph indexes, as in text.md. The glyph map pairs
an index with the character read from that cell of FDETXT.FON. Cells 0-9
are the digits and cells 10-35 are A-Z. The other cells are the reading in
docs/fdps/text/glyph-map.tsv. A cell that looks like two similar characters
can be off by one stroke.

Scenario index N is the member FDETXT(N+1).TXT. FDETXT00.TXT is the
interface block, not scenario 0. Members past FDETXT30.TXT use the same
layout for indexes past 29.

Controls, from FUN_0001ff30:

    0xfffe  new line
    0xfffd  page
    0xfffc  insert the interface string held in DAT_00064030
    0xfffb  insert the interface string held in DAT_00064034
    0xfffa  the number held in DAT_00064038
    0xffef  portrait, and the next word is the lookup argument
    0xffee  portrait, and the next word is a unit slot
    0xffff  end
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_MAP = ROOT / "docs" / "fdps" / "text" / "glyph-map.tsv"
DEFAULT_OUT = ROOT / "docs" / "fdps" / "text"

CONTROLS = {
    0xFFFE: "\n",
    0xFFFD: "\n[page]\n",
    0xFFFC: "[insert-1]",
    0xFFFB: "[insert-2]",
    0xFFFA: "[number]",
}


def members(vfs: bytes) -> list[tuple[str, bytes]]:
    directory = struct.unpack_from("<H", vfs, 5)[0]
    count = struct.unpack_from("<I", vfs, 7)[0]
    found = []
    for index in range(count):
        entry = directory + index * 26
        name = vfs[entry : entry + 13].split(b"\x00", 1)[0].decode("latin1")
        upper = name.upper()
        if not (upper.startswith("FDETXT") and upper.endswith(".TXT")):
            continue
        size = struct.unpack_from("<I", vfs, entry + 13)[0]
        offset = struct.unpack_from("<I", vfs, entry + 22)[0]
        found.append((upper, vfs[offset : offset + size]))
    return sorted(found)


def load_map(path: Path) -> dict[int, str]:
    table = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        index, character = line.split("\t", 1)
        table[int(index)] = character
    return table


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


def render(words: tuple[int, ...], table: dict[int, str]) -> str:
    parts = []
    cursor = 0
    while cursor < len(words):
        word = words[cursor]
        if word == 0xFFFF:
            break
        if word in (0xFFEF, 0xFFEE):
            argument = words[cursor + 1] if cursor + 1 < len(words) else 0
            kind = "portrait" if word == 0xFFEF else "slot"
            parts.append(f"[{kind}:{argument}]")
            cursor += 2
            continue
        if word in CONTROLS:
            parts.append(CONTROLS[word])
            cursor += 1
            continue
        parts.append(table.get(word, f"[{word:04x}]"))
        cursor += 1
    return "".join(parts).strip("\n")


def write_member(name: str, blob: bytes, table: dict[int, str], out: Path) -> tuple[str, int]:
    number = int(name[6:8])
    if number == 0:
        label = "interface"
        dest = out / "interface.txt"
    else:
        label = f"scenario {number - 1}"
        dest = out / f"scenario-{number - 1:02d}.txt"
    body = [
        f"# {label}  ({name})  {len(strings_of(blob))} strings",
        "# Read from the font bitmaps. A similar-looking character may be off by one stroke.",
        "",
    ]
    for index, words in enumerate(strings_of(blob)):
        body.append(f"## {index}")
        body.append(render(words, table))
        body.append("")
    dest.write_text("\n".join(body), encoding="utf-8")
    return label, len(strings_of(blob))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains FIELD.VFS")
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    archive = args.data_dir / "FIELD.VFS"
    if not archive.is_file():
        print(f"missing {archive}", file=sys.stderr)
        return 1
    if not args.map.is_file():
        print(f"missing {args.map}", file=sys.stderr)
        return 1
    table = load_map(args.map)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, blob in members(archive.read_bytes()):
        label, count = write_member(name, blob, table, args.out)
        print(f"{label}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
