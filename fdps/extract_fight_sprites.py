#!/usr/bin/env python3
"""Extract FDPS battle pictures to PNG.

Reads the VFS archives in a game directory and writes one cropped PNG per
frame, plus sheet.png for the clip. Frame order is the SAF frame table.
Each frame is shown for its hold count. The sheet cell is the union of the
frames' compose-buffer boxes, so a tighter crop stays where the fight drew
it. The layout is the one in pictures.md.

Folders:

  backdrops/   Back##     one frame, the terrain behind the fight
  stands/      Stand###   standing body, drawn for the defender and for the
                          attacker while they are not swinging
  attacks/     Act###     the swing. A counter uses the defender's Act file
  effects/     Magic###, the spell-phase clips (MB/ML/ME/MS, EB/EL/EE/ES,
                          EMG), and the other effect clips in MISC.VFS
                          (Cure, Curemp, Mag11, Magic0bb, Magic0gg, Poseff,
                          Posion)

Chunk byte 1 is expanded with mode 0. The fight repaints those chunks with
expander mode 9, which this script does not apply. Written pixels use
Fight.pal. Pixels the decoder skips stay transparent.

Title, chapter, and phase-banner clips (Logo, Chapter, Gameover, Bonus-1,
Enyphase, Plyphase) are not battle sprites and are left in the archive.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

COMPOSE_PITCH = 0x170
COMPOSE_WIDTH = 368
COMPOSE_HEIGHT = 248
SHEET_MAX_WIDTH = 2048

EFFECT_STEMS = (
    "MAGIC",
    "MB",
    "ML",
    "ME",
    "MS",
    "EB",
    "EL",
    "EE",
    "ES",
    "EMG",
    "CURE",
    "MAG",
    "POSEFF",
    "POSION",
)


class ExtractError(Exception):
    pass


def vfs_members(path: Path) -> list[tuple[str, bytes]]:
    data = path.read_bytes()
    if data[:3] != b"VFS":
        raise ExtractError(f"{path.name} does not start with VFS")
    count = struct.unpack_from("<I", data, 7)[0]
    directory = struct.unpack_from("<H", data, 5)[0]
    members: list[tuple[str, bytes]] = []
    for index in range(count):
        entry = directory + index * 26
        if entry + 26 > len(data):
            raise ExtractError(f"{path.name} directory runs past the archive")
        raw_name = data[entry : entry + 13]
        name = raw_name.split(b"\x00", 1)[0].decode("latin1")
        size = struct.unpack_from("<I", data, entry + 13)[0]
        offset = struct.unpack_from("<I", data, entry + 22)[0]
        if offset + size > len(data):
            raise ExtractError(f"{path.name}:{name} runs past the archive")
        members.append((name, data[offset : offset + size]))
    return members


def member_map(path: Path) -> dict[str, bytes]:
    return {name.upper(): blob for name, blob in vfs_members(path)}


def load_palette(misc: dict[str, bytes], name: str = "FIGHT.PAL") -> bytes:
    blob = misc.get(name.upper())
    if blob is None or len(blob) != 768:
        raise ExtractError(f"MISC.VFS has no 768-byte {name}")
    if max(blob) > 63:
        raise ExtractError(f"{name} components are outside 0..63")
    rgb = bytearray(256 * 3)
    for index, component in enumerate(blob):
        rgb[index] = component << 2
    return bytes(rgb)


def decode_cell(src: bytes, width: int, height: int) -> tuple[bytearray, bytearray]:
    """Mode 0 of the picture expander. n = (opcode & 0x3f) + 1."""
    pixels = bytearray(width * height)
    mask = bytearray(width * height)
    cursor = 0
    for y in range(height):
        x = 0
        while x < width:
            if cursor >= len(src):
                raise ExtractError(f"cell ended at row {y}, column {x}")
            opcode = src[cursor]
            cursor += 1
            count = (opcode & 0x3F) + 1
            kind = opcode >> 6
            if kind == 0:
                if cursor >= len(src):
                    raise ExtractError("cell ended on a repeat")
                value = src[cursor]
                cursor += 1
                for _ in range(count):
                    if x >= width:
                        raise ExtractError("repeat ran past the row")
                    pixels[y * width + x] = value
                    mask[y * width + x] = 1
                    x += 1
            elif kind == 1:
                if cursor >= len(src):
                    raise ExtractError("cell ended on a weave")
                value = src[cursor]
                cursor += 1
                for _ in range(count):
                    x += 1
                    if x >= width:
                        raise ExtractError("weave ran past the row")
                    pixels[y * width + x] = value
                    mask[y * width + x] = 1
                    x += 1
            elif kind == 2:
                if cursor + count > len(src):
                    raise ExtractError("cell ended on a copy")
                for _ in range(count):
                    if x >= width:
                        raise ExtractError("copy ran past the row")
                    pixels[y * width + x] = src[cursor]
                    mask[y * width + x] = 1
                    x += 1
                    cursor += 1
            else:
                x += count
                if x > width:
                    raise ExtractError("skip ran past the row")
    return pixels, mask


def cell_spans(blob: bytes, table: int, limit: int) -> tuple[list[int], dict[int, int]]:
    offsets = [struct.unpack_from("<I", blob, table + index * 4)[0] for index in range(limit)]
    order = sorted(range(limit), key=lambda index: offsets[index])
    ends: dict[int, int] = {}
    for earlier, later in zip(order, order[1:]):
        ends[earlier] = offsets[later]
    if order:
        ends[order[-1]] = len(blob)
    return offsets, ends


def read_picture(blob: bytes, picture_table: int, picture: int) -> tuple[int, int, tuple[int, ...]]:
    offset = struct.unpack_from("<I", blob, picture_table + picture * 4)[0]
    columns, rows = struct.unpack_from("<hh", blob, offset)
    if columns < 0 or rows < 0:
        raise ExtractError(f"picture {picture} has a negative grid")
    count = columns * rows
    indexes = struct.unpack_from("<" + "H" * count, blob, offset + 4) if count else ()
    return columns, rows, indexes


def parse_saf(blob: bytes, name: str) -> dict:
    if blob[:3] != b"SAF" or len(blob) < 0x30 or blob[3] != 6:
        raise ExtractError(f"{name} is not SAF version 0x06")
    cell_w, cell_h = struct.unpack_from("<HH", blob, 7)
    frame_count = struct.unpack_from("<H", blob, 0x0C)[0]
    frame_table = struct.unpack_from("<I", blob, 0x0E)[0]
    picture_limit = struct.unpack_from("<H", blob, 0x16)[0]
    picture_table = struct.unpack_from("<I", blob, 0x18)[0]
    cell_limit = struct.unpack_from("<H", blob, 0x20)[0]
    cell_table = struct.unpack_from("<I", blob, 0x22)[0]
    if min(cell_w, cell_h) <= 0:
        raise ExtractError(f"{name} has a zero cell size")
    frames = []
    for index in range(frame_count):
        frame_at = struct.unpack_from("<I", blob, frame_table + index * 4)[0]
        sample, hold = struct.unpack_from("<hh", blob, frame_at)
        preamble = blob[frame_at + 4]
        hit = blob[frame_at + 5]
        chunk_count = struct.unpack_from("<H", blob, frame_at + 8)[0]
        chunks = []
        cursor = frame_at + 10
        for _ in range(chunk_count):
            picture, x, y = struct.unpack_from("<Hhh", blob, cursor)
            mode = blob[cursor + 6]
            remap = struct.unpack_from("<h", blob, cursor + 7)[0]
            chunks.append(
                {
                    "picture": picture,
                    "x": x,
                    "y": y,
                    "mode": mode,
                    "remap": remap,
                }
            )
            cursor += 13
        frames.append(
            {
                "sample": sample,
                "hold": hold,
                "preamble": preamble,
                "hit": hit,
                "chunks": chunks,
            }
        )
    return {
        "cell_w": cell_w,
        "cell_h": cell_h,
        "picture_limit": picture_limit,
        "picture_table": picture_table,
        "cell_limit": cell_limit,
        "cell_table": cell_table,
        "frames": frames,
    }


def render_frame(
    blob: bytes, saf: dict, frame: dict
) -> tuple[bytes, bytes, int, int, int, int] | None:
    cell_w = saf["cell_w"]
    cell_h = saf["cell_h"]
    offsets, ends = saf["spans"]
    cache: dict[int, tuple[bytearray, bytearray]] = saf["cache"]

    def cell(index: int) -> tuple[bytearray, bytearray]:
        cached = cache.get(index)
        if cached is not None:
            return cached
        if index >= saf["cell_limit"]:
            raise ExtractError(f"cell {index} is past the table")
        decoded = decode_cell(blob[offsets[index] : ends[index]], cell_w, cell_h)
        cache[index] = decoded
        return decoded

    placed: list[tuple[int, int, int, int, tuple[int, ...]]] = []
    min_x = 1 << 30
    min_y = 1 << 30
    max_x = -(1 << 30)
    max_y = -(1 << 30)
    for chunk in frame["chunks"]:
        if chunk["picture"] >= saf["picture_limit"]:
            raise ExtractError(f"picture {chunk['picture']} is past the table")
        columns, rows, indexes = read_picture(blob, saf["picture_table"], chunk["picture"])
        if columns == 0 or rows == 0:
            continue
        width = columns * cell_w
        height = rows * cell_h
        x = chunk["x"]
        y = chunk["y"]
        placed.append((x, y, columns, rows, indexes))
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + width)
        max_y = max(max_y, y + height)
    if not placed:
        return None

    canvas_w = max_x - min_x
    canvas_h = max_y - min_y
    pixels = bytearray(canvas_w * canvas_h)
    mask = bytearray(canvas_w * canvas_h)
    for x, y, columns, rows, indexes in placed:
        for row in range(rows):
            for column in range(columns):
                cell_pixels, cell_mask = cell(indexes[row * columns + column])
                dest_x = x - min_x + column * cell_w
                dest_y = y - min_y + row * cell_h
                for cy in range(cell_h):
                    src = cy * cell_w
                    dest = (dest_y + cy) * canvas_w + dest_x
                    for cx in range(cell_w):
                        if cell_mask[src + cx]:
                            pixels[dest + cx] = cell_pixels[src + cx]
                            mask[dest + cx] = 1

    left, top, right, bottom = canvas_w, canvas_h, 0, 0
    for y in range(canvas_h):
        row = mask[y * canvas_w : (y + 1) * canvas_w]
        if 1 not in row:
            continue
        top = min(top, y)
        bottom = max(bottom, y + 1)
        xs = [index for index, bit in enumerate(row) if bit]
        left = min(left, xs[0])
        right = max(right, xs[-1] + 1)
    if right <= left or bottom <= top:
        return None

    cropped_w = right - left
    cropped_h = bottom - top
    cropped = bytearray(cropped_w * cropped_h)
    cropped_mask = bytearray(cropped_w * cropped_h)
    for y in range(cropped_h):
        src = (top + y) * canvas_w + left
        dest = y * cropped_w
        cropped[dest : dest + cropped_w] = pixels[src : src + cropped_w]
        cropped_mask[dest : dest + cropped_w] = mask[src : src + cropped_w]
    return bytes(cropped), bytes(cropped_mask), cropped_w, cropped_h, min_x + left, min_y + top


def write_png(path: Path, width: int, height: int, indexes: bytes, mask: bytes, palette: bytes) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row = y * width
        for x in range(width):
            if mask[row + x]:
                color = indexes[row + x] * 3
                raw.extend(palette[color : color + 3])
                raw.append(255)
            else:
                raw.extend(b"\x00\x00\x00\x00")

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def is_effect(name: str) -> bool:
    stem = Path(name).stem.upper()
    return any(stem.startswith(prefix) for prefix in EFFECT_STEMS)


def clips_to_extract(data_dir: Path) -> list[tuple[str, str, bytes]]:
    fight = member_map(data_dir / "FIGHT.VFS")
    act = member_map(data_dir / "FIGACT.VFS")
    back = member_map(data_dir / "BACKGRND.VFS")
    misc = member_map(data_dir / "MISC.VFS")
    chosen: list[tuple[str, str, bytes]] = []
    for name, blob in back.items():
        if name.startswith("BACK") and name.endswith(".SAF"):
            chosen.append(("backdrops", name, blob))
    for name, blob in fight.items():
        if name.startswith("STAND") and name.endswith(".SAF"):
            chosen.append(("stands", name, blob))
        elif name.startswith("MAGIC") and name.endswith(".SAF"):
            chosen.append(("effects", name, blob))
    for name, blob in act.items():
        if name.startswith("ACT") and name.endswith(".SAF"):
            chosen.append(("attacks", name, blob))
    for name, blob in misc.items():
        if name.endswith(".SAF") and is_effect(name):
            chosen.append(("effects", name, blob))
    chosen.sort(key=lambda item: (item[0], item[1]))
    return chosen


def clamp_sheet(frames: list[dict]) -> dict | None:
    """Stamp frames into one grid, each in its compose-buffer position."""
    placed = [frame for frame in frames if "pixels" in frame]
    if not placed:
        return None
    min_x = min(frame["x"] for frame in placed)
    min_y = min(frame["y"] for frame in placed)
    max_x = max(frame["x"] + frame["width"] for frame in placed)
    max_y = max(frame["y"] + frame["height"] for frame in placed)
    cell_w = max_x - min_x
    cell_h = max_y - min_y
    columns = max(1, min(len(frames), SHEET_MAX_WIDTH // cell_w if cell_w else 1))
    rows = (len(frames) + columns - 1) // columns
    sheet_w = columns * cell_w
    sheet_h = rows * cell_h
    indexes = bytearray(sheet_w * sheet_h)
    mask = bytearray(sheet_w * sheet_h)
    for index, frame in enumerate(frames):
        if "pixels" not in frame:
            continue
        column = index % columns
        row = index // columns
        dest_x = column * cell_w + frame["x"] - min_x
        dest_y = row * cell_h + frame["y"] - min_y
        source = frame["pixels"]
        source_mask = frame["mask"]
        for y in range(frame["height"]):
            src = y * frame["width"]
            dest = (dest_y + y) * sheet_w + dest_x
            for x in range(frame["width"]):
                if source_mask[src + x]:
                    indexes[dest + x] = source[src + x]
                    mask[dest + x] = 1
    return {
        "indexes": bytes(indexes),
        "mask": bytes(mask),
        "width": sheet_w,
        "height": sheet_h,
        "columns": columns,
        "rows": rows,
        "cell_width": cell_w,
        "cell_height": cell_h,
        "x": min_x,
        "y": min_y,
    }


def extract_clip(folder: Path, name: str, blob: bytes, palette: bytes) -> dict:
    saf = parse_saf(blob, name)
    saf["spans"] = cell_spans(blob, saf["cell_table"], saf["cell_limit"])
    saf["cache"] = {}
    stem = Path(name).stem
    clip_dir = folder / stem
    clip_dir.mkdir(parents=True, exist_ok=True)
    frames_out = []
    for index, frame in enumerate(saf["frames"]):
        rendered = render_frame(blob, saf, frame)
        record = {
            "index": index,
            "hold": frame["hold"],
            "hit": frame["hit"],
            "preamble": frame["preamble"],
            "sample": frame["sample"],
            "chunks": frame["chunks"],
        }
        if rendered is None:
            record["empty"] = True
        else:
            indexes, mask, width, height, origin_x, origin_y = rendered
            filename = f"frame_{index:03d}.png"
            write_png(clip_dir / filename, width, height, indexes, mask, palette)
            record["file"] = f"{stem}/{filename}"
            record["x"] = origin_x
            record["y"] = origin_y
            record["width"] = width
            record["height"] = height
            record["pixels"] = indexes
            record["mask"] = mask
        frames_out.append(record)
    sheet = clamp_sheet(frames_out)
    sheet_record = None
    if sheet is not None:
        write_png(clip_dir / "sheet.png", sheet["width"], sheet["height"], sheet["indexes"], sheet["mask"], palette)
        sheet_record = {
            "file": f"{stem}/sheet.png",
            "columns": sheet["columns"],
            "rows": sheet["rows"],
            "cell_width": sheet["cell_width"],
            "cell_height": sheet["cell_height"],
            "x": sheet["x"],
            "y": sheet["y"],
        }
    for record in frames_out:
        record.pop("pixels", None)
        record.pop("mask", None)
    clip = {
        "file": name,
        "cell": [saf["cell_w"], saf["cell_h"]],
        "frames": frames_out,
    }
    if sheet_record is not None:
        clip["sheet"] = sheet_record
    return clip


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains FIGHT.VFS, FIGACT.VFS, BACKGRND.VFS, and MISC.VFS")
    parser.add_argument("--out", type=Path, required=True, help="directory to write; created if missing")
    parser.add_argument(
        "--only",
        choices=("backdrops", "stands", "attacks", "effects"),
        action="append",
        help="extract one folder; repeat to extract several. Default is all four",
    )
    args = parser.parse_args()
    data_dir = args.data_dir
    for archive in ("FIGHT.VFS", "FIGACT.VFS", "BACKGRND.VFS", "MISC.VFS"):
        if not (data_dir / archive).is_file():
            print(f"missing {archive} in {data_dir}", file=sys.stderr)
            return 1

    palette = load_palette(member_map(data_dir / "MISC.VFS"))
    wanted = set(args.only) if args.only else {"backdrops", "stands", "attacks", "effects"}
    args.out.mkdir(parents=True, exist_ok=True)
    counts = {role: {"clips": 0, "frames": 0} for role in ("backdrops", "stands", "attacks", "effects")}
    by_role: dict[str, list[dict]] = {role: [] for role in counts}

    for role, name, blob in clips_to_extract(data_dir):
        if role not in wanted:
            continue
        record = extract_clip(args.out / role, name, blob, palette)
        by_role[role].append(record)
        counts[role]["clips"] += 1
        counts[role]["frames"] += len(record["frames"])
        print(f"{role}/{Path(name).stem}  {len(record['frames'])} frames", flush=True)

    for role, clips in by_role.items():
        if role not in wanted:
            continue
        payload = {
            "role": role,
            "palette": "Fight.pal",
            "compose": {"width": COMPOSE_WIDTH, "height": COMPOSE_HEIGHT, "pitch": COMPOSE_PITCH},
            "clips": clips,
        }
        (args.out / role).mkdir(parents=True, exist_ok=True)
        (args.out / role / "clips.json").write_text(json.dumps(payload, indent=2) + "\n")

    print(
        "wrote "
        + ", ".join(f"{role} {counts[role]['clips']} clips / {counts[role]['frames']} frames" for role in counts if role in wanted)
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExtractError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
