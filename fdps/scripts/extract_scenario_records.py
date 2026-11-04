#!/usr/bin/env python3
"""Write one content pack per scenario index, and every icon script.

The field names are the packed structs in formats.md. A field those
structs mark unread is written under that name and nothing else is added
for it. Icon opcodes use the lengths in scenario.md. Opcode 0 ends a
script. Pictures, text, samples, music, and the stat tables are not written.

Index NN lands in extract/scenario/NN/. Section S of that index is
M + NN + S + .MPL and ATTR + NN + S + .DAT, under sections/S/. The detail
file is MNN.DTL. SHOPNN.DAT is shop.json for indexes 0 through 29. Index
30 is skipped. A member that is not in its archive is listed in
missing.json and the run continues. Every .dat member of ICONANI.VFS
lands in extract/icon/.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parent
SCENARIO = GAME / "extract" / "scenario"
ICON = GAME / "extract" / "icon"

# Opcode advances from scenario.md. A byte that is not in this set ends the script.
FIXED = {
    3: 2,
    4: 3,
    5: 3,
    6: 2,
    7: 2,
    8: 2,
    10: 5,
    11: 2,
    12: 2,
    13: 3,
    14: 2,
    15: 2,
    17: 2,
    18: 4,
    19: 3,
    20: 5,
    21: 4,
    97: 1,
    98: 3,
    99: 1,
}


class ExtractError(Exception):
    pass


def vfs_members(data: bytes, label: str) -> dict[str, bytes]:
    if data[:3] != b"VFS":
        raise ExtractError(f"{label} does not start with VFS")
    count = struct.unpack_from("<I", data, 7)[0]
    directory = struct.unpack_from("<H", data, 5)[0]
    members: dict[str, bytes] = {}
    for index in range(count):
        entry = directory + index * 26
        if entry + 26 > len(data):
            raise ExtractError(f"{label} directory runs past the archive")
        name = data[entry : entry + 13].split(b"\x00", 1)[0].decode("latin1")
        size = struct.unpack_from("<I", data, entry + 13)[0]
        offset = struct.unpack_from("<I", data, entry + 22)[0]
        if offset + size > len(data):
            raise ExtractError(f"{label}:{name} runs past the archive")
        members[name.upper()] = data[offset : offset + size]
    return members


def need(blob: bytes, end: int, label: str) -> None:
    if end > len(blob):
        raise ExtractError(f"{label} row ends at {end}, past {len(blob)}")


def u8(blob: bytes, offset: int) -> int:
    return blob[offset]


def u16(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<H", blob, offset)[0]


def i16(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<h", blob, offset)[0]


def u32(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<I", blob, offset)[0]


def i32(blob: bytes, offset: int) -> int:
    return struct.unpack_from("<i", blob, offset)[0]


def magic(blob: bytes) -> str:
    return blob[:3].decode("latin1")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def map_file(blob: bytes, label: str) -> dict:
    need(blob, 0x83, f"{label} header")
    actor_count = u8(blob, 2)
    if 0x83 + actor_count * 26 > len(blob):
        raise ExtractError(f"{label} count {actor_count} runs past {len(blob)}")
    record_count = (len(blob) - 0x83) // 26
    actors = []
    for index in range(record_count):
        at = 0x83 + index * 26
        actors.append(
            {
                "side": u8(blob, at),
                "character": u8(blob, at + 1),
                "at_2": u8(blob, at + 2),
                "at_3": u8(blob, at + 3),
                "scale": u8(blob, at + 4),
                "item0": u8(blob, at + 5),
                "item1": u8(blob, at + 6),
                "item": list(blob[at + 7 : at + 13]),
                "spell": list(blob[at + 0x0D : at + 0x11]),
                "phase": u8(blob, at + 0x11),
                "arg0": u8(blob, at + 0x12),
                "arg1": u8(blob, at + 0x13),
                "script": u8(blob, at + 0x14),
                "group": u8(blob, at + 0x15),
                "end": list(blob[at + 0x16 : at + 0x19]),
                "learned": u8(blob, at + 0x19),
            }
        )
    return {
        "zero": u8(blob, 0),
        "slots": u8(blob, 1),
        "actor_count": actor_count,
        "turn": [
            {"turn": u8(blob, 3 + i * 3), "handler": u8(blob, 4 + i * 3), "side": u8(blob, 5 + i * 3)}
            for i in range(16)
        ],
        "step": [
            {"handler": u8(blob, 0x33 + i * 2), "match": u8(blob, 0x34 + i * 2)} for i in range(16)
        ],
        "find": [
            {"kind": u8(blob, 0x53 + i * 3), "value": i16(blob, 0x54 + i * 3)} for i in range(16)
        ],
        "actor": actors,
    }


def cod_file(blob: bytes, label: str) -> dict:
    need(blob, 9, f"{label} header")
    if magic(blob) != "COD":
        raise ExtractError(f"{label} does not start with COD")
    count = u16(blob, 7)
    end = 9 + count * 6
    need(blob, end, label)
    records = []
    for index in range(count):
        at = 9 + index * 6
        records.append({"id": i16(blob, at), "x": i16(blob, at + 2), "y": i16(blob, at + 4)})
    return {
        "magic": "COD",
        "zero": u8(blob, 3),
        "flag": u8(blob, 4),
        "at_5": u8(blob, 5),
        "zero2": u8(blob, 6),
        "count": count,
        "record": records,
    }


def grid_file(blob: bytes, label: str) -> dict:
    need(blob, 11, f"{label} header")
    if magic(blob) != "MPL":
        raise ExtractError(f"{label} does not start with MPL")
    width = u16(blob, 7)
    height = u16(blob, 9)
    end = 11 + width * height * 2
    need(blob, end, label)
    cells = [i16(blob, 11 + index * 2) for index in range(width * height)]
    return {
        "magic": "MPL",
        "at_3": u8(blob, 3),
        "version": u8(blob, 4),
        "at_5": u16(blob, 5),
        "width": width,
        "height": height,
        "cell": cells,
    }


def attr_file(blob: bytes, label: str) -> dict:
    need(blob, 0x11, f"{label} header")
    if magic(blob) != "ATR":
        raise ExtractError(f"{label} does not start with ATR")
    count = (len(blob) - 0x11) // 4
    end = 0x11 + count * 4
    need(blob, end, label)
    records = []
    for index in range(count):
        at = 0x11 + index * 4
        records.append(
            {
                "anim": u8(blob, at),
                "tint": u8(blob, at + 1),
                "terrain": u8(blob, at + 2),
                "backdrop": u8(blob, at + 3),
            }
        )
    return {
        "magic": "ATR",
        "at_3": u8(blob, 3),
        "version": u8(blob, 4),
        "at_5": u16(blob, 5),
        "pad": list(blob[7:0x11]),
        "record": records,
    }


def dtl_file(blob: bytes, label: str) -> dict:
    need(blob, 0x10, f"{label} header")
    if magic(blob) != "DTL":
        raise ExtractError(f"{label} does not start with DTL")
    width = u16(blob, 7)
    height = u16(blob, 9)
    end = 0x10 + width * height
    need(blob, end, label)
    return {
        "magic": "DTL",
        "at_3": u8(blob, 3),
        "version": u8(blob, 4),
        "at_5": u16(blob, 5),
        "width": width,
        "height": height,
        "pad": list(blob[0x0B:0x10]),
        "tile": list(blob[0x10:end]),
    }


def dsc_file(blob: bytes, label: str) -> dict:
    need(blob, 4, f"{label} header")
    count = u32(blob, 0)
    end = 4 + count * 32
    need(blob, end, label)
    sections = []
    for index in range(count):
        at = 4 + index * 32
        sections.append(
            {
                "offset_x": i32(blob, at),
                "offset_y": i32(blob, at + 4),
                "scale_x": i32(blob, at + 8),
                "scale_y": i32(blob, at + 0x0C),
                "drift_x": i32(blob, at + 0x10),
                "drift_y": i32(blob, at + 0x14),
                "order": i32(blob, at + 0x18),
                "highlight": i32(blob, at + 0x1C),
            }
        )
    return {"count": count, "section": sections}


def instruction_length(blob: bytes, index: int, label: str) -> int:
    op = blob[index]
    if op == 1:
        need(blob, index + 4, f"{label} opcode 1")
        return 4 + 2 * blob[index + 3]
    if op == 2:
        need(blob, index + 3, f"{label} opcode 2")
        return 3 + 2 * blob[index + 2]
    if op == 9:
        need(blob, index + 2, f"{label} opcode 9")
        return 2 + blob[index + 1]
    if op == 16:
        need(blob, index + 3, f"{label} opcode 16")
        return 3 + 2 * blob[index + 2]
    if op in FIXED:
        return FIXED[op]
    return 1


def icon_file(blob: bytes, label: str) -> list[dict]:
    instructions = []
    index = 0
    while index < len(blob):
        op = blob[index]
        length = instruction_length(blob, index, label)
        need(blob, index + length, f"{label} opcode {op}")
        instructions.append({"opcode": op, "operands": list(blob[index + 1 : index + length])})
        index += length
        if op == 0 or op not in FIXED and op not in (1, 2, 9, 16):
            break
    if index != len(blob):
        raise ExtractError(f"{label} walk ended at {index} of {len(blob)}")
    if not instructions or instructions[-1]["opcode"] != 0:
        raise ExtractError(f"{label} does not end on opcode 0")
    return instructions


def shop_file(blob: bytes, label: str) -> dict:
    need(blob, 36, label)
    return {"group": [list(blob[index * 12 : (index + 1) * 12]) for index in range(3)]}


def take(archive: dict[str, bytes], name: str, missing: list[str]) -> bytes | None:
    blob = archive.get(name.upper())
    if blob is None:
        missing.append(name.upper())
        return None
    return blob


def write_section(
    folder: Path,
    section: int,
    nn: str,
    field1: dict[str, bytes],
    field2: dict[str, bytes],
    missing: list[str],
    root_copies: dict[str, object],
) -> None:
    grid_name = f"M{nn}{section}.MPL"
    attr_name = f"ATTR{nn}{section}.DAT"
    grid_blob = take(field1, grid_name, missing)
    attr_blob = take(field2, attr_name, missing)
    if grid_blob is None and attr_blob is None:
        return
    section_dir = folder / "sections" / str(section)
    if grid_blob is not None:
        payload = grid_file(grid_blob, grid_name)
        write_json(section_dir / "grid.json", payload)
        if section == 0:
            root_copies["grid.json"] = payload
    if attr_blob is not None:
        payload = attr_file(attr_blob, attr_name)
        write_json(section_dir / "attr.json", payload)
        if section == 0:
            root_copies["attr.json"] = payload


def write_scenario(
    index: int,
    field: dict[str, bytes],
    field1: dict[str, bytes],
    field2: dict[str, bytes],
    icons: dict[str, bytes],
) -> None:
    nn = f"{index:02d}"
    if index == 30:
        print("scenario/30 skipped")
        return
    folder = SCENARIO / nn
    missing: list[str] = []
    written: list[str] = []
    root_copies: dict[str, object] = {}

    def put(name: str, payload: object) -> None:
        write_json(folder / name, payload)
        written.append(name)

    pairs = (
        (field, f"MAP{nn}.DAT", "map.json", map_file),
        (field, f"MAP{nn}.COD", "cod.json", cod_file),
        (field1, f"M{nn}.DTL", "dtl.json", dtl_file),
    )
    for archive, member_name, filename, parse in pairs:
        blob = take(archive, member_name, missing)
        if blob is not None:
            put(filename, parse(blob, member_name))

    dsc_name = f"DSC{nn}.DAT"
    dsc_blob = take(field2, dsc_name, missing)
    if dsc_blob is not None:
        dsc = dsc_file(dsc_blob, dsc_name)
        put("dsc.json", dsc)
        section_numbers = range(dsc["count"])
    else:
        section_numbers = range(1)
    for section in section_numbers:
        write_section(folder, section, nn, field1, field2, missing, root_copies)

    if index <= 29:
        shop_name = f"SHOP{nn}.DAT"
        shop_blob = take(field, shop_name, missing)
        if shop_blob is not None:
            put("shop.json", shop_file(shop_blob, shop_name))
        icon_name = f"ICON{nn}.DAT"
        icon_blob = take(icons, icon_name, missing)
        if icon_blob is not None:
            put("icon.json", icon_file(icon_blob, icon_name))

    if index == 0:
        for name, payload in root_copies.items():
            put(name, payload)
    if missing:
        put("missing.json", missing)
    print(f"scenario/{nn}  {', '.join(written)}" + (f"  missing {', '.join(missing)}" if missing else ""))


def write_icons(icons: dict[str, bytes]) -> int:
    count = 0
    for name in sorted(icons):
        if not name.endswith(".DAT"):
            continue
        payload = icon_file(icons[name], name)
        write_json(ICON / f"{name[:-4].lower()}.json", payload)
        count += 1
        print(f"icon/{name[:-4].lower()}.json  {len(payload)} opcodes")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "data_dir",
        type=Path,
        help="directory that contains FIELD.VFS, FIELD1.VFS, FIELD2.VFS, and ICONANI.VFS",
    )
    args = parser.parse_args()
    needed = ("FIELD.VFS", "FIELD1.VFS", "FIELD2.VFS", "ICONANI.VFS")
    for filename in needed:
        if not (args.data_dir / filename).is_file():
            print(f"missing {filename} in {args.data_dir}", file=sys.stderr)
            return 1

    field = vfs_members((args.data_dir / "FIELD.VFS").read_bytes(), "FIELD.VFS")
    field1 = vfs_members((args.data_dir / "FIELD1.VFS").read_bytes(), "FIELD1.VFS")
    field2 = vfs_members((args.data_dir / "FIELD2.VFS").read_bytes(), "FIELD2.VFS")
    icons = vfs_members((args.data_dir / "ICONANI.VFS").read_bytes(), "ICONANI.VFS")

    for index in range(65):
        write_scenario(index, field, field1, field2, icons)
    written = write_icons(icons)
    print(f"wrote {written} icon scripts")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExtractError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
