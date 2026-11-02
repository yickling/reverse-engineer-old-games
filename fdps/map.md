# Map, camera, and terrain

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

The picture is mode 13h, 320×200. A map frame is composed by `FUN_0002bcf0` into a buffer of `0x15180` bytes at pitch `0x168` (360). `FUN_0002c0c0` paints one section as 14 columns by 9 rows of 24×24 tiles, which is the 320×200 window with a partial tile at the right and bottom edges. The camera origin is in pixels. `DAT_00069ce4` is the horizontal origin and `DAT_00069ce0` the vertical one. The same two axes for the cursor are `DAT_00069cd4` and `DAT_00069ccc`.

`FUN_0002c0c0` divides the camera by 24 and keeps the remainder, so the window can sit between tile boundaries. For each of the 9×14 cells it wraps the tile coordinate across the section width and height (the shorts at MPL `+7` and `+9`). The MPL cell is the little-endian short at `file + 0x0b + (y * width + x) * 2`. That short is the tile-picture index. Where those files come from is in [Scenario files](scenario.md).

Tile pixels come from the section CEL. Its header matches `ICON.CEL`: `CEL`, version `1`, then three big-endian shorts. Those shorts are the directory offset, the width, and the height. On `M000.CEL` they are `0x0f`, 24, and 24. The directory is little-endian dwords. When the file is packed, the first dword is the file offset where the pictures begin, so the number of directory entries is `(first_offset - directory_offset) / 4`, and the last entry is the end of the last picture rather than a picture of its own. The picture list is the run of little-endian dwords at the directory that stay increasing, inside the file, and past the end of the table itself. Mode 0 at 24×24 consumes every span of that run for 68 of the 69 section files, through the end of the file. The uint16 at header `+10` is only a prefix of that run: on `M190`, `M290`, and `M620` it counts 28, 129, and 120 pictures, and the run continues for 284, 385, and 376. Those three counts are the `ATTR` record counts. `M310` has the same shape of run, 192 pictures, and mode 0 does not expand any of them. The `MPL` for that section names tiles 0 through 172. `FUN_0005664b` expands the picture selected by `dword[directory + index * 4]`. Mode 0 of that expander, and the byte that widens a window CEL, are in [Pictures](pictures.md).

Drawing one cell, from `FUN_0002c0c0`:

```
tile = mpl_short(x, y)
if layer_mode == 0:
    blit picture[tile] with expander mode 0
else:
    attr = byte[attr_file + 0x11 + tile * 4]
    kind = attr & 7
    if kind == 1: tile = tile + blink          # blink is 0 or 1, flipped every 4 ticks
    if kind == 2: tile = tile + ((tick >> 2) & 3) * 0x60
    if attr & 0x80:
        blit picture[tile], expander mode 9, using attr byte +1
    else if occupancy_byte(x, y) == 0xff:
        blit picture[tile], mode 0
    else:
        blit picture[tile], mode 9 or 10       # 10 when layer_mode == 1, else 9
```

`tick` is `DAT_00069d64`. `blink` is `DAT_00060160`. Across the `ATTR` files, the low 3 bits are only ever 0 or 2, so the two-frame blink is unused on disk and the four-step `* 0x60` animation is the one that occurs. Mode 0 is the plain expander. Modes 9 and 10 are `FUN_0005738b` and `FUN_00057503`. The blend is in [Pictures](pictures.md). They are what paints a tile that a unit is standing on, or a tile whose attribute has bit `0x80`.

`FUN_0002bcf0` draws every section whose byte `DAT_00069cfe[i]` is below 10, then the units (`FUN_0002cfd0`), then sections above 10. A section can therefore paint over the units. The visible copy out of the map buffer is 320×200 from buffer+`0x21d8` in the phase transition, and the combat copy is buffer+`0x2298` at pitch `0x170`.

`FUN_0002b790(x, y)` is the tile query. It reads the MPL short into `DAT_00069d04`, then the 4-byte `ATR` record for that picture:

| Record byte | Stored at | Use |
| --- | --- | --- |
| 0 | `DAT_00069d08` | The animation byte the drawer reads. |
| 1 | `DAT_00069d0a` | Passed to the expander when bit `0x80` of byte 0 is set. |
| 2 | `DAT_00069d09` | Terrain kind. Movement cost and the attack/defense percents index by this. |
| 3 | `DAT_00069d0b` | Backdrop. Combat loads `Back%02d.saf` from it, after decrementing it when it is nonzero. |

The same call stores the occupancy byte at `grid + (y * width + x) * 2 + 1` into `DAT_00069d0c`. The attack confirm rejects a tile whose stored byte is `0xff`. How that byte is marked for a swing is in [Combat](combat.md).

On disk, byte 2 takes values 0, 1, 2, 5, and 6. Byte 3 takes 55 distinct values, the largest 63, which matches the 63 backdrop files. For 67 of the 69 `ATTR` files the record count equals that picture run, including `M310` at 192. `M630` has 192 pictures and 288 records; its `MPL` only names tiles 0 through 149. `ATTR151.DAT` has 192 records and no section CEL.

Movement is a flood fill in `FUN_00010de0`. The occupancy grid is `width * height` byte pairs in front of which `FUN_000227b0` writes the two dimensions. `FUN_00010b20` sets each pair's second byte to `0xff` and masks the first with `0x3f`. The fill then treats the first byte's bit `0x40` as "do not enter" and bit `0x80` as "entering spends the whole remaining budget". The second byte is the best cost found so far. Cost of a step is `cost_here + move_row[terrain]`, where `move_row` is the 10-byte `ProMap.dat` row for the unit's class. Who stamps bit `0x40` and bit `0x80` was not read. The percents applied to attack and defense are signed dwords:

| Terrain | Attack %, dwords at `0x60040` | Defense %, dwords at `0x60058` |
| --- | --- | --- |
| 0 | +5 | 0 |
| 1 | 0 | 0 |
| 2 | −5 | +10 |
| 3 | −5 | +10 |
| 4 | −5 | −5 |
| 5 | 0 | 0 |
| 6 | 0, because it reads the first defense dword | the dword at `0x60070`, not copied here |

`FUN_00012550` returning nonzero skips that percent for that fighter. What it tests was not read. How the percent enters the damage formula is in [Combat](combat.md).
