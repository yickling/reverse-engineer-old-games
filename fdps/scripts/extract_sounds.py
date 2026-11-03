#!/usr/bin/env python3
"""Extract FDPS sampled sounds to WAVE files.

Reads the VFS archives in a game directory. A .wav member is already a
RIFF WAVE file and is copied as stored, including BaseWav.vfs inside
MISC.VFS. A SAF sample is not a WAVE file. The record at
file + dword[sample_table + index * 4] is two flag bytes, a uint16 rate,
a uint32 length, and that many bytes at +8. The layout is the one in
formats.md and pictures.md.

01 08 selects type 0, 01 10 selects 1, 02 08 selects 2, and any other pair
selects 3. Type 0 and 1 are one channel. Type 2 and 3 are two channels.
Type 0 and 2 are 8-bit. Type 1 and 3 are 16-bit. The bytes are written as
a format-1 WAVE at the rate in the record. 8-bit samples are stored
unsigned, which is what a format-1 WAVE expects.

Folders:

  waves/     the named .wav members
  samples/   one folder per SAF member that has a sample count above 0,
             sample_000.wav and up, in sample-table order
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


class ExtractError(Exception):
    pass


def vfs_members(data: bytes, label: str) -> list[tuple[str, bytes]]:
    if data[:3] != b"VFS":
        raise ExtractError(f"{label} does not start with VFS")
    count = struct.unpack_from("<I", data, 7)[0]
    directory = struct.unpack_from("<H", data, 5)[0]
    members: list[tuple[str, bytes]] = []
    for index in range(count):
        entry = directory + index * 26
        if entry + 26 > len(data):
            raise ExtractError(f"{label} directory runs past the archive")
        name = data[entry : entry + 13].split(b"\x00", 1)[0].decode("latin1")
        size = struct.unpack_from("<I", data, entry + 13)[0]
        offset = struct.unpack_from("<I", data, entry + 22)[0]
        if offset + size > len(data):
            raise ExtractError(f"{label}:{name} runs past the archive")
        members.append((name, data[offset : offset + size]))
    return members


def sample_type(first: int, second: int) -> int:
    if first == 1 and second == 8:
        return 0
    if first == 1 and second == 0x10:
        return 1
    if first == 2 and second == 8:
        return 2
    return 3


def type_shape(kind: int) -> tuple[int, int]:
    channels = 2 if kind >= 2 else 1
    bits = 16 if kind & 1 else 8
    return channels, bits


def wav_pcm(rate: int, channels: int, bits: int, pcm: bytes) -> bytes:
    block = channels * (bits // 8)
    if block == 0 or len(pcm) % block != 0:
        raise ExtractError(f"sample length {len(pcm)} is not a whole {bits}-bit frame")
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(pcm),
        b"WAVE",
        b"fmt ",
        16,
        1,
        channels,
        rate,
        rate * block,
        block,
        bits,
        b"data",
        len(pcm),
    )
    return header + pcm


def describe_wave(blob: bytes, label: str) -> dict:
    if blob[:4] != b"RIFF" or blob[8:12] != b"WAVE":
        raise ExtractError(f"{label} is not a RIFF WAVE")
    cursor = 12
    fmt = None
    data_size = None
    while cursor + 8 <= len(blob):
        kind = blob[cursor : cursor + 4]
        size = struct.unpack_from("<I", blob, cursor + 4)[0]
        body = cursor + 8
        if body + size > len(blob):
            raise ExtractError(f"{label} chunk {kind!r} runs past the file")
        if kind == b"fmt " and size >= 16:
            audio_format, channels, rate, _byte_rate, _block, bits = struct.unpack_from("<HHIIHH", blob, body)
            fmt = {
                "format": audio_format,
                "channels": channels,
                "rate": rate,
                "bits": bits,
            }
        elif kind == b"data":
            data_size = size
        cursor = body + size + (size & 1)
    if fmt is None or data_size is None:
        raise ExtractError(f"{label} has no fmt or data chunk")
    fmt["data_bytes"] = data_size
    return fmt


def frame_users(blob: bytes) -> dict[int, list[int]]:
    frame_count = struct.unpack_from("<H", blob, 0x0C)[0]
    frame_table = struct.unpack_from("<I", blob, 0x0E)[0]
    users: dict[int, list[int]] = {}
    for index in range(frame_count):
        at = frame_table + index * 4
        if at + 4 > len(blob):
            raise ExtractError("frame table runs past the file")
        frame_at = struct.unpack_from("<I", blob, at)[0]
        if frame_at + 2 > len(blob):
            raise ExtractError("frame record runs past the file")
        sample = struct.unpack_from("<h", blob, frame_at)[0]
        if sample >= 0:
            users.setdefault(sample, []).append(index)
    return users


def saf_samples(blob: bytes, name: str) -> list[dict]:
    if len(blob) < 0x30 or blob[:3] != b"SAF" or blob[3] != 6:
        raise ExtractError(f"{name} is not SAF version 0x06")
    count = struct.unpack_from("<H", blob, 0x2A)[0]
    table = struct.unpack_from("<I", blob, 0x2C)[0]
    users = frame_users(blob)
    samples = []
    for index in range(count):
        slot = table + index * 4
        if slot + 4 > len(blob):
            raise ExtractError(f"{name} sample table runs past the file")
        at = struct.unpack_from("<I", blob, slot)[0]
        if at + 8 > len(blob):
            raise ExtractError(f"{name} sample {index} runs past the file")
        first = blob[at]
        second = blob[at + 1]
        rate = struct.unpack_from("<H", blob, at + 2)[0]
        length = struct.unpack_from("<I", blob, at + 4)[0]
        if at + 8 + length > len(blob):
            raise ExtractError(f"{name} sample {index} bytes run past the file")
        kind = sample_type(first, second)
        channels, bits = type_shape(kind)
        samples.append(
            {
                "index": index,
                "flags": [first, second],
                "type": kind,
                "channels": channels,
                "bits": bits,
                "rate": rate,
                "length": length,
                "pcm": blob[at + 8 : at + 8 + length],
                "frames": users.get(index, []),
            }
        )
    return samples


def collect(data_dir: Path) -> tuple[list[tuple[str, str, bytes]], list[tuple[str, str, bytes]]]:
    waves: list[tuple[str, str, bytes]] = []
    clips: list[tuple[str, str, bytes]] = []
    for path in sorted(data_dir.glob("*.VFS")):
        for name, blob in vfs_members(path.read_bytes(), path.name):
            items = [(path.name, name, blob)]
            if name.lower().endswith(".vfs") and blob[:3] == b"VFS":
                items = [
                    (f"{path.name}/{name}", nested_name, nested)
                    for nested_name, nested in vfs_members(blob, f"{path.name}/{name}")
                ]
            for archive, member, body in items:
                lower = member.lower()
                if lower.endswith(".wav"):
                    waves.append((archive, member, body))
                elif lower.endswith(".saf"):
                    clips.append((archive, member, body))
    return waves, clips


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="directory that contains the VFS archives")
    parser.add_argument("--out", type=Path, required=True, help="directory to write; created if missing")
    args = parser.parse_args()
    if not args.data_dir.is_dir():
        print(f"missing data directory {args.data_dir}", file=sys.stderr)
        return 1

    waves, clips = collect(args.data_dir)
    wave_dir = args.out / "waves"
    sample_root = args.out / "samples"
    wave_dir.mkdir(parents=True, exist_ok=True)
    sample_root.mkdir(parents=True, exist_ok=True)

    wave_records = []
    for archive, member, blob in waves:
        info = describe_wave(blob, f"{archive}:{member}")
        destination = wave_dir / member
        destination.write_bytes(blob)
        wave_records.append(
            {
                "archive": archive,
                "name": member,
                "file": f"waves/{member}",
                **info,
            }
        )
        print(f"waves/{member}  {info['rate']} Hz", flush=True)

    sample_records = []
    sample_count = 0
    for archive, member, blob in clips:
        samples = saf_samples(blob, f"{archive}:{member}")
        if not samples:
            continue
        stem = Path(member).stem
        folder = sample_root / stem
        folder.mkdir(parents=True, exist_ok=True)
        written = []
        for sample in samples:
            filename = f"sample_{sample['index']:03d}.wav"
            (folder / filename).write_bytes(
                wav_pcm(sample["rate"], sample["channels"], sample["bits"], sample["pcm"])
            )
            written.append(
                {
                    "index": sample["index"],
                    "file": f"samples/{stem}/{filename}",
                    "flags": sample["flags"],
                    "type": sample["type"],
                    "channels": sample["channels"],
                    "bits": sample["bits"],
                    "rate": sample["rate"],
                    "length": sample["length"],
                    "frames": sample["frames"],
                }
            )
            sample_count += 1
        sample_records.append(
            {
                "archive": archive,
                "name": member,
                "samples": written,
            }
        )
        print(f"samples/{stem}  {len(written)} samples", flush=True)

    payload = {"waves": wave_records, "clips": sample_records}
    (args.out / "sounds.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {len(wave_records)} waves, {len(sample_records)} clips, {sample_count} samples")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExtractError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
