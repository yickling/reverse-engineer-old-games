# Map, camera, and terrain

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

The picture is mode 13h, 320×200. A map frame is composed by `object 1 + 0x1bcf0` into a buffer of `0x15180` bytes at pitch `0x168` (360). `object 1 + 0x1c0c0` paints one section as 14 columns by 9 rows of 24×24 tiles, which is the 320×200 window with a partial tile at the right and bottom edges. The camera origin is in pixels. `object 2 + 0x9ce4` is the horizontal origin and `object 2 + 0x9ce0` the vertical one. The same two axes for the cursor are `object 2 + 0x9cd4` and `object 2 + 0x9ccc`.

`object 1 + 0x1c0c0` divides the camera by 24 and keeps the remainder, so the window can sit between tile boundaries. For each of the 9×14 cells it wraps the tile coordinate across the section width and height (the shorts at MPL `+7` and `+9`). The MPL cell is the little-endian short at `file + 0x0b + (y * width + x) * 2`. That short is the tile-picture index. Where those files come from is in [Scenario files](scenario.md).

The `MPL`, `ATTR`, and `DTL` records are the structs in [File formats](formats.md). `object 1 + 0x127b0` keeps one pointer per section, and the count is `object 2 + 0x9cdc`. `object 2 + 0x9cb0` is `m%02d%d.mpl` from `FIELD1.VFS`. `object 2 + 0x9c20` is `m%02d%d.cel` from the same archive. `object 2 + 0x9c98` is `attr%02d%d.dat` from `FIELD2.VFS`. Both numbers in the name are the scenario index and the section. `object 1 + 0x1bcf0` passes section `i`'s three pointers to `object 1 + 0x1c0c0`, with the scaled camera, the occupancy grid, and that section's highlight byte. The painter reads width and height at MPL `+7` and `+9` and the cell short at `+0xb`, and adds `0x11` to the ATTR pointer before the 4-byte records. Section 0's MPL, the dword at `object 2 + 0x9cb0` with no index, is the grid whose dimensions are copied into the occupancy layer and whose cell short the search increments, in [Scenario files](scenario.md) and [Turns](turns.md). `object 1 + 0x19410` and `object 1 + 0x212b0` free all three arrays.

Tile pixels come from the section CEL. Its header matches `ICON.CEL`: `CEL`, version `1`, then three big-endian shorts. Those shorts are the directory offset, the width, and the height. On `M000.CEL` they are `0x0f`, 24, and 24. The directory is little-endian dwords. When the file is packed, the first dword is the file offset where the pictures begin, so the number of directory entries is `(first_offset - directory_offset) / 4`, and the last entry is the end of the last picture rather than a picture of its own. The picture list is the run of little-endian dwords at the directory that stay increasing, inside the file, and past the end of the table itself. Mode 0 at 24×24 consumes every span of that run for 68 of the 69 section files, through the end of the file. The uint16 at header `+10` is only a prefix of that run: on `M190`, `M290`, and `M620` it counts 28, 129, and 120 pictures, and the run continues for 284, 385, and 376. Those three counts are the `ATTR` record counts. `M310` has the same shape of run, 192 pictures, and mode 0 does not expand any of them. The `MPL` for that section names tiles 0 through 172. `object 1 + 0x4664b` expands the picture selected by `dword[directory + index * 4]`. Mode 0 of that expander, and the byte that widens a window CEL, are in [Pictures](pictures.md).

Drawing one cell, from `object 1 + 0x1c0c0`:

```
tile = mpl_short(x, y)
if highlight == 0:
    blit picture[tile] with expander mode 0          # plate ignores the range
else:
    attr = byte[attr_file + 0x11 + tile * 4]
    kind = attr & 7
    if kind == 1: tile = tile + blink          # blink is 0 or 1, flipped every 4 ticks
    if kind == 2: tile = tile + ((tick >> 2) & 3) * 0x60
    if attr & 0x80:
        blit picture[tile], mode 9, selector = attr byte +1
    else if cost_byte(x, y) == 0xff:
        blit picture[tile], mode 0             # outside the range
    else if highlight == 1:
        blit picture[tile], mode 10            # flat recolor of the tile
    else:
        blit picture[tile], mode 9, selector = pulse key   # blend over the buffer
```

A section carries two bytes a designer sets separately. `object 1 + 0x127b0` reads both from the `DSC` record at `object 1 + 0x12a68`. The seventh dword, stored in `object 2 + 0x9cfe`, is when the plate is painted. The eighth, stored in `object 2 + 0x9cf8`, is `highlight` above: how a tile inside the move or spell mask is colored. The mask itself is in [Combat](combat.md).

Across all 62 `DSC` files, 66 sections, the pairs are:

| Sections | Order | Highlight | Where it sits | How a marked tile is drawn |
| --- | --- | --- | --- | --- |
| 62 | 9 | 1 | Under the cursor and the units | Mode 10, a recolor of the tile |
| 3 | 8 | 0 | Before that ground plate | Mode 0 always. The mask is skipped |
| 1 | 11 | 2 | After the units | Mode 9, blended over the buffer |

`object 1 + 0x1bcf0` paints every section whose order byte is below 10, then the cursor pictures, then the units, then every section whose order byte is above 10. The unit pass is the shadow, the sprite, and the status mark, in [Pictures](pictures.md). An order of 10 would fall in neither pass. No file stores 10, so that value is the seam where the cursor and the units are inserted.

Disassembly of `object 1 + 0x1bfb0` and `object 1 + 0x1cfd0`, not a decompile. `object 1 + 0x1bfb0` writes section indexes 0 through the count at `object 2 + 0x9cdc` minus 1, then bubble-sorts that array by the order byte at `object 2 + 0x9cfe`. A lower byte comes first. An equal byte is not swapped. The compose walks that array, which is why the plates below 10 are painted before the cursor and the units. `object 1 + 0x1c430`, the pictures around the cursor in [Combat](combat.md), sits between that first pass and the units. `object 1 + 0x1cfd0` then walks every unit twice through `object 1 + 0x1cb30`. The first walk stores 1 at `object 2 + 0x14c`, which is the shadow pass. The second stores 0, which is the sprite. The byte it pushes is written 0 at the start of `object 1 + 0x1cb30`, and the compose passes 0. A remake paints back to front: every section whose order byte is below 10, lowest first and with an equal byte keeping index order, then the aim marks, then every shadow, then every sprite, then every section whose order is above 10. The 62 ground plates use 9, the last value that still goes under them. The three plates at 8 are the second section of `DSC05.DAT`, `DSC29.DAT`, and `DSC63.DAT`. The one plate at 11 is the second section of `DSC07.DAT`. Inferred from that split: order 8 is a background, order 9 is the ground the player stands on, and order 11 is a foreground that can cover a unit.

The same function places a plate with `(camera * scale + offset) >> 3`. `object 1 + 0x127b0` stores the section's third dword as the horizontal scale (`object 2 + 0x9c80`) and the fourth as the vertical scale (`object 2 + 0x9c68`). The first two dwords are the offsets (`object 2 + 0x9bf0`, `object 2 + 0x9c08`). The fifth and sixth (`object 2 + 0x9c50`, `object 2 + 0x9c38`) are added to those offsets when `object 2 + 0x9d64` changes. Every one of the 66 sections stores 0 in those four, so a plate does not drift on its own. Every ground plate and the foreground plate store scale `8, 8`, and `(camera * 8) >> 3` is the camera, so they stay locked to it. The three order-8 plates store `4, 2` or `8, 4`, which is half or a quarter of the camera step. Inferred: a smaller scale is a farther plate. Those three also store highlight 0, so the range is not drawn on them.

Highlight 0 leaves the plate as stored pictures. Highlight 1, which is every ground plate, uses expander mode 10: the tile is recolored from its own pixels, and the pixel already in the buffer is not read. The ramp is the dword `object 2 + 0x154`. No instruction stores it, so that recolor does not change during play. Inferred: the range on the ground is one fixed tint of the terrain, and it looks the same whether or not a background plate was drawn underneath. Highlight 2, the foreground plate, uses mode 9. That mode mixes the tile with the pixel already in the buffer, so the tint includes the units painted a moment earlier. Its selector walks the 14 bytes at `object 1 + 0x1b010`, `02 03 04 05 06 07 07 07 06 05 04 03 02 02`. `object 2 + 0x15c` advances by 1 on every call of this painter and wraps at `0x38`. The index is that counter divided by 4, so each byte is held for four section paints. Inferred: the foreground range shimmers, and the walk stays in the lower half of the blend ramp (a selector above 8 is folded by `0x10 - selector` in [Pictures](pictures.md)).

The blend record for modes 9 and 10 is four dwords: `object 2 + 0x53f0`, the selector, `object 2 + 0x43f0`, and `object 2 + 0x154`. Mode 9 reads the selector. Mode 10 reads the last dword once. Attribute bit `0x80` is a separate tint. It always calls mode 9 and uses attribute byte `+1` as the selector, so it does not use the pulse table and it does not read the mask.

`tick` is `object 2 + 0x9d64`. `blink` is `object 2 + 0x160`. Across the `ATTR` files, the low 3 bits are only ever 0 or 2, so the two-frame blink is unused on disk and the four-step `* 0x60` animation is the one that occurs. Mode 0 is the plain expander. Modes 9 and 10 are `object 1 + 0x4738b` and `object 1 + 0x47503`.

The cursor pictures are in [Combat](combat.md). The visible copy out of the map buffer is 320×200 from buffer+`0x21d8` in the phase transition, and the combat copy is buffer+`0x2298` at pitch `0x170`. The command icons and the message box are drawn into the same buffer, and the copy that follows them is 312×192 from that origin onto `(4, 4)` of the 320-wide surface, in [Pictures](pictures.md).

`object 1 + 0x1b790(x, y)` is the tile query. It reads the MPL short into `object 2 + 0x9d04`, then the 4-byte `ATR` record for that picture:

| Record byte | Stored at | Use |
| --- | --- | --- |
| 0 | `object 2 + 0x9d08` | The animation byte the drawer reads. Bits `0x60` are the tile-search test in [Turns](turns.md). |
| 1 | `object 2 + 0x9d0a` | Passed to the expander when bit `0x80` of byte 0 is set. |
| 2 | `object 2 + 0x9d09` | Terrain kind. Movement cost and the attack/defense percents index by this. |
| 3 | `object 2 + 0x9d0b` | Backdrop. Combat loads `Back%02d.saf` from it, after decrementing it when it is nonzero. |

The same call stores the occupancy byte at `grid + (y * width + x) * 2 + 1` into `object 2 + 0x9d0c`. The attack confirm rejects a tile whose stored byte is `0xff`. How that byte is marked for a swing is in [Combat](combat.md).

On disk, byte 2 takes values 0, 1, 2, 5, and 6. Byte 3 takes 55 distinct values, the largest 63, which matches the 63 backdrop files. For 67 of the 69 `ATTR` files the record count equals that picture run, including `M310` at 192. `M630` has 192 pictures and 288 records; its `MPL` only names tiles 0 through 149. `ATTR151.DAT` has 192 records and no section CEL.

Movement is a flood fill in `object 1 + 0xde0`. The occupancy grid is `width * height` byte pairs. `object 1 + 0x127b0` writes the width and height of section 0, the first `MPL` of this scenario. The grids and the check that every placed coordinate lands inside them are in [Scenario files](scenario.md). `object 1 + 0xb20` sets each pair's second byte to `0xff` and masks the first with `0x3f`. The fill then treats the first byte's bit `0x40` as "do not enter" and bit `0x80` as "entering spends the whole remaining budget". The second byte is the best cost found so far. Cost of a step is `cost_here + move_row[terrain]`, where `move_row` is the 10-byte `ProMap.dat` row for the unit's class. `object 1 + 0xb90(filter)` calls `object 1 + 0xc30` on each visible unit the filter accepts. Filter 0 accepts a side other than 0, and any other filter accepts side 0. `object 1 + 0xc30` ORs `0x40` into the first byte of that unit's pair, and ORs `0x80` into the first byte of each of the four orthogonal neighbors that sit on the map. The walk that asks for this stamp is in [Turns](turns.md). The percents applied to attack and defense are signed dwords:

| Terrain | Attack %, dwords at `object 2 + 0x40` | Defense %, dwords at `object 2 + 0x58` |
| --- | --- | --- |
| 0 | +5 | 0 |
| 1 | 0 | 0 |
| 2 | −5 | +10 |
| 3 | −5 | +10 |
| 4 | −5 | −5 |
| 5 | 0 | 0 |
| 6 | 0, because it reads the first defense dword | the dword at `object 2 + 0x70`, not copied here |

`object 1 + 0x2550` returning nonzero skips that percent for that fighter. The classes it accepts are in [Combat](combat.md), with the way the percent enters the damage formula.
