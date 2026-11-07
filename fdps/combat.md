# Combat numbers

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. How the fight screen is drawn is in [Pictures](pictures.md). The unit words are in [Units](units.md).

## From the map to the fight

Two callers reach the same clip player.

The command menu is `object 1 + 0x5cf0`, opened when a move ends on the unit's current tile. Slot 0 is the attack. It reads the weapon with `object 1 + 0x15110(unit, 0)`, the first equipped pair whose type is from 1 through `0x15`, then `object 1 + 0x8b30`. Weapon bytes `+0xb` and `+0xc` go to `object 1 + 0x1e50` as the range, with side filter 0, so the list is visible units whose side byte is `0` and whose occupancy byte is not `0xff`.

`object 1 + 0x1e50` marks that occupancy grid, then `object 1 + 0x1b280` lets the cursor move a tile at a time. `Z` (`0x2c`) and keypad 5 (`0x4c`) step through the list and center on that unit. Confirm (`0x39` or `0x1c`) accepts when `object 1 + 0x1b790` stored an occupancy byte other than `0xff` and `object 1 + 0x9f0` finds a side-`0` unit on that tile. The menu sets `object 2 + 0x9cd0` to 1 before the picker, and the distance test is strict less-than that value, so the unit has to be on the cursor tile. Escape (`0x01`) or delete (`0x53`) returns −1 and the menu stays up. A chosen target is faced with `object 1 + 0xc2b0`, then `object 1 + 0x8d50` plays the clips. The menu does not read `object 2 + 0x10`. It always plays the screen.

The phase walker is `object 1 + 0x10`, called for side `1` and then side `0` from `object 1 + 0xe3c0`. Which script runs is in [Turns](turns.md). `object 1 + 0x2c10` fills the three scores below and returns 0 when all three are below 6. Otherwise the largest score wins. The comparison is the last step of the routine at the end of this section. `attack` and `defense` there are the attacker's `+0x48` and the defender stored by the swing scorer, its `+0x4a`. The spell id is `object 2 + 0x3f90`, and its row is `object 1 + 0x8bc0`. A three-way tie at 6 or above matches none of those tests: the function still returns 1, and it does not call an action. The swing is `object 1 + 0x2e50`. The cast is `object 1 + 0x3c90` and the item action is `object 1 + 0x17150`, both below. `object 1 + 0x2e50` is the swing:

```
center the camera on the attacker          # object 1 + 0x1d7e0
walk toward object 2 + 0x3f80, object 2 + 0x3f84     # object 1 + 0x19e0
center on the defender
face the defender                          # object 1 + 0xc2b0
wait 100                                   # object 1 + 0x33a20
if object 2 + 0x10 == 0:
    redraw the map and apply the pools in place    # object 1 + 0xc370
else:
    play the clips                         # object 1 + 0x8d50
```

The settings corner flips `object 2 + 0x10`, and the save load restores it, both in [Turns](turns.md) and [Save](save.md). The compare at `object 1 + 0x3d6d` is the branch above: 1 calls `object 1 + 0xa4a0`. The byte in the image is 1. The writes of that byte are the xor with 1 at `object 1 + 0x84ad`, the front-of-file restore at `object 1 + 0x1414e` (the record byte at `+0xe`), and the slot restore at `object 1 + 0x145af` (the slot byte at `+7`). `object 1 + 0x5268` reads the byte into the front save at that same `+0xe`, which is file offset `0x30d1` in [Save](save.md). Title row 0 calls neither restore, and the opener does not store the byte, so it is still 1 when the opener returns. The swing treats 0 as the map and any other value as the clips, so a new game plays the fight. A remake of that visit shows the fight until the player flips the corner.

The walk in `object 1 + 0x19e0` flood-fills with the attacker's move budget. Each path byte is one tile: `0` +Y, `1` −X, `2` −Y, anything else +X. `object 1 + 0x1d060` plays a tile as six redraws. `object 1 + 0x1d0f0` (the +Y step; the other three facings are the same shape) sets facing, then writes sub-tile byte `+4` from 1 through 6 and adds 4 to the camera and the cursor on each redraw. Six steps of 4 pixels is one 24-pixel tile. A key byte of `0x02` or `0x03` skips the intermediate redraws. After the last step the tile coordinate increments and `+4` returns to 0.

Facing, from `object 1 + 0xc2b0`, compares absolute dx with absolute dy. The larger axis wins. Defender to the left is facing 1, to the right is 3, above is 2, below is 0.

Range marking, from `object 1 + 0x1e50(x, y, dest, shape, inner, side)`. The cost byte is the mask: `0xff` is outside, and any other value is inside. `shape` below `0x10` calls `object 1 + 0xde0` with the class-0 move row, the center, and `shape` as the budget. That fill writes `0` on the origin and does not clear the other tiles, so a caller that wants a fresh mask calls `object 1 + 0xb20` first. If `inner` is nonzero, every tile whose Manhattan distance from the center is below `inner` is then set back to `0xff`. `shape` at or above `0x10` subtracts `0x10` and writes `0` on the center's row where `|dx|` is at most that radius, and on the center's column where `|dy|` is at most that radius. It does not clear either. A visible unit is listed when its tile's cost byte is not `0xff` and its side matches `side`: `0` keeps side `0`, `1` keeps a side other than `0`, `2` keeps side `1`, and `3` keeps side `2`. The ids are written in unit-index order. A null `dest` only returns the count. Tiles left at `0xff` are the ones confirm rejects. `object 1 + 0x1b790` stores that same occupancy byte at `object 2 + 0x9d0c`. The counter test is a third use of weapon byte `+0xb`: `object 1 + 0x37e0` returns 1 when the defender's `+0x26` is 0, the two units are one tile apart, and `+0xb` is 1.

## The spell area

A spell hits the units standing on the tiles this mask marks. The row is `object 1 + 0x8bc0`. Byte `+4` is the `shape` above. Byte `+3` is a second range, used to choose where the mask is centered. Spells pass `inner` 0, so the flood is not punched back. The step costs of that flood are the class-0 row in [Map](map.md). The cast itself is `object 1 + 0x3c90`: it paints from the stored stand with byte `+4`, copies the ids, then clears the grid.

`object 1 + 0x3420` clears between the two paints. It flood-fills from the caster with budget byte `+3`, copies the reached tiles with `object 1 + 0x1da0`, and calls `object 1 + 0xb20`. Each of those tiles is then a center: `object 1 + 0x1e50` with `shape` byte `+4` and `inner` 0, then another clear before the next center. The CPU never takes the line below. A shape of `0x10` or more is the plus.

The player's aim, `object 1 + 0x17bf0`, is the other center. Byte `+3` equal to 0 paints byte `+4` from the cursor tile, side filter 0, and does not clear first. Any other byte `+3` first paints that byte from the cursor, with side byte `+6`, and the picker runs. After the picker confirms, the grid is cleared. Byte `+3` of 15 or less then paints byte `+4` from the cursor that was confirmed. Byte `+3` of 16 or more does not paint a second area. It walks a line with `object 1 + 0x3670` and plays `Chess.wav`. The same line is what an item uses when its range byte is `0x10` or higher: `(stand x, stand y, buffer, unit x, unit y, byte +0x10 - 0x10, side)`.

`object 1 + 0x3670(cursor x, cursor y, dest, origin x, origin y, length, side)` does not use the cost grid. The step is one tile on a single axis, from the origin toward the cursor. Equal x steps in y: a smaller cursor y steps toward smaller y, and any other cursor y, including the same tile, steps toward larger y. Any other x steps in x, toward smaller x when the cursor x is smaller, otherwise toward larger x. The origin tile is not tested. Each of the `length` steps moves the cursor pixel by 24, and a step inside the map asks `object 1 + 0x1d830` for the unit under that pixel. Side argument 0 keeps a side other than 0. Any other argument keeps side 0. Flag bit 0 is not tested. The player passes the caster as the origin, the cursor as the aim, length `byte +3 - 0x10`, and side argument 1. The two cursor pixels are saved and restored.

A marked tile is drawn from the section's highlight byte. Highlight 1, every ground plate, recolors the tile in place (expander mode 10). Highlight 0 skips the mask. Highlight 2 blends the tile over the buffer and walks the pulse selector. Which files use which pair, and the reading of them as ground, a farther plate, and a foreground shimmer, are in [Map](map.md). The player's picker runs while the aim mask is still on the grid, so that is the area on screen. The effect list is painted and then cleared by `object 1 + 0xb20` with no compose between the two calls.

`object 1 + 0x1c430` lays pictures on tiles around the cursor pixel when `object 2 + 0x9cd0` is 1 through 5. That global is the cursor leash: confirm is a strict less-than against it. A spell stores byte `+4` plus 2 there before aiming, and the zero byte-`+3` path then forces it to 1. Value 6 writes cost 0 on the cursor tile and draws nothing. Any other value draws nothing. `object 1 + 0x1c9b0` copies one 24×24 picture from `Cusor.cel`, the file `object 1 + 0x19630` stores at `object 2 + 0x43c8`, when the pixel sits in the camera window. Offsets below are tiles, picture index in parentheses.

```
# object 1 + 0x1e50. Cost 0xff is outside the mask.
# object 1 + 0xde0 writes 0 on the origin and does not clear.

def paint(x, y, shape, inner):
    if shape < 0x10:
        flood(class_0_move_row, x, y, budget=shape)
        if inner != 0:
            set cost to 0xff where |dx| + |dy| < inner
    else:
        radius = shape - 0x10
        set cost to 0 where the tile shares x or y
            and |dx| <= radius or |dy| <= radius

def line(cursor, origin, length, side):       # object 1 + 0x3670
    if cursor.x == origin.x:
        step = (0, -1) if cursor.y < origin.y else (0, 1)
    else:
        step = (-1, 0) if cursor.x < origin.x else (1, 0)
    tile = origin
    hits = []
    repeat length times:
        tile = tile + step
        if tile is on the map:
            id = unit under that pixel          # object 1 + 0x1d830, or none
            if id exists and (side == 0) == (unit.side != 0):
                hits.append(id)
    return hits

# object 1 + 0x1c430. Pictures, not the hit test.
# 1: (0,0)=0
# 2: (0,0)=1
# 3: (0,0)=0xe  (0,-1)=2  (-1,0)=3  (1,0)=4  (0,1)=5
# 4: (0,0)=1  (0,-2)=2  (-2,0)=3  (2,0)=4  (0,2)=5
#    (-1,-1)=6  (1,-1)=7  (-1,1)=8  (1,1)=9
#    (0,-1)=10  (-1,0)=11  (1,0)=12  (0,1)=13
# 5: (0,0)=1  (0,-3)=2  (-3,0)=3  (3,0)=4  (0,3)=5
#    (-1,-2)=(-2,-1)=6  (1,-2)=(2,-1)=7
#    (-1,2)=(-2,1)=8  (1,2)=(2,1)=9
#    (0,-2)=10  (-2,0)=11  (2,0)=12  (0,2)=13
#    (-1,-1)=0xe  (1,-1)=0xf  (1,1)=0x10  (-1,1)=0x11

def player_aim(caster):                        # object 1 + 0x17bf0
    leash = spell[+4] + 2                      # object 2 + 0x9cd0
    if spell[+3] == 0:
        leash = 1
        list = paint_and_list(cursor, spell[+4], side=0)
    else:
        list = paint_and_list(cursor, spell[+3], side=spell[+6])
        if the picker confirms:
            clear the grid                        # object 1 + 0xb20
            if spell[+3] <= 15:
                list = paint_and_list(cursor, spell[+4], side=spell[+6])
            else:
                list = line(cursor, caster.tile, spell[+3] - 0x10, side=1)
    return list

def cpu_spell_area(caster):                    # object 1 + 0x3420
    flood(class_0_move_row, caster.tile, budget=spell[+3])
    stands = tiles whose cost is not 0xff
    clear the grid
    for stand in stands:
        list = paint_and_list(stand, spell[+4], inner=0, side=folded spell[+6])
        clear the grid
        score list
```

## The three scores

Each scorer writes 0, then raises its global only when it finds a candidate. All three return 0. The numbers they store are bands, not the damage formula.

`object 1 + 0x2230` is the swing. It reads the weapon through `object 1 + 0x15110(unit, 0)` and `object 1 + 0x8b30`, flood-fills with budget `+0x3b` on `object 1 + 0x8b60(class + 1)`, and asks `object 1 + 0x1da0` for the reachable tiles. `object 1 + 0x1da0` lists every tile whose cost byte is not `0xff`, in row-major order, and returns the count. `object 1 + 0x18f0` writes `0xff` into that byte for the other visible units on one side of the filter. The same two calls choose where a CPU walk stops, in [Turns](turns.md). From each stand tile, `object 1 + 0x1e50` lists targets with `shape` = weapon byte `+0xc`, `inner` = byte `+0xb`, and `side` = 1 when the phase filter is 0, else 0. A phase filter of 0 is the side-`0` walk, so that walk's swing list is every visible unit whose side is not 0. Side `1` passes filter 1, and its swing list is side 0. For a target the band is 0 when `attack - defense` is below 3, else 8. When that margin is greater than the target's `+0x40`, the margin is doubled and the band becomes `0x12`. `object 1 + 0x25c0` returns 1 only when the attacker's `+0x26` is 0, the two tiles are one step apart on a side (`object 1 + 0x2d0d4` is the absolute value, and the two absolutes sum to 1), the weapon-group lookup finds a pair, and that record's byte `+0xb` is below 2. Any other case returns −1. A return of 1 adds the attacker's `+0x4a` minus the target's `+0x48` to the margin. A target whose byte `+8` is 0 multiplies the margin by 3/2. The kept candidate is the highest band, and on a tie the larger margin. An equal band and an equal margin keeps the earlier stand tile, and within a tile the earlier unit index. It stores the target in `object 2 + 0x3f74` and the stand tile in `object 2 + 0x3f80` and `object 2 + 0x3f84`.

`object 1 + 0x3420` is the spell. `object 1 + 0x17810` fills the id list, the same call that enables menu slot 1, and byte `+0x27` must be 0. A spell is skipped unless byte `+5` of its `object 1 + 0x8bc0` row is at or below the word at unit `+0x44`. The flood fill uses budget byte `+3` of that row and the class-0 move row. The reached tiles are copied, the grid is cleared, and each of them is then a center for the area mask in [The spell area](#the-spell-area). `object 1 + 0x1e50` lists targets with `shape` = row byte `+4`, `inner` = 0, and a side taken from row byte `+6`. The grid is cleared again after that list. When the phase filter is 0, byte `+6` equal to 0 becomes list side `1`, and any other value becomes list side `0`. When the phase filter is not 0, byte `+6` is the list side as stored. `object 1 + 0x3920` scores that list, and the kept candidate is the higher score, then the larger first short of the row. An equal score and an equal short keeps the earlier tile. The stand tile is `object 2 + 0x3f9c` and `object 2 + 0x3fa0`, and the spell id is `object 2 + 0x3f90`.

`object 1 + 0x3920` sums a per-target band. Ids `0x0e`, `0x0f`, `0x10`, and `0x21` score the target's pool against its `+0x42`: 8 when the pool is below a third, 3 when it is below a half, otherwise 0, and bit 0 of `+0x34` doubles that. Id `0x11` adds 6 for each target that still has a spell list and whose `+0x27` is 0. Id `0x18` adds 6 for each target whose `+0x25`, `+0x26`, or `+0x27` is nonzero. Id `0x12` adds 10 for each target whose `+0x25` is 0. Id `0x13` does the same for `+0x26`. Id `0x14` calls that counter three times, for `+0x22`, `+0x23`, and `+0x24`, and keeps only the last return, so the score is 4 per target whose `+0x24` is 0. The counter is `object 1 + 0x3c20`. Every other id adds 8, or `0x18` when the pool is below the row's first short. Ids `0x0a` and `0x0b` skip a target that `object 1 + 0x2550` accepts. A target whose byte `+8` is 0 replaces that band with `trunc(band * 3 / 2)`. At `object 1 + 0x3bf0` the band, 8 or `0x18`, is loaded with `FILD` and multiplied by the double `1.5` at `object 2 + 0x1571`. `object 1 + 0x2d25c` then rounds toward zero: it stores the control word, sets the high byte to `0x1f`, runs `FRNDINT`, and restores the word. `FISTP` writes the result back. 8 becomes 12. `0x18` becomes 36.

`object 1 + 0x3040` is the carried item. `object 1 + 0x15210` is the count, the same call that enables menu slot 2. Index `i` reads the id at unit `+0x0b + i * 2` and the record from `object 1 + 0x8b30`. Byte `+0x0d` of that record must be nonzero. The stand tiles come from one `object 1 + 0x1e50` at the unit's own tile whose list is discarded: byte `+0x10` below `0x10` is the `shape` and `inner` is 0, and a byte at or above `0x10` is painted with `shape` 1 and `inner` 1. From each stand tile the target list uses record byte `+0x12` as `shape` and `inner` 0 when byte `+0x10` is below `0x10`. At or above `0x10` the list is the line in [The spell area](#the-spell-area), called as `(stand x, stand y, buffer, unit x, unit y, byte +0x10 - 0x10, side)`. The side is record byte `+0x11`, with the same fold the spell uses: a phase filter of 0 turns byte 0 into list side `1` and any other byte into list side `0`. `object 1 + 0x32b0` scores that list, and a strictly higher score replaces `object 2 + 0x3f8c`. The stand tile is `object 2 + 0x3f98` and `object 2 + 0x3f94`, and the slot index is `object 2 + 0x3f7c`.

`object 1 + 0x32b0` returns 0 unless byte `+0x0d` is `0x0b` or `0x1e`. Kind `0x0b` uses signed division toward zero. A target whose `+0x40` is at or below `+0x42 / 3` adds 8. Above that and at or below `+0x42 / 2` adds 3. Above half adds 0. Bit `0x80` of `+0x34` multiplies that term by 3. Kind `0x1e` adds `0x12` when `+0x40` is at or below the short at record `+0x0e`, and 8 when it is above that short.

## The CPU routine

This is `object 1 + 0x2c10` together with the three scorers. Rows 0, 1, 2, 3, and 5 of the script table call it first. Rows 10 and 11 do not: row 10 takes the item when that score is above 5, then the swing when its score is 6 or more, and otherwise the budget-100 walk. Row 11 is that shape with the spell and `object 1 + 0x3c90` in place of the item. Division is toward zero.

```
# phase is the filter object 1 + 0x10 was given.
# 0 is the side-0 walk. 1 is the side-1 walk.
# A unit is visible when bit 0 of byte +5 is clear.

def folded_side(phase, byte):
    if phase == 0:
        return 1 if byte == 0 else 0
    return byte

# object 1 + 0x1e50. Writes ids in unit-index order.
# side 0 keeps side 0. side 1 keeps any side other than 0.
# side 2 keeps side 1. side 3 keeps side 2.
def targets(x, y, shape, inner, side):
    paint(x, y, shape, inner)                       # the mask above
    return visible units on a tile whose cost is not 0xff
        and whose side matches side

def swing_margin(attacker, target, stand):             # object 1 + 0x2230
    margin = attacker[+0x48] - target[+0x4a]
    band = 0 if margin < 3 else 8
    if target[+0x40] < margin:
        margin = margin * 2
        band = 0x12
    if object 1 + 0x25c0(target, stand) == 1:
        margin = margin + attacker[+0x4a] - target[+0x48]
    if target[+8] == 0:
        margin = (margin * 3) / 2
    return band, margin

def score_swing(unit, phase):                          # object 1 + 0x2230
    best = (0, none)
    weapon = equipped pair of type 1..0x15             # object 1 + 0x15110(unit, 0)
    if weapon is missing:
        return best
    row = Item.dat[weapon]
    stamp(phase)                                       # object 1 + 0xb90
    fill(ProMap[class + 1], unit.tile, budget = unit[+0x3b])
    punch the other units on the mover's side          # object 1 + 0x18f0
    side = 1 if phase == 0 else 0
    for stand in tiles whose cost is not 0xff:         # object 1 + 0x1da0, row-major
        for target in targets(stand, row[+0xc], row[+0xb], side):
            band, margin = swing_margin(unit, target, stand)
            if band > best.band or (band == best.band and margin > best.margin):
                best = (band, margin, target, stand)
    return best

def spell_band(spell_id, targets):                     # object 1 + 0x3920
    row = MagicDat[spell_id]
    total = 0
    if spell_id in (0x0e, 0x0f, 0x10, 0x21):
        for target in targets:
            pool, maxp = unsigned(target[+0x40]), unsigned(target[+0x42])
            if pool < maxp / 3: term = 8
            else if pool < maxp / 2: term = 3
            else: term = 0
            if bit 0 of target[+0x34] is set: term = term * 2
            total = total + term
    else if spell_id == 0x11:
        total = 6 * count of targets that have a spell list and +0x27 == 0
    else if spell_id == 0x12:
        total = 10 * count of targets whose +0x25 == 0     # object 1 + 0x3c20
    else if spell_id == 0x13:
        total = 10 * count of targets whose +0x26 == 0
    else if spell_id == 0x14:
        total = 4 * count of targets whose +0x24 == 0
        # the same count for +0x22 and for +0x23 is computed and dropped
    else if spell_id == 0x18:
        total = 6 * count of targets whose +0x25, +0x26, or +0x27 is nonzero
    else:
        for target in targets:
            if spell_id in (0x0a, 0x0b) and object 1 + 0x2550(target) != 0:
                continue
            term = 0x18 if target[+0x40] < row.first_short else 8
            if target[+8] == 0:
                term = trunc(term * 1.5)            # double at object 2 + 0x1571, object 1 + 0x2d25c
            total = total + term
    return total

def score_spell(unit, phase):                          # object 1 + 0x3420
    best = (0, none)
    if unit[+0x27] != 0 or the unit has no spell list:
        return best
    for spell_id in the learned list:                  # object 1 + 0x17810
        row = MagicDat[spell_id]
        if row[+5] > unit[+0x44]:
            continue
        fill(class-0 move row, unit.tile, budget = row[+3])
        side = folded_side(phase, row[+6])
        for stand in tiles whose cost is not 0xff:
            listed = targets(stand, row[+4], 0, side)
            if listed is empty:
                continue
            score = spell_band(spell_id, listed)
            if score > best.score or (score == best.score and row.first_short > best.short):
                best = (score, row.first_short, spell_id, stand)
    return best

def item_band(record, targets):                        # object 1 + 0x32b0
    total = 0
    if record[+0x0d] == 0x0b:
        for target in targets:
            if target[+0x42] / 3 < target[+0x40]:
                term = 0 if target[+0x42] / 2 < target[+0x40] else 3
            else:
                term = 8
            if bit 0x80 of target[+0x34] is set: term = term * 3
            total = total + term
    else if record[+0x0d] == 0x1e:
        for target in targets:
            total = total + (8 if record[+0x0e] < target[+0x40] else 0x12)
    return total

def score_item(unit, phase):                           # object 1 + 0x3040
    best = 0
    for slot in carried pairs whose record[+0x0d] != 0:
        record = Item.dat[id at unit +0x0b + slot * 2]
        side = folded_side(phase, record[+0x11])
        # the first list is discarded; it only paints the stand tiles
        if record[+0x10] < 0x10:
            targets(unit.tile, record[+0x10], 0, 0)
        else:
            targets(unit.tile, 1, 1, 0)
        for stand in tiles whose cost is not 0xff:
            if record[+0x10] < 0x10:
                listed = targets(stand, record[+0x12], 0, side)
            else:
                listed = line(stand, unit.tile, record[+0x10] - 0x10, side)
            if listed is empty:
                continue
            score = item_band(record, listed)
            if score > best:
                best = (score, slot, stand)
    return best

def choose_action(unit, phase):                        # object 1 + 0x2c10
    swing = score_swing(unit, phase)                   # object 2 + 0x3f78
    spell = score_spell(unit, phase)                   # object 2 + 0x3f88
    item = score_item(unit, phase)                     # object 2 + 0x3f8c
    if swing.band < 6 and spell.score < 6 and item.score < 6:
        return no action
    prefer_swing = bit 0x40 of unit[+0x34]
    defender = the unit id score_swing stored           # object 2 + 0x3f74, unchanged when no swing candidate
    if swing.band > spell.score and swing.band > item.score:
        play the swing                                  # object 1 + 0x2e50
    else if swing.band == spell.score and item.score < spell.score:
        if spell.id < 0x12:
            if MagicDat[spell.id].first_short < unit[+0x48] - defender[+0x4a]:
                play the swing
            else:
                cast                                    # object 1 + 0x3c90
        else if prefer_swing:
            play the swing
        else:
            cast
    else if swing.band == item.score and spell.score < item.score:
        if prefer_swing: play the swing
        else: use the item                              # object 1 + 0x17150
    else if swing.band < spell.score and item.score <= spell.score:
        cast
    else if swing.band < item.score and spell.score < item.score:
        use the item
    # a three-way tie at 6 or above calls none of these
    return acted
```

`object 1 + 0x3c90` casts when the spell band is at least 6. It lists targets from the stored stand tile with range byte `+4` of the spell row, moves the cursor there, waits 200, and plays the clips. `object 2 + 0x10 == 1` calls `object 1 + 0xa4a0`, which subtracts the spell row's byte `+5` through `object 1 + 0x18590`. Any other value calls `object 1 + 0x188c0`, which subtracts that byte at `object 1 + 0x18942`. Both then call `object 1 + 0x182f0` once per target, at `object 1 + 0xae3f` and `object 1 + 0x18e1f`. It then runs the death spin and the death-record walk with `object 2 + 0x3f74`, clears the experience term, and returns 1.

`object 1 + 0x182f0(caster, target, spell)` reads the signed short at the start of the spell row. A positive short is multiplied by byte `+9` of the target's `ProMap` row and divided by 100. A negative short is negated, multiplied by the caster's attack word, divided by 100, and then the target's defense word is subtracted, and a negative result becomes 0. `rand % 100` has to land below byte `+2`. Spell ids `0x0a` and `0x0b` also require `object 1 + 0x2550(target)` to be 0. `object 1 + 0x18430` then takes `amount * 9 / 10` plus `(rand % 100) * amount / 1000` off the target's word at `+0x40`, and floors that word at 0. When the target's side is 0 it adds to the experience term: `EnemyDat` byte `+9` of `character id - 0x3c`, times the target's byte `+0x21`. A pool that is still above 0 after the hit multiplies that add by the amount taken and divides by the maximum at `+0x42`.

## The two spell players

`object 2 + 0x10 == 1` calls `object 1 + 0xa4a0`. Any other value calls `object 1 + 0x188c0`. The clip names are in [Pictures](pictures.md).

`object 1 + 0xa4a0` sends ids `0x0a`, `0x0b`, `0x0e` through `0x16`, `0x18`, and `0x21` to `object 1 + 0x188c0` and returns. Every other id plays the fight. After the begin clip, `object 1 + 0x18590` subtracts the cost. A strike clip with no frame whose byte `+5` is set calls `object 1 + 0x32b5b` on the error string and `object 1 + 0x32b7f(1)`. For each target the player saves `+0x40`, calls `object 1 + 0x182f0` at `object 1 + 0xae3f`, saves the word again, and writes the first value back. A return of 0 skips the later writes. Id `0x0d` with a nonzero return also calls `object 1 + 0x18eb0`. Each hit frame then stores `start - (start - after) * n / hits` at `+0x40`. `n` counts hit frames as they are shown, and `hits` is how many the clip has. The last of them leaves the word where `object 1 + 0x182f0` put it. The experience term that function added stays. The map blend tables are copied back when the end clip finishes.

`object 1 + 0x18eb0(target)` walks `+0x25`, `+0x26`, and `+0x27`. When `rand % 100` is below `0x14` and `object 1 + 0x19050` returns 0, that byte becomes `rand % 2 + 2`.

`object 1 + 0x188c0` clears `object 2 + 0x9cd0` and sets it back to 1 before returning. Id `0x0b` formats `Emg%02d.saf` as 10 and then calls `object 1 + 0x185e0`. Any other id formats the id itself. Id `0x21` also opens `Emg33-1.saf`, plays it with `object 1 + 0x12290`, and frees that clip. That player is the map clip player in [Pictures](pictures.md). Ids `0x0a` and `0x0b` open `EarQu.wav`, start it with `object 1 + 0x20790(wav, 1, -1, -1)`, and redraw 25 times. Each redraw sets the camera to the saved point plus `rand % 4 - 2` on each axis, `object 1 + 0x1bc40` runs, and the two camera words are restored. `object 1 + 0x16dd0` then plays the formatted clip on the map. Each frame is drawn twice. A target is placed at `tile x * 24 - camera x - 24`, `tile y * 24 - camera y - 0x1e`. Only the first target on the first pass starts the sample. The blit is the map window: buffer `+0x21d8`, pitch `0x168`, to `0xa0504`, 312 by 192.

`object 1 + 0x185e0` opens `Mag11.saf`. It copies the screen, and for steps 31 down through 1 draws the current frame over that copy with mode 9 and selector `step / 2`. It then plays the clip through. The map palette is installed with bias `0x3f` on each channel, the 320 by 200 screen is cleared, and six redraws bring that bias down by 10 a step.

After the clip, ids `0x0e`, `0x0f`, `0x10`, and `0x21` call `object 1 + 0x17040` with the signed short at the start of the spell row, then `object 1 + 0xf4e0` with that amount and `0x27`. The other ids branch:

```
0x15: object 1 + 0x1d550(object 2 + 0x437c * 24, object 2 + 0x4380 * 24)
      the first target's tile becomes those two globals
      the clip plays again
      # the globals are the confirmed aim, in Turns
      # object 1 + 0x1d550 slides the cursor to that pixel first
0x16: clear bit 0x80 of +5 on each target
0x18: if +0x25, +0x26, or +0x27 is nonzero, object 1 + 0xf7a0(target)
      then store 0 in those three bytes
0x11: object 1 + 0xf8e0(count, targets, 0x2b) twice
      a 0 from object 1 + 0x18f40(0x11) calls object 1 + 0xf660
0x12, 0x13: the same test with that id, without object 1 + 0xf8e0
0x14: for kind in 0, 1, 2:
          if object 1 + 0x18f40(kind) != 0:
              object 1 + 0xfbd0(target, one of the three dwords at object 1 + 0x17638)
              object 1 + 0x14d40(target)
          object 1 + 0xf310()
other: amount = object 1 + 0x182f0(caster, target, id)    # object 1 + 0x18e1f
       0 calls object 1 + 0xf660
       any other amount calls object 1 + 0xf4e0(amount, 0, target)
       id 0x0d also calls object 1 + 0x18eb0
```

`object 1 + 0x1d550(x, y)` slides the cursor pixel, `object 2 + 0x9cd4` and `object 2 + 0x9ccc`, toward that point. A zero delta on both axes returns. The step count is the larger absolute delta divided by 24, and a count of 0 is not guarded. The step on the longer axis is that delta divided by the count, so a remainder shorter than the count is dropped. The shorter axis spreads its remainder across the steps. After each step the camera follows when the cursor is closer than 24 pixels to the window edge or farther than `0xd8` across or `0x90` down. The camera is clamped to the map: x at `width * 24 - 0x138`, y at `height * 24 - 0xc0`, and neither below 0. The width and height are the shorts at `object 2 + 0x144`. A camera move redraws, and so does a step while `object 2 + 0x9cd0` is not 0. The item give calls the same slide to put the cursor back, in [Turns](turns.md).

`object 1 + 0x174b0` fills that list. It copies the three bytes at `+0x31` when flag bit 0 is clear, `+0x40` is below 1, and the first of those bytes is 2, 3, 4, or 5. `object 1 + 0x16150`, used after a swing, copies a first byte other than `0xff` and does not require that range.

`object 1 + 0x17150` uses the stored item slot. Range byte `+0x10` below `0x10` lists targets from the stand tile with byte `+0x12`. At or above `0x10` the list is the line, called at `object 1 + 0x17239`. It faces the first listed id, fades the palette from white back to the installed colors, and moves the cursor `range - 0x10` tiles from the camera tile toward the stand tile, clamped to the map. `object 1 + 0x16270` then applies the item. The kind is byte `+0x0d` of the record, and the short at `+0x0e` is the amount passed to the helper. The experience term is cleared, and the death spin runs. `object 1 + 0x17150` returns 0, so a script that called it continues.

| Kind | What `object 1 + 0x16270` does |
| --- | --- |
| `0x01`, `0x07` | Play `EMg00.saf` and subtract from each target's `+0x40`. `0x01` then removes the pair. |
| `0x02`, `0x08` | The same with `EMg05.saf`. `0x02` removes the pair. |
| `0x03`, `0x09` | The same with `EMg08.saf`. `0x03` removes the pair. |
| `0x04`, `0x0a` | Play `EarQu.wav`, shake the camera for 25 frames, then subtract from `+0x40`. `0x04` removes the pair. |
| `0x0b`, `0x20` | Play `Posion.saf` and add to each target's `+0x40`. `0x0b` removes the pair. |
| `0x0c` | Play `CureMP.saf`. A target whose `+0x46` is 0 queues four rising digits when its tile is on screen. Any other target adds to `+0x44`, capped at `+0x46`. The pair is removed. |
| `0x0f` | Play `Cure.saf` and add 15 to the first target's `+0x42`. The pair is removed. |
| `0x10` | The same for `+0x46`. |
| `0x11`, `0x12`, `0x13` | Play `Cure.saf` and add 7 to `+0x37`, `+0x39`, or `+0x3e`, then rebuild the combat words. The pair is removed. |
| `0x14` | Play `Cure.saf` and add 1 to `+0x3b`. The pair is removed. |
| `0x16`, `0x18` | Clear `+0x25` or `+0x26`, play `Cure.saf`, and call `object 1 + 0xf8e0` with `0xff`. The pair is removed. |
| `0x1e` | Subtract from each target's `+0x40`. The pair stays. |
| `0x21` | When the first target's character id is 9, add 30 to `+0x37` and `+0x39`, add 1 to `+0x3b`, call `object 1 + 0x18280` with `0x1d`, and remove the pair. Any other character only shows text `0x21d`. |
| `0x22` | Character 9 gains 100 on `+0x42` and the pair is removed. Any other character shows text `0x21d`. |
| `0x23` | When byte `+8` is 8 and `object 1 + 0x24290` finds id `0xa3`, that pair and the used index are removed and id `0xbe` is given. Otherwise text `0x220` or `0x21d` is shown. |

## Effect ids

The names in the two tables below are estimates, inferred from the effect. They are a list to correct. The game's own label for an item is interface string `id + 0xc9`, and for a spell it is interface string `id + 0x1be`, in [Text](text.md). Those strings are not copied here.

A spell's effect is the id. `MagicDat.dat` supplies the power, the chance, the step budget, the area, the cost taken from `+0x44`, and the side. A positive power is magic damage, scaled by the target's spell percent. A negative power is damage from the caster's attack. Ids `0x0e`, `0x0f`, `0x10`, and `0x21` add the power to hit points instead. The branches are the spell player above.

| Id | Estimated name | Effect |
| --- | --- | --- |
| 0 | Fire | Damage 70. Cost 7. |
| 1 | Raging fire | Damage 150. Cost 15. |
| 2 | Hellfire | Damage 310. Cost 35. |
| 3 | Light arrow | Damage 300. Cost 20. |
| 4 | Holy pillar | Damage 600. Cost 40. |
| 5 | Thunder | Damage 50. Cost 8. |
| 6 | Thunderbolt | Damage 110. Cost 15. |
| 7 | Thunder strike | Damage 250. Cost 32. |
| 8 | Ice burst | Damage 60. Cost 10. |
| 9 | Deep ice | Damage 130. Cost 20. |
| 10 | Fissure | Damage 150, and the screen shakes. Skips the classes in `object 1 + 0x2550`. Cost 45. |
| 11 | Cataclysm | Damage 350, and the screen shakes. Same skip. Cost 95. |
| 12 | Gravity bolt | Damage 350. Cost 35. |
| 13 | Necro array | Damage 500. A hit also rolls the poison, freeze, and silence counts. Cost 100. |
| 14 | Restore | Heals 70. Cost 4. Side byte 1. |
| 15 | Healing wind | Heals 200. Cost 10. Side byte 1. |
| 16 | Healing spring | Heals 500. Cost 25. Side byte 1. |
| 17 | Silence | May set `+0x27` for 2 or 3 phases, when that byte is still 0. Cost 25. |
| 18 | Poison | May set `+0x25` for 2 or 3 phases, when that byte is still 0. Cost 10. |
| 19 | Paralyze | May set `+0x26` for 2 or 3 phases, when that byte is still 0. Cost 20. |
| 20 | Blessing | May set `+0x22`, `+0x23`, and `+0x24`, each for 2 or 3 phases. Those three writes read magic row 20, which is this row, so the chance is 100. Cost 50. Side byte 1. |
| 21 | Teleport | Moves the first target onto the confirmed aim. Cost 50. Side byte 1. |
| 22 | Refresh | Clears the acted flag, bit `0x80` of byte `+5`, so the target can be ordered again. Cost 40. Side byte 3. |
| 23 | Death curse | Damage 9999, chance 60. Cost 100. |
| 24 | Cure ailments | Clears `+0x25`, `+0x26`, and `+0x27`. Cost 30. Side byte 1. |
| 25 | Dragon blaze | Attack-scaled damage, power 160. The caster can step 23. Cost 65. |
| 26 | Power impact | Attack-scaled damage, power 160. The caster can step 23. Cost 50. |
| 27 | Diamond cut | Attack-scaled damage, power 200. Step budget 1. Cost 30. |
| 28 | Fire break | Attack-scaled damage, power 160. Cost 65. |
| 29 | God cannon | Attack-scaled damage, power 120. Area byte 3. Cost 75. |
| 30 | Meteor arrow | Attack-scaled damage, power 120. Cost 40. |
| 31 | Spirit shot | Attack-scaled damage, power 140. The caster can step 20. Cost 35. |
| 32 | Judgment bolt | Damage 520. Cost 70. |
| 33 | Requiem | Heals 800. Cost 55. Side byte 1. |
| 34 | Gravity well | Damage 1000. Cost 80. |
| 35 | Holy dragon slash | Attack-scaled damage, power 250. The caster can step 31. Cost 100. |
| 36 | Flame dragon | Damage 700. Cost 60. |
| 37 | Ice missile | Damage 270. Cost 35. |
| 38 | Absolute zero | Damage 700. Cost 65. |
| 39 | Advent | Damage 1400. Cost 130. |

An item's use is `Item.kind`, byte `+0x0d`. The amount is the short at `+0x0e`. Kinds `0x01` through `0x04`, and kind `0x0b`, are consumed. Kinds `0x07` through `0x0a` play the same four clips and stay in the inventory, and kind `0x20` is the heal that stays. `Item.swing`, byte `+9`, is a separate effect on the attack: 1 may freeze, 2 plays a second swing, 3 adds to the crit roll, and 4 may poison. A row whose kind is 0 and whose swing is 0 only changes the equipped stats, and it is left out.

`object 1 + 0x16270` has no branch for kind `0x05`, `0x06`, `0x0d`, or `0x1b`. Those four rows are listed with the effect left open.

| Id | Estimated name | Effect |
| --- | --- | --- |
| 9 | Thunder sword | Lightning damage 130. Kept. |
| 10 | Ice sword | Ice damage 150. Kept. |
| 11 | Holy-fire sword | Fire damage 200. Kept. |
| 12 | Earth sword | Quake damage 400. Kept. |
| 14 | Spirit sword | Kind `0x0d`, amount 300. No branch. |
| 18 | Poison claw | A hit may poison. |
| 28 | Goddess staff | Heals 400. Kept. |
| 34 | Silver spear | Ice damage 140. Kept. |
| 35 | Thunder spear | Lightning damage 100. Kept. |
| 36 | Holy-light spear | Heals 200, and a hit adds to the crit roll. Kept. |
| 38 | Gem lance | A hit plays a second swing. |
| 40 | Aurora spear | Heals 200, and a hit adds to the crit roll. Kept. |
| 42 | Holy spear | A hit adds to the crit roll. |
| 47 | Magic staff | Fire damage 30. Kept. |
| 49 | Dark staff | A hit may poison. |
| 50 | Sun staff | Fire damage 80. Kept. |
| 51 | Light staff | Heals 80. Kept. |
| 52 | Angel staff | Heals 120. Kept. |
| 53 | Merlin's staff | Fire damage 150. Kept. |
| 54 | Dragon staff | Fire damage 200. Kept. |
| 55 | Diamond staff | Ice damage 200. Kept. |
| 60 | Poison ring | A hit may poison. |
| 62 | Curse ring | A hit may freeze. |
| 67 | Seal glove | Kind `0x1b`, amount 80. No branch. |
| 68 | Elusive glove | A hit adds to the crit roll. |
| 71 | Snipe bow | A hit adds to the crit roll. |
| 74 | Wind bow | Heals 200, and a hit adds to the crit roll. Kept. |
| 75 | Demon blade | A hit may freeze. |
| 78 | Iron shot | A hit adds to the crit roll. |
| 79 | Ballista | A hit plays a second swing. |
| 80 | Vulcan | A hit plays a second swing. |
| 88 | Named fire sword | Fire damage 100. Kept. |
| 90 | Named lightning sword | Lightning damage 100, and a hit adds to the crit roll. Kept. |
| 95 | Spirit strike | A hit may freeze. |
| 98 | Flame-dragon sword | Fire damage 300. Kept. |
| 99 | Light cannon | Damage 9999. The pair stays. Range byte 30. |
| 160 | Scorching sword | Fire damage 200. Kept. |
| 161 | Firelight sword | Fire damage 300, and a hit adds to the crit roll. Kept. |
| 162 | True flame-dragon sword | Fire damage 500, and a hit adds to the crit roll. Kept. |
| 164 | Fortify kit | On character 9: attack base and defense base gain 30, move gains 1, and spell 29 is learned. Consumed. Any other character shows text and is unchanged. |
| 165 | Demon blade, lesser | A hit may freeze. |
| 166 | Demon blade, middle | A hit may freeze. |
| 167 | Demon blade, greater | A hit may freeze. |
| 168 | Royal bow | Heals 120, and a hit plays a second swing. Kept. |
| 170 | Venom claw | A hit may poison. |
| 171 | Familiar | A hit may freeze. |
| 172 | Ancient cannon | A hit adds to the crit roll. |
| 173 | Vitality kit | On character 9: maximum hit points gain 100. Consumed. Any other character shows text and is unchanged. |
| 177 | Keepsake ring | A hit adds to the crit roll. |
| 178 | Hell bow | A hit may poison. |
| 180 | Herb | Heals 50. Consumed. |
| 181 | Tonic | Heals 100. Consumed. |
| 182 | Regen draught | Heals 250. Consumed. |
| 183 | Magic herb | Restores 40 of the second pool. Consumed. |
| 184 | Magic water | Restores 100 of the second pool. Consumed. |
| 185 | Crystal grain | Restores 250 of the second pool. Consumed. |
| 187 | High-energy device | When byte `+8` is 8 and the unit also carries item 163, both are removed and item 190 is given. Otherwise text, and nothing is removed. |
| 190 | High-energy cannon | Fire damage 400, and a hit adds to the crit roll. Kept. Range byte 22. |
| 191 | Iron-cutting sword, lesser | A hit adds to the crit roll. |
| 192 | Iron-cutting sword, middle | A hit adds to the crit roll. |
| 193 | Iron-cutting sword, greater | A hit adds to the crit roll. |
| 194 | Holy water | Heals 1000. Consumed. |
| 195 | Fire bead | Fire damage 100. Consumed. |
| 196 | Thunder bead | Lightning damage 100. Consumed. |
| 197 | Ice bead | Ice damage 100. Consumed. |
| 198 | Earth bead | Quake damage 100. Consumed. |
| 199 | Flame | Damage 300. The pair stays. Range byte 30. |
| 200 | Fire gem | Fire damage 150. Consumed. |
| 201 | Thunder gem | Lightning damage 150. Consumed. |
| 202 | Ice gem | Ice damage 150. Consumed. |
| 203 | Earth gem | Quake damage 150. Consumed. |
| 204 | Blank | Kind `0x05`, amount 150. The interface string is empty. No branch. |
| 205 | Fire crystal | Fire damage 200. Consumed. |
| 206 | Thunder crystal | Lightning damage 200. Consumed. |
| 207 | Ice crystal | Ice damage 200. Consumed. |
| 208 | Light crystal | Kind `0x06`, amount 200. No branch. |
| 210 | Fire stone | Fire damage 400. Consumed. |
| 211 | Thunder stone | Lightning damage 400. Consumed. |
| 212 | Ice stone | Ice damage 400. Consumed. |
| 213 | Sky gem | Kind `0x06`, amount 250. No branch. |
| 214 | Life fruit | Maximum hit points gain 15. Consumed. |
| 215 | Magic crystal | Maximum of the second pool gains 15. Consumed. |
| 216 | Strength draught | Attack base gains 7, then the combat words are rebuilt. Consumed. |
| 217 | Endurance draught | Defense base gains 7, then the combat words are rebuilt. Consumed. |
| 218 | Hit draught | Hit base gains 7, then the combat words are rebuilt. Consumed. |
| 221 | Wind feather | Move gains 1. Consumed. |
| 222 | Antidote | Clears `+0x25`. Consumed. |
| 223 | Freeze cure | Clears `+0x26`. Consumed. |

`object 1 + 0x16200` walks the targets and subtracts. `object 1 + 0x16fa0` plays `Posion.saf` and adds. Both draw the number that the helper returns, then call `object 1 + 0xf310`. The arithmetic is the same shape in `object 1 + 0x18430` (subtract from `+0x40`), `object 1 + 0x17040` (add to `+0x40`, capped at `+0x42`), and `object 1 + 0x17570` (add to `+0x44`, capped at `+0x46`). `rand` is `object 1 + 0x32a68`. It calls `object 1 + 0x32a62`, which returns the dword at `object 2 + 0x39c`. The call stores `seed * 0x41c64e6d + 0x3039` back into that dword and returns bits 16 through 30, so the value is 0 through `0x7fff`. A null pointer returns 0. The dword in the image is 1. `object 1 + 0x32a8a` stores its argument into the same dword. No function was created there, and no direct call of it was found. The timer tick is `object 1 + 0x20520`, in [Session](session.md). Disassembly of that body: it increments `object 2 + 0x9d64` and calls `rand` once, and the return value is discarded. That is the only call on the tick. The timer is started in startup, before the title, so the seed at the first command is the image seed advanced once for each tick that has fired. How many ticks that is depends on the title and the opener, and that count is not in the program. A roll is not fixed by the battle. The same command after a longer title, or a longer chapter card, draws a later value. A remake that seeds again at the first command will not match these rolls. Integer division is toward zero.

```
spread = amount * 9 / 10 + (rand % 100) * amount / 1000
```

The drawn number is `spread`. A cap or a floor can move the pool by less than that. `object 1 + 0x18430` writes `max(0, +0x40 - spread)`. When the target's side byte is 0 it adds to the experience term. The row is `object 1 + 0x8b00(character - 0x3c)`, and the added term is byte 9 of that row times `+0x21`. While the pool stays above 0, that term is multiplied by `spread / +0x42`.

`object 1 + 0x17040` writes `min(+0x42, +0x40 + spread)`. When the character id is below `0x3c` it adds to the experience term. The scale starts at `+0x21` and gains `0x1e` when the character id is above `0x0e` and below `0x22`. The added term is `scale * 0x19 * written / +0x42`, where `written` is the amount the pool actually rose.

`object 1 + 0xf660`, `object 1 + 0xf4e0`, `object 1 + 0xf7a0`, and `object 1 + 0xfbd0` do not change a pool. Each one runs only when the unit's tile x is the camera tile through 12 tiles to the right, and y is one tile above the camera through 8 below. Inside that window they append entries at `object 2 + 0x4378`. The frame byte goes to `object 2 + 0x4120`, the unit id to `object 2 + 0x41e8`, and a picture byte to `object 2 + 0x42b0`.

`object 1 + 0xf660` appends four. The frames are 1, 8, 13, and 19. The picture bytes, at `object 1 + 0xc2a2`, are `0x34`, `0x35`, `0x36`, and `0x36`. `object 1 + 0xf7a0` uses the same frames and the next four bytes, `0x37`, `0x38`, `0x39`, and `0x3a`, at `object 1 + 0xc2a6`. `object 1 + 0xf4e0(amount, base, id)` formats the amount with `%d` at `object 2 + 0x17bc` into a buffer that starts as four spaces. It appends four entries whose frames are 2, 8, 14, and 20. The digits sit in the rightmost slots. A slot with no digit is stored as `0xff`, and a digit slot is stored as `base + digit`. The damage call passes base 0. The heal call passes `0x27`. `object 1 + 0xfbd0(id, bytes)` walks four bytes. A byte that is not 0 is stored at that byte's own index, with the same frames as `object 1 + 0xf660` and that byte as the picture. The count advances by how many of the four were not 0. Spell id `0x14` passes one of the three dwords at `object 1 + 0x17638`. Their bytes are `3b 3c 3c 00`, `3d 3e 3f 00`, and `3d 3e 40 00`. The last byte is 0, so three entries are written in a row and the count advances by 3.

## The number

`rand` is `object 1 + 0x32a68`. The arithmetic below is `object 1 + 0x9f60` on the clip path and `object 1 + 0xc4f0` on the immediate path. The two bodies match. `object 1 + 0x9f60` does not write the pool. It returns six dwords. Dword 0 is 1, and a landed roll stores 0. Dword 1 is 1 when defense was halved. Dword 5 is the damage. The clip player spreads dword 5 across the hit frames. A miss leaves dword 5 at 0, so the pool write subtracts nothing.

`object 1 + 0x2550` returns 1 when the class byte is `0x16`, `0x17`, `0x18`, `0x1f`, or `0x25`. That fighter skips the terrain percent. The status write for weapon kinds 1 and 4 asks `object 1 + 0x19050`. It returns 1, and the status is skipped, when the class is `0x19`, `0x21`, `0x22`, `0x24`, `0x25`, or `0x26`, or the character id is from `0x3c` through `0x44`. Kind 4 writes `+0x25` and kind 1 writes `+0x26`. A spell applies the same kind of count through `object 1 + 0x18f40`. The six countdowns, and which spell and item kinds write them, are in [Units](units.md).

```
attack  = attacker[+0x48]
defense = defender[+0x4a]
hp, max  = defender[+0x40], defender[+0x42]
hit      = attacker[+0x4c] - defender[+0x4e]
crit     = class_row[8]                 # ProMap.dat row for attacker[+0x20]

if object 1 + 0x2550(attacker) == 0:
    attack  += attack  * attack_percent[terrain] / 100
if object 1 + 0x2550(defender) == 0:
    defense += defense * defense_percent[terrain] / 100

if kind == 3: crit += arg
if kind == 4 and rand % 100 < arg and object 1 + 0x19050(defender) == 0:
    defender[+0x25] = rand % 4 + 2
if kind == 1 and rand % 100 < arg and object 1 + 0x19050(defender) == 0:
    defender[+0x26] = rand % 2 + 2

landed = rand % 100 < hit
if landed:
    if rand % 100 < crit:
        defense = defense / 2
        crit_flag = 1
    damage = (attack - defense) * 9 / 10
    if damage < 0: damage = 0
    if damage / 9 != 0: damage += rand % (damage / 9)
```

Integer division is toward zero. The terrain percents are in [Map](map.md).

On the clip path the experience term is written only when the attacker's side byte is `2` and the defender's side byte is `0`:

```
row = object 1 + 0x8b00(defender[+7] - 0x3c)
scale = attacker[+0x21]
if attacker[+7] > 10: scale += 0x1e
gain = defender[+0x21] * byte(row + 9) / scale
if hp_after != 0: gain = gain * damage / max
object 2 + 0x9cec = gain
```

The immediate path uses a different condition, a side-`2` attacker and a defender whose character id is above `0x3b`, and it writes the same shape of term. Inferred: the term is experience, because `object 1 + 0xdd00` adds it to byte `+0x3c` and raises `+0x21` when that byte crosses 100.

`object 1 + 0x96b0` rolls `rand % 100 < 3` twice. Either success, or weapon byte `+9 == 2`, sets the swing count to 2. The count is decremented before each swing, so the common case plays once. A pool that reaches 0 cancels the swing that would have followed. The immediate path's second pass is the one already described for `object 1 + 0xc370`.

Hit frames apply the damage, from `object 1 + 0x96b0`. `start` is the defender's pool at the beginning of that swing. `n` counts hit frames as they are shown. `hits` is how many frames in the clip have byte `+5` set, or 1 if the clip has none.

```
on the first tick of a hit frame:
    n += 1
    hp = start - (n * damage) / hits
    if hp < 0: hp = 0
    defender[+0x40] = hp
```

The function returns that `hp`. The caller treats a nonzero return as "the defender can still answer." A counterattack is a second call of `object 1 + 0x96b0` with the two units swapped, and only when `object 1 + 0x37e0` returned 1.

## After the pools change

Both callers then do the same three steps, in a different order. The menu passes the attacker. `object 1 + 0x2e50` passes the defender.

```
records = object 1 + 0x16150()     # every visible unit whose pool is below 1
object 1 + 0xd690()               # spin, hide, play Explo.Saf on the map

# command menu, the unit passed through is the attacker
object 2 + 0x9cec = object 2 + 0x9cec * 15 / 10
object 1 + 0xdd00(attacker)
object 1 + 0xd960(attacker, records)

# phase walker, the unit passed through is the defender
object 1 + 0xd960(defender, records)
object 2 + 0x9cec = object 2 + 0x9cec * 15 / 10
object 1 + 0xdd00(defender)
```

`object 1 + 0xd690` collects units whose flag bit 0 is clear and whose word at `+0x40` is 0. For 13 steps it sets every such unit's facing to `step % 4` and redraws the map, so the sprite turns in place. It then stores `1` in byte `+5`, which hides the sprite. If the list was not empty it plays every frame of `Explo.Saf` on the map buffer, once per corpse, at that unit's tile with y shifted up by 6. The visible copy is the map window, buffer+`0x21d8`. Only the first corpse is blitted with the sample flag set, so only that one starts the frame's sample. There is no separate death clip on the fight screen. The fight has already returned to the map before this runs.

`object 1 + 0x16150` runs before that hide. It copies the three bytes at `+0x31` from each still-visible unit whose pool is below 1 and whose first byte is not `0xff`. `object 1 + 0xd960` walks the copies. The first byte selects the step, and the next two are read as a short:

```
0: if the unit passed in is not side 2, or object 1 + 0x9b0 is nonzero, return.
   Otherwise show text 0x1e6, store short + 0xc9 in object 2 + 0x4030, and call
   object 1 + 0x15cf0(unit, short). A result of -1 shows text 0x1e7 and then either
   object 1 + 0x15990 or text 0x1e8.
1: same side test. Show text 0x1e9 and add the short to object 2 + 0x43b8.
2: call (&object 2 + 0x1c4)[short](unit).
above 2: if the short is not 0xff and not -1, show that short as a text id.
   4 then stores 2 in the outcome dword. 5 stores 1.
```

`object 1 + 0x15cf0` is the give in [Units](units.md). `object 1 + 0x15990` is the carried-item pick in [Turns](turns.md). Outcome `1` and `2` are the session's game-over and scenario-end paths, in [Session](session.md).

`object 1 + 0xdd00` returns immediately when the term is 0, or when `object 1 + 0x9b0` is nonzero. Character id `9` also returns at level `0x63`. Any other character returns at level `0x28`. Otherwise the term is capped at 99, added to byte `+0x3c`, and a number is drawn rising off the unit's tile for 15 map frames. If the sum passes 99, `Levup.wav` is started, `+0x21` increases by 1, the sum drops by 100, and a picture from `object 2 + 0x43a0` is held over the map until a key below `0x80` or 250 frames. The new level is capped again: character `9` at 99, anything else at `0x28`, and the remainder byte is cleared when a cap hits. One crossing subtracts 100 once, so one fight raises the level by at most 1.

The row is `object 1 + 0x8ad0` of the character id. `object 1 + 0xe340` adds one rolled amount to each of five words. The pairs are bytes 0, 2, 4, 6, and 8 of that row, added to `+0x37`, `+0x39`, `+0x3e`, `+0x42`, and `+0x46`. The current pools at `+0x40` and `+0x44` are not raised with the maximums. `object 1 + 0x14d40` then rebuilds the combat words. `FriLevUp.dat` byte 10, unless it is `0xff`, selects a 12-byte row of `GetMgTab.dat` through `object 1 + 0x8bf0`. The loop at `object 1 + 0xe020` walks six pairs. When the first byte equals unit `+0x21`, the second byte is passed to `object 1 + 0x18280`, which sets the learned-id bit in [Units](units.md). The same call with id `0x1d` is item kind `0x21`. Ending 0 calls it as `object 1 + 0x18280(0, 0)`, in [Session](session.md).

```
lo = pair[0]
span = pair[1] - lo          # unsigned bytes, so a lower second byte wraps
added = lo if span == 0 else lo + rand % span
word = word + added
```

`rand` is `object 1 + 0x32a68`. The added amount is stored at `object 2 + 0x4038` and passed to `object 1 + 0x7520` with pitch `0xa4` and width 0. The card pixels and the 6×8 split are in [Pictures](pictures.md).
