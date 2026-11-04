#!/usr/bin/env python3
"""Write the scenario-0 records and the stat tables as JSON.

The field names are the packed structs in formats.md, scenario.md, and
units.md. A field those structs mark unread is written under that name
and nothing else is added for it. SHOP00.DAT, pictures, text, samples,
and music are not written.

Scenario 0 lands in extract/scenario/00/. The nine MISC.VFS tables land
in extract/tables/, one JSON array per file.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAME = HERE.parent
SCENARIO = GAME / "extract" / "scenario" / "00"
TABLES = GAME / "extract" / "tables"

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


def rows(blob: bytes, count: int, stride: int, label: str) -> list[bytes]:
    out = []
    for index in range(count):
        start = index * stride
        end = start + stride
        need(blob, end, f"{label} row {index}")
        out.append(blob[start:end])
    return out


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def map_file(blob: bytes) -> dict:
    need(blob, 0x83, "MAP00.DAT header")
    actor_count = u8(blob, 2)
    end = 0x83 + actor_count * 26
    need(blob, end, "MAP00.DAT")
    if end != len(blob):
        raise ExtractError(f"MAP00.DAT is {len(blob)} bytes, header count {actor_count} covers {end}")
    actors = []
    for index in range(actor_count):
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


def cod_file(blob: bytes) -> dict:
    need(blob, 9, "MAP00.COD header")
    if magic(blob) != "COD":
        raise ExtractError("MAP00.COD does not start with COD")
    count = u16(blob, 7)
    end = 9 + count * 6
    need(blob, end, "MAP00.COD")
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


def grid_file(blob: bytes) -> dict:
    need(blob, 11, "M000.MPL header")
    if magic(blob) != "MPL":
        raise ExtractError("M000.MPL does not start with MPL")
    width = u16(blob, 7)
    height = u16(blob, 9)
    end = 11 + width * height * 2
    need(blob, end, "M000.MPL")
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


def attr_file(blob: bytes) -> dict:
    need(blob, 0x11, "ATTR000.DAT header")
    if magic(blob) != "ATR":
        raise ExtractError("ATTR000.DAT does not start with ATR")
    count = (len(blob) - 0x11) // 4
    end = 0x11 + count * 4
    need(blob, end, "ATTR000.DAT")
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


def dtl_file(blob: bytes) -> dict:
    need(blob, 0x10, "M00.DTL header")
    if magic(blob) != "DTL":
        raise ExtractError("M00.DTL does not start with DTL")
    width = u16(blob, 7)
    height = u16(blob, 9)
    end = 0x10 + width * height
    need(blob, end, "M00.DTL")
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


def dsc_file(blob: bytes) -> dict:
    need(blob, 4, "DSC00.DAT header")
    count = u32(blob, 0)
    end = 4 + count * 32
    need(blob, end, "DSC00.DAT")
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


def instruction_length(blob: bytes, index: int) -> int:
    op = blob[index]
    if op == 1:
        need(blob, index + 4, "ICON00.DAT opcode 1")
        return 4 + 2 * blob[index + 3]
    if op == 2:
        need(blob, index + 3, "ICON00.DAT opcode 2")
        return 3 + 2 * blob[index + 2]
    if op == 9:
        need(blob, index + 2, "ICON00.DAT opcode 9")
        return 2 + blob[index + 1]
    if op == 16:
        need(blob, index + 3, "ICON00.DAT opcode 16")
        return 3 + 2 * blob[index + 2]
    if op in FIXED:
        return FIXED[op]
    return 1


def icon_file(blob: bytes) -> list[dict]:
    instructions = []
    index = 0
    while index < len(blob):
        op = blob[index]
        length = instruction_length(blob, index)
        need(blob, index + length, f"ICON00.DAT opcode {op}")
        instructions.append({"opcode": op, "operands": list(blob[index + 1 : index + length])})
        index += length
        if op == 0 or op not in FIXED and op not in (1, 2, 9, 16):
            break
    if index != len(blob):
        raise ExtractError(f"ICON00.DAT walk ended at {index} of {len(blob)}")
    if not instructions or instructions[-1]["opcode"] != 0:
        raise ExtractError("ICON00.DAT does not end on opcode 0")
    return instructions


def item_row(row: bytes) -> dict:
    return {
        "type": row[0],
        "attack": struct.unpack_from("<H", row, 1)[0],
        "hit": struct.unpack_from("<H", row, 3)[0],
        "defense": struct.unpack_from("<H", row, 5)[0],
        "avoid": struct.unpack_from("<H", row, 7)[0],
        "swing": row[9],
        "at_0x0a": row[0x0A],
        "inner": row[0x0B],
        "shape": row[0x0C],
        "kind": row[0x0D],
        "amount": struct.unpack_from("<H", row, 0x0E)[0],
        "range": row[0x10],
        "cpu_side": row[0x11],
        "use_shape": row[0x12],
        "price": struct.unpack_from("<H", row, 0x13)[0],
        "menu_side": row[0x15],
        "at_0x16": row[0x16],
    }


def friaprda_row(row: bytes) -> dict:
    return {
        "kind": row[0],
        "class_id": row[1],
        "scale": row[2],
        "hp": struct.unpack_from("<H", row, 3)[0],
        "mp": struct.unpack_from("<H", row, 5)[0],
        "move": row[7],
        "spells": list(row[8:12]),
        "items": list(row[0x0C:0x12]),
        "attack": struct.unpack_from("<H", row, 0x12)[0],
        "defense": struct.unpack_from("<H", row, 0x14)[0],
        "hit": struct.unpack_from("<H", row, 0x16)[0],
    }


def frilevup_row(row: bytes) -> dict:
    # Five pairs. Spawn reads the first byte of each. Byte 10 selects the GetMgTab row.
    names = ("attack", "defense", "hit", "hp", "mp")
    record = {name: [row[index * 2], row[index * 2 + 1]] for index, name in enumerate(names)}
    record["spell_row"] = row[10]
    return record


def enemydat_row(row: bytes) -> dict:
    return {
        "kind": row[0],
        "class_id": row[1],
        "hp": struct.unpack_from("<H", row, 2)[0],
        "mp": row[4],
        "attack": row[5],
        "defense": row[6],
        "hit": row[7],
        "move": row[8],
        "experience": row[9],
    }


def promap_row(row: bytes) -> dict:
    return {"move_cost": list(row[:8]), "crit": row[8], "spell_scale": row[9]}


def proequ_row(row: bytes) -> dict:
    return {"type": list(row)}


def magicdat_row(row: bytes) -> dict:
    return {
        "power": struct.unpack_from("<h", row, 0)[0],
        "chance": row[2],
        "budget": row[3],
        "shape": row[4],
        "cost": row[5],
        "side": row[6],
    }


def getmgtab_row(row: bytes) -> dict:
    return {
        "pair": [{"level": row[index], "learned": row[index + 1]} for index in range(0, 12, 2)]
    }


def rankup_row(row: bytes) -> dict:
    return {
        "choice": [
            {"character_id": row[index], "class_id": row[index + 1], "third": row[index + 2]}
            for index in range(0, 12, 3)
        ]
    }


TABLE_SPECS = (
    ("FRIAPRDA.DAT", "friaprda.json", 60, 0x18, friaprda_row),
    ("FRILEVUP.DAT", "frilevup.json", 60, 0x0B, frilevup_row),
    ("ENEMYDAT.DAT", "enemydat.json", 91, 0x0A, enemydat_row),
    ("ITEM.DAT", "item.json", 251, 0x17, item_row),
    ("PROMAP.DAT", "promap.json", 41, 0x0A, promap_row),
    ("PROEQU.DAT", "proequ.json", 36, 6, proequ_row),
    ("MAGICDAT.DAT", "magicdat.json", 40, 7, magicdat_row),
    ("GETMGTAB.DAT", "getmgtab.json", 60, 0x0C, getmgtab_row),
    ("RANKUP.DAT", "rankup.json", 9, 0x0C, rankup_row),
)


def member(archive: dict[str, bytes], name: str, label: str) -> bytes:
    try:
        return archive[name.upper()]
    except KeyError as error:
        raise ExtractError(f"{label} has no {name}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "data_dir",
        type=Path,
        help="directory that contains FIELD.VFS, FIELD1.VFS, FIELD2.VFS, MISC.VFS, and ICONANI.VFS",
    )
    args = parser.parse_args()
    needed = ("FIELD.VFS", "FIELD1.VFS", "FIELD2.VFS", "MISC.VFS", "ICONANI.VFS")
    for filename in needed:
        if not (args.data_dir / filename).is_file():
            print(f"missing {filename} in {args.data_dir}", file=sys.stderr)
            return 1

    field = vfs_members((args.data_dir / "FIELD.VFS").read_bytes(), "FIELD.VFS")
    field1 = vfs_members((args.data_dir / "FIELD1.VFS").read_bytes(), "FIELD1.VFS")
    field2 = vfs_members((args.data_dir / "FIELD2.VFS").read_bytes(), "FIELD2.VFS")
    misc = vfs_members((args.data_dir / "MISC.VFS").read_bytes(), "MISC.VFS")
    icons = vfs_members((args.data_dir / "ICONANI.VFS").read_bytes(), "ICONANI.VFS")

    scenario = {
        "map.json": map_file(member(field, "MAP00.DAT", "FIELD.VFS")),
        "cod.json": cod_file(member(field, "MAP00.COD", "FIELD.VFS")),
        "grid.json": grid_file(member(field1, "M000.MPL", "FIELD1.VFS")),
        "attr.json": attr_file(member(field2, "ATTR000.DAT", "FIELD2.VFS")),
        "dtl.json": dtl_file(member(field1, "M00.DTL", "FIELD1.VFS")),
        "dsc.json": dsc_file(member(field2, "DSC00.DAT", "FIELD2.VFS")),
        "icon.json": icon_file(member(icons, "ICON00.DAT", "ICONANI.VFS")),
    }
    for name, payload in scenario.items():
        write_json(SCENARIO / name, payload)

    for member_name, filename, count, stride, parse in TABLE_SPECS:
        blob = member(misc, member_name, "MISC.VFS")
        parsed = [parse(row) for row in rows(blob, count, stride, member_name)]
        write_json(TABLES / filename, parsed)
        print(f"tables/{filename}  {count} rows of {stride}")

    grid = scenario["grid.json"]
    actors = scenario["map.json"]["actor"]
    print(
        f"scenario/00  grid {grid['width']}x{grid['height']}  "
        f"actors {len(actors)}  icon {len(scenario['icon.json'])}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExtractError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
