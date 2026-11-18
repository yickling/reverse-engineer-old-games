#!/usr/bin/env python3
"""Expand an LZEXE 0.91 DOS executable to an MZ file.

The compressed file keeps the original IP, CS, SP, and SS in the first four
words of the decompressor, and the compressed size in paragraphs in the fifth.
The bitstream starts at
((header CS - that size + header paragraphs) << 4).

usage: unpack_lzexe.py INPUT OUTPUT
"""

import struct
import sys
from pathlib import Path


def _u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]


def _getbit(src, i, buf, count):
    b = buf & 1
    count -= 1
    if count == 0:
        buf = _u16(src, i)
        i += 2
        count = 16
    else:
        buf >>= 1
    return b, i, buf, count


def unpack(data):
    if data[:2] not in (b"MZ", b"ZM") or data[0x1C:0x20] != b"LZ91":
        raise SystemExit("not an LZEXE 0.91 executable")
    words = struct.unpack_from("<16H", data, 0)
    stub_at = (words[0x0B] + words[4]) << 4
    info = struct.unpack_from("<8H", data, stub_at)
    ip, cs, sp, ss, comp_paras = info[:5]
    stream = ((words[0x0B] - comp_paras + words[4]) << 4)
    src = data[stream:]
    i = 0
    buf = _u16(src, 0)
    i = 2
    count = 16
    out = bytearray()
    window = bytearray(0x4500)
    p = 0
    while True:
        if p > 0x4000:
            out += window[:0x2000]
            rest = p - 0x2000
            window[:rest] = window[0x2000:0x2000 + rest]
            p = rest
        bit, i, buf, count = _getbit(src, i, buf, count)
        if bit:
            window[p] = src[i]
            i += 1
            p += 1
            continue
        bit, i, buf, count = _getbit(src, i, buf, count)
        if not bit:
            hi, i, buf, count = _getbit(src, i, buf, count)
            lo, i, buf, count = _getbit(src, i, buf, count)
            length = ((hi << 1) | lo) + 2
            span = src[i] | 0xFF00
            i += 1
        else:
            lo = src[i]
            hi = src[i + 1]
            i += 2
            span = lo | ((hi & ~0x07) << 5) | 0xE000
            length = (hi & 0x07) + 2
            if length == 2:
                length = src[i]
                i += 1
                if length == 0:
                    break
                if length == 1:
                    continue
                length += 1
        if span >= 0x8000:
            span -= 0x10000
        for _ in range(length):
            window[p] = window[p + span]
            p += 1
    out += window[:p]
    rel = bytearray(data[stub_at + 0x158 :])
    ri = 0
    rel_off = 0
    rel_seg = 0
    fixups = []
    while True:
        span = rel[ri]
        ri += 1
        if span == 0:
            span = _u16(rel, ri)
            ri += 2
            if span == 0:
                rel_seg = (rel_seg + 0x0FFF) & 0xFFFF
                continue
            if span == 1:
                break
        rel_off += span
        rel_seg = (rel_seg + ((rel_off & ~0x0F) >> 4)) & 0xFFFF
        rel_off &= 0x0F
        fixups.append((rel_off, rel_seg))
    reloc_at = 0x1C
    rel_end = reloc_at + 4 * len(fixups)
    pad = (0x200 - rel_end) & 0x1FF
    header = rel_end + pad
    minalloc = words[5]
    if words[6] != 0:
        minalloc -= info[5] + ((info[6] + 16 - 1) >> 4) + 9
    blob = bytearray(header + len(out))
    def w(off, val):
        struct.pack_into("<H", blob, off, val & 0xFFFF)
    size = header + len(out)
    w(0, 0x5A4D)
    w(2, size & 0x1FF)
    w(4, (size + 0x1FF) >> 9)
    w(6, len(fixups))
    w(8, header // 16)
    w(0x0A, minalloc)
    w(0x0C, words[6])
    w(0x0E, ss)
    w(0x10, sp)
    w(0x14, ip)
    w(0x16, cs)
    w(0x18, reloc_at)
    for n, (off, seg) in enumerate(fixups):
        struct.pack_into("<HH", blob, reloc_at + 4 * n, off, seg)
    blob[header:] = out
    if cs * 16 + ip >= len(out):
        raise SystemExit("entry is outside the expanded image")
    return bytes(blob)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: unpack_lzexe.py INPUT OUTPUT")
    image = unpack(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(image)
    print(f"{len(image)} bytes")


if __name__ == "__main__":
    main()
