#!/usr/bin/env python3
"""Extract the cinematic SAF clips to PNG frames.

No AVI, Smacker, FLI, or MPEG member is in the archives. The clips the
game plays as a movie are SAF version 0x06. This writes those, one PNG
per frame, on a canvas shared by the whole clip so a later frame stays
where the earlier one drew it. A chunk whose mode byte is 1 is expanded
with mode 0, the same way the fight frames are. The layout is the one
in pictures.md.

LOGO.SAF is colored from DYNASTY.PAL. CHAPTER.SAF is colored from
CHAPTER.PAL. The other clips are colored from FDE.PAL.

Folders:

  title/     Logo, Chapter, Gameover, Bonus-1, Enyphase, Plyphase
  icon/      Icon#### from ICONANI.VFS, the clips icon opcode 6 plays
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_fight_sprites as frames  # noqa: E402

TITLE = (
    "LOGO.SAF",
    "CHAPTER.SAF",
    "GAMEOVER.SAF",
    "BONUS-1.SAF",
    "ENYPHASE.SAF",
    "PLYPHASE.SAF",
)

PALETTE_FOR = {
    "LOGO.SAF": "DYNASTY.PAL",
    "CHAPTER.SAF": "CHAPTER.PAL",
}


def clip_box(blob: bytes, saf: dict) -> tuple[int, int, int, int] | None:
    min_x = 1 << 30
    min_y = 1 << 30
    max_x = -(1 << 30)
    max_y = -(1 << 30)
    cell_w = saf["cell_w"]
    cell_h = saf["cell_h"]
    for frame in saf["frames"]:
        for chunk in frame["chunks"]:
            columns, rows, _indexes = frames.read_picture(
                blob, saf["picture_table"], chunk["picture"]
            )
            if columns <= 0 or rows <= 0:
                continue
            min_x = min(min_x, chunk["x"])
            min_y = min(min_y, chunk["y"])
            max_x = max(max_x, chunk["x"] + columns * cell_w)
            max_y = max(max_y, chunk["y"] + rows * cell_h)
    if max_x <= min_x or max_y <= min_y:
        return None
    return min_x, min_y, max_x - min_x, max_y - min_y


def paint(blob: bytes, saf: dict, frame: dict, box: tuple[int, int, int, int]) -> tuple[bytes, bytes]:
    min_x, min_y, width, height = box
    cell_w = saf["cell_w"]
    cell_h = saf["cell_h"]
    offsets, ends = saf["spans"]
    cache: dict[int, tuple[bytearray, bytearray]] = saf["cache"]
    pixels = bytearray(width * height)
    mask = bytearray(width * height)

    def cell(index: int) -> tuple[bytearray, bytearray]:
        cached = cache.get(index)
        if cached is not None:
            return cached
        decoded = frames.decode_cell(blob[offsets[index] : ends[index]], cell_w, cell_h)
        cache[index] = decoded
        return decoded

    for chunk in frame["chunks"]:
        columns, rows, indexes = frames.read_picture(blob, saf["picture_table"], chunk["picture"])
        if columns <= 0 or rows <= 0:
            continue
        for row in range(rows):
            for column in range(columns):
                cell_pixels, cell_mask = cell(indexes[row * columns + column])
                dest_x = chunk["x"] - min_x + column * cell_w
                dest_y = chunk["y"] - min_y + row * cell_h
                for cy in range(cell_h):
                    src = cy * cell_w
                    dest = (dest_y + cy) * width + dest_x
                    for cx in range(cell_w):
                        if cell_mask[src + cx]:
                            pixels[dest + cx] = cell_pixels[src + cx]
                            mask[dest + cx] = 1
    return bytes(pixels), bytes(mask)


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


def extract_one(folder: Path, name: str, blob: bytes, palette_name: str, palette: bytes) -> dict:
    saf = frames.parse_saf(blob, name)
    saf["spans"] = frames.cell_spans(blob, saf["cell_table"], saf["cell_limit"])
    saf["cache"] = {}
    box = clip_box(blob, saf)
    stem = Path(name).stem.lower()
    clip_dir = folder / stem
    clip_dir.mkdir(parents=True, exist_ok=True)
    record_frames = []
    if box is None:
        for index, frame in enumerate(saf["frames"]):
            record_frames.append({"index": index, "hold": frame["hold"], "empty": True})
        return {
            "file": name,
            "palette": palette_name,
            "frames": record_frames,
        }
    origin_x, origin_y, width, height = box
    for index, frame in enumerate(saf["frames"]):
        indexes, mask = paint(blob, saf, frame, box)
        filename = f"frame_{index:03d}.png"
        write_png(clip_dir / filename, width, height, indexes, mask, palette)
        record_frames.append(
            {
                "index": index,
                "hold": frame["hold"],
                "file": f"{stem}/{filename}",
            }
        )
    return {
        "file": name,
        "palette": palette_name,
        "x": origin_x,
        "y": origin_y,
        "width": width,
        "height": height,
        "frames": record_frames,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains MISC.VFS and ICONANI.VFS")
    parser.add_argument("--out", type=Path, required=True, help="directory to write; created if missing")
    args = parser.parse_args()
    misc = frames.member_map(args.data_dir / "MISC.VFS")
    icon = frames.member_map(args.data_dir / "ICONANI.VFS")
    args.out.mkdir(parents=True, exist_ok=True)
    clips = []
    for name in TITLE:
        blob = misc.get(name)
        if blob is None:
            raise frames.ExtractError(f"MISC.VFS has no {name}")
        palette_name = PALETTE_FOR.get(name, "FDE.PAL")
        palette = frames.load_palette(misc, palette_name)
        print(name, flush=True)
        clips.append(extract_one(args.out / "title", name, blob, palette_name, palette))
    palette = frames.load_palette(misc, "FDE.PAL")
    for name in sorted(n for n in icon if n.startswith("ICON") and n.endswith(".SAF")):
        print(name, flush=True)
        clips.append(extract_one(args.out / "icon", name, icon[name], "FDE.PAL", palette))
    summary = {
        "clips": [
            {
                "file": clip["file"],
                "palette": clip["palette"],
                "width": clip.get("width"),
                "height": clip.get("height"),
                "frames": len(clip["frames"]),
            }
            for clip in clips
        ]
    }
    (args.out / "videos.json").write_text(json.dumps({"clips": clips}, indent=2) + "\n")
    (args.out / "index.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {len(clips)} clips")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except frames.ExtractError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
