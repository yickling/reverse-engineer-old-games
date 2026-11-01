#!/usr/bin/env python3
"""Extract FDPS map pictures and interface windows to PNG.

Uses the CEL layout in pictures.md. Mode 0 is the decoder in
extract_fight_sprites.py. Colors come from Fde.pal, except
StBoard.cel (StBoard.pal) and FigBar.cel (Fight.pal).

Folders:

  maps/icons/CHAR###   12 frames, sheet is 4 rows of 3 (facing, then step)
  maps/tiles/M###      one section's tiles. A gap uses the count at header +10.
                       A tail after that count is named in tiles.json and not drawn.
  maps/faces/          FACE.CEL, 125x100
  ui/                  every .cel in MISC.VFS

M310.CEL does not expand with mode 0, so it is recorded and skipped.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("extract_fight_sprites", HERE / "extract_fight_sprites.py")
fight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fight)

SHEET_MAX_WIDTH = 2048

# StBoard.cel is installed with StBoard.pal. FigBar.cel is opened by the
# fight players that install Fight.pal. Everything else in this batch is Fde.pal.
PALETTE_FOR = {
    "STBOARD.CEL": "STBOARD.PAL",
    "FIGBAR.CEL": "FIGHT.PAL",
}


def bitmap_size(blob: bytes) -> tuple[int, int]:
    if blob[:4] != b"CEL\x01":
        raise fight.ExtractError("not a CEL")
    if blob[6] != 0 or blob[8] not in (0, 1):
        raise fight.ExtractError(f"unexpected size bytes {blob[6]:02x} {blob[8]:02x}")
    return blob[7] + (256 if blob[8] else 0), blob[9]


def directory_offset(blob: bytes) -> int:
    return struct.unpack_from(">H", blob, 4)[0]


def read_dwords(blob: bytes, count: int) -> list[int] | None:
    start = directory_offset(blob)
    if count <= 0 or start + count * 4 > len(blob):
        return None
    offsets = [struct.unpack_from("<I", blob, start + index * 4)[0] for index in range(count)]
    if any(offsets[index] > offsets[index + 1] or offsets[index + 1] > len(blob) for index in range(count - 1)):
        return None
    return offsets


def packed_offsets(blob: bytes) -> list[int] | None:
    start = directory_offset(blob)
    if start + 4 > len(blob):
        return None
    first = struct.unpack_from("<I", blob, start)[0]
    if first < start + 4 or (first - start) % 4 or first > len(blob):
        return None
    return read_dwords(blob, (first - start) // 4)


def counted_offsets(blob: bytes) -> list[int] | None:
    count = struct.unpack_from(">H", blob, 10)[0]
    return read_dwords(blob, count + 1)


def can_decode(blob: bytes, offsets: list[int], width: int, height: int) -> bool:
    try:
        for start, end in zip(offsets, offsets[1:]):
            if start != end:
                fight.decode_cell(blob[start:end], width, height)
    except fight.ExtractError:
        return False
    return True


def choose_offsets(blob: bytes, width: int, height: int) -> tuple[list[int], str] | None:
    packed = packed_offsets(blob)
    if packed and len(packed) >= 2 and can_decode(blob, packed, width, height):
        return packed, "packed"
    counted = counted_offsets(blob)
    if counted and len(counted) >= 2 and can_decode(blob, counted, width, height):
        return counted, "count"
    return None


def write_sheet(
    folder: Path,
    frames: list[tuple[bytes, bytes] | None],
    width: int,
    height: int,
    palette: bytes,
    columns: int,
) -> dict:
    rows = (len(frames) + columns - 1) // columns
    sheet_w = columns * width
    sheet_h = rows * height
    indexes = bytearray(sheet_w * sheet_h)
    mask = bytearray(sheet_w * sheet_h)
    for index, frame in enumerate(frames):
        if frame is None:
            continue
        pixels, bits = frame
        column = index % columns
        row = index // columns
        dest_x = column * width
        dest_y = row * height
        for y in range(height):
            src = y * width
            dest = (dest_y + y) * sheet_w + dest_x
            for x in range(width):
                if bits[src + x]:
                    indexes[dest + x] = pixels[src + x]
                    mask[dest + x] = 1
    fight.write_png(folder / "sheet.png", sheet_w, sheet_h, bytes(indexes), bytes(mask), palette)
    return {"file": f"{folder.name}/sheet.png", "columns": columns, "rows": rows, "cell_width": width, "cell_height": height}


def extract_cel(folder: Path, name: str, blob: bytes, palette: bytes, columns: int | None) -> dict:
    width, height = bitmap_size(blob)
    chosen = choose_offsets(blob, width, height)
    record: dict = {"file": name, "width": width, "height": height}
    if chosen is None:
        record["skipped"] = "mode 0 did not consume the pictures"
        return record
    offsets, how = chosen
    record["directory"] = how
    tail = len(blob) - offsets[-1]
    if tail:
        record["tail_bytes"] = tail
    folder.mkdir(parents=True, exist_ok=True)
    frames: list[tuple[bytes, bytes] | None] = []
    written = 0
    for index, (start, end) in enumerate(zip(offsets, offsets[1:])):
        if start == end:
            frames.append(None)
            continue
        pixels, mask = fight.decode_cell(blob[start:end], width, height)
        fight.write_png(folder / f"frame_{index:03d}.png", width, height, pixels, mask, palette)
        frames.append((bytes(pixels), bytes(mask)))
        written += 1
    record["pictures"] = len(frames)
    record["written"] = written
    if frames and any(frame is not None for frame in frames):
        used = columns or max(1, min(len(frames), SHEET_MAX_WIDTH // max(width, 1)))
        record["sheet"] = write_sheet(folder, frames, width, height, palette, used)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains ICON.CEL, FACE.CEL, FIELD1.VFS, and MISC.VFS")
    parser.add_argument("--out", type=Path, required=True, help="directory to write; created if missing")
    parser.add_argument("--only", choices=("icons", "tiles", "faces", "ui"), action="append")
    args = parser.parse_args()
    for filename in ("ICON.CEL", "FACE.CEL", "FIELD1.VFS", "MISC.VFS"):
        if not (args.data_dir / filename).is_file():
            print(f"missing {filename} in {args.data_dir}", file=sys.stderr)
            return 1

    misc = fight.member_map(args.data_dir / "MISC.VFS")
    palettes = {name: fight.load_palette(misc, name) for name in ("FDE.PAL", "FIGHT.PAL", "STBOARD.PAL")}
    palette = palettes["FDE.PAL"]
    wanted = set(args.only) if args.only else {"icons", "tiles", "faces", "ui"}
    args.out.mkdir(parents=True, exist_ok=True)

    if "icons" in wanted:
        icon = (args.data_dir / "ICON.CEL").read_bytes()
        width, height = bitmap_size(icon)
        offsets, how = choose_offsets(icon, width, height)
        pictures = len(offsets) - 1
        if pictures % 12:
            raise fight.ExtractError(f"ICON.CEL has {pictures} pictures, not a multiple of 12")
        icon_records = []
        for character in range(pictures // 12):
            folder = args.out / "maps" / "icons" / f"CHAR{character:03d}"
            folder.mkdir(parents=True, exist_ok=True)
            frames = []
            base = character * 12
            for step in range(12):
                start = offsets[base + step]
                end = offsets[base + step + 1]
                pixels, mask = fight.decode_cell(icon[start:end], width, height)
                fight.write_png(folder / f"frame_{step:03d}.png", width, height, pixels, mask, palette)
                frames.append((bytes(pixels), bytes(mask)))
            sheet = write_sheet(folder, frames, width, height, palette, 3)
            icon_records.append({"character": character, "frames": 12, "directory": how, "sheet": sheet})
            print(f"maps/icons/CHAR{character:03d}  12 frames", flush=True)
        payload = {"palette": "Fde.pal", "cell": [width, height], "characters": icon_records}
        (args.out / "maps" / "icons").mkdir(parents=True, exist_ok=True)
        (args.out / "maps" / "icons" / "clips.json").write_text(json.dumps(payload) + "\n")
        print(f"wrote icons {pictures // 12} characters / {pictures} frames")

    if "tiles" in wanted:
        field = fight.member_map(args.data_dir / "FIELD1.VFS")
        tile_records = []
        for name in sorted(field):
            if not name.endswith(".CEL"):
                continue
            record = extract_cel(args.out / "maps" / "tiles" / Path(name).stem, name, field[name], palette, None)
            tile_records.append(record)
            if record.get("skipped"):
                print(f"maps/tiles/{Path(name).stem}  skipped", flush=True)
            else:
                tail = f"  tail {record['tail_bytes']}" if record.get("tail_bytes") else ""
                print(f"maps/tiles/{Path(name).stem}  {record['written']} tiles{tail}", flush=True)
        (args.out / "maps" / "tiles").mkdir(parents=True, exist_ok=True)
        (args.out / "maps" / "tiles" / "tiles.json").write_text(
            json.dumps({"palette": "Fde.pal", "sections": tile_records}, indent=2) + "\n"
        )
        written = sum(record.get("written", 0) for record in tile_records)
        skipped = sum(1 for record in tile_records if record.get("skipped"))
        print(f"wrote tiles {written} pictures, {skipped} sections skipped")

    if "faces" in wanted:
        record = extract_cel(args.out / "maps" / "faces", "FACE.CEL", (args.data_dir / "FACE.CEL").read_bytes(), palette, None)
        (args.out / "maps" / "faces.json").write_text(json.dumps({"palette": "Fde.pal", "clip": record}, indent=2) + "\n")
        print(f"maps/faces  {record.get('written', 0)} pictures")

    if "ui" in wanted:
        ui_records = []
        for name in sorted(misc):
            if not name.endswith(".CEL"):
                continue
            palette_name = PALETTE_FOR.get(name, "FDE.PAL")
            record = extract_cel(args.out / "ui" / Path(name).stem, name, misc[name], palettes[palette_name], None)
            record["palette"] = palette_name
            ui_records.append(record)
            print(f"ui/{Path(name).stem}  {record.get('written', 0)} pictures  {palette_name}", flush=True)
        (args.out / "ui").mkdir(parents=True, exist_ok=True)
        (args.out / "ui" / "ui.json").write_text(json.dumps({"files": ui_records}, indent=2) + "\n")
        print(f"wrote ui {sum(record.get('written', 0) for record in ui_records)} pictures")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except fight.ExtractError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
