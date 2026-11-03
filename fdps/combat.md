# Combat numbers

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. How the fight screen is drawn is in [Pictures](pictures.md). The unit words are in [Units](units.md).

## From the map to the fight

Two callers reach the same clip player.

The command menu is `FUN_00015cf0`, opened when a move ends on the unit's current tile. Slot 0 is the attack. It reads the weapon with `FUN_00025110(unit, 0)`, the first equipped pair whose type is from 1 through `0x15`, then `FUN_00018b30`. Weapon bytes `+0xb` and `+0xc` go to `FUN_00011e50` as the range, with side filter 0, so the list is visible units whose side byte is `0` and whose occupancy byte is not `0xff`.

`FUN_00011e50` marks that occupancy grid, then `FUN_0002b280` lets the cursor move a tile at a time. `Z` (`0x2c`) and keypad 5 (`0x4c`) step through the list and center on that unit. Confirm (`0x39` or `0x1c`) accepts when `FUN_0002b790` stored an occupancy byte other than `0xff` and `FUN_000109f0` finds a side-`0` unit on that tile. The menu sets `DAT_00069cd0` to 1 before the picker, and the distance test is strict less-than that value, so the unit has to be on the cursor tile. Escape (`0x01`) or delete (`0x53`) returns −1 and the menu stays up. A chosen target is faced with `FUN_0001c2b0`, then `FUN_00018d50` plays the clips. The menu does not read `DAT_00060010`. It always plays the screen.

The phase walker is `FUN_00010010`, called for side `1` and then side `0` from `FUN_0001e3c0`. Which script runs is in [Turns](turns.md). `FUN_00012c10` fills the three scores below and returns 0 when all three are below 6. Otherwise the largest score wins. The comparison is the last step of the routine at the end of this section. `attack` and `defense` there are the attacker's `+0x48` and the defender stored by the swing scorer, its `+0x4a`. The spell id is `DAT_00063f90`, and its row is `FUN_00018bc0`. A three-way tie at 6 or above matches none of those tests: the function still returns 1, and it does not call an action. The swing is `FUN_00012e50`. The cast is `FUN_00013c90` and the item action is `FUN_00027150`, both below. `FUN_00012e50` is the swing:

```
center the camera on the attacker          # FUN_0002d7e0
walk toward DAT_00063f80, DAT_00063f84     # FUN_000119e0
center on the defender
face the defender                          # FUN_0001c2b0
wait 100                                   # FUN_00043a20
if DAT_00060010 == 0:
    redraw the map and apply the pools in place    # FUN_0001c370
else:
    play the clips                         # FUN_00018d50
```

The settings corner flips `DAT_00060010`, and the save load restores it, both in [Turns](turns.md) and [Save](save.md). It is also touched at `0x13d6d`, `0x15268`, `0x24363`, and `0x245af`. Those four were not separated.

The walk in `FUN_000119e0` flood-fills with the attacker's move budget. Each path byte is one tile: `0` +Y, `1` −X, `2` −Y, anything else +X. `FUN_0002d060` plays a tile as six redraws. `FUN_0002d0f0` (the +Y step; the other three facings are the same shape) sets facing, then writes sub-tile byte `+4` from 1 through 6 and adds 4 to the camera and the cursor on each redraw. Six steps of 4 pixels is one 24-pixel tile. A key byte of `0x02` or `0x03` skips the intermediate redraws. After the last step the tile coordinate increments and `+4` returns to 0.

Facing, from `FUN_0001c2b0`, compares absolute dx with absolute dy. The larger axis wins. Defender to the left is facing 1, to the right is 3, above is 2, below is 0.

Range marking, from `FUN_00011e50(x, y, dest, shape, inner, side)`. The cost byte is the mask: `0xff` is outside, and any other value is inside. `shape` below `0x10` calls `FUN_00010de0` with the class-0 move row, the center, and `shape` as the budget. That fill writes `0` on the origin and does not clear the other tiles, so a caller that wants a fresh mask calls `FUN_00010b20` first. If `inner` is nonzero, every tile whose Manhattan distance from the center is below `inner` is then set back to `0xff`. `shape` at or above `0x10` subtracts `0x10` and writes `0` on the center's row where `|dx|` is at most that radius, and on the center's column where `|dy|` is at most that radius. It does not clear either. A visible unit is listed when its tile's cost byte is not `0xff` and its side matches `side`: `0` keeps side `0`, `1` keeps a side other than `0`, `2` keeps side `1`, and `3` keeps side `2`. The ids are written in unit-index order. A null `dest` only returns the count. Tiles left at `0xff` are the ones confirm rejects. `FUN_0002b790` stores that same occupancy byte at `DAT_00069d0c`. The counter test is a third use of weapon byte `+0xb`: `FUN_000137e0` returns 1 when the defender's `+0x26` is 0, the two units are one tile apart, and `+0xb` is 1.

## The spell area

A spell hits the units standing on the tiles this mask marks. The row is `FUN_00018bc0`. Byte `+4` is the `shape` above. Byte `+3` is a second range, used to choose where the mask is centered. Spells pass `inner` 0, so the flood is not punched back. The step costs of that flood are the class-0 row in [Map](map.md). The cast itself is `FUN_00013c90`: it paints from the stored stand with byte `+4`, copies the ids, then clears the grid.

`FUN_00013420` clears between the two paints. It flood-fills from the caster with budget byte `+3`, copies the reached tiles with `FUN_00011da0`, and calls `FUN_00010b20`. Each of those tiles is then a center: `FUN_00011e50` with `shape` byte `+4` and `inner` 0, then another clear before the next center. The CPU never takes the line below. A shape of `0x10` or more is the plus.

The player's aim, `FUN_00027bf0`, is the other center. Byte `+3` equal to 0 paints byte `+4` from the cursor tile, side filter 0, and does not clear first. Any other byte `+3` first paints that byte from the cursor, with side byte `+6`, and the picker runs. After the picker confirms, the grid is cleared. Byte `+3` of 15 or less then paints byte `+4` from the cursor that was confirmed. Byte `+3` of 16 or more does not paint a second area. It walks a line with `FUN_00013670` and plays `Chess.wav`. The same line is what an item uses when its range byte is `0x10` or higher: `(stand x, stand y, buffer, unit x, unit y, byte +0x10 - 0x10, side)`.

`FUN_00013670(cursor x, cursor y, dest, origin x, origin y, length, side)` does not use the cost grid. The step is one tile on a single axis, from the origin toward the cursor. Equal x steps in y: a smaller cursor y steps toward smaller y, and any other cursor y, including the same tile, steps toward larger y. Any other x steps in x, toward smaller x when the cursor x is smaller, otherwise toward larger x. The origin tile is not tested. Each of the `length` steps moves the cursor pixel by 24, and a step inside the map asks `FUN_0002d830` for the unit under that pixel. Side argument 0 keeps a side other than 0. Any other argument keeps side 0. Flag bit 0 is not tested. The player passes the caster as the origin, the cursor as the aim, length `byte +3 - 0x10`, and side argument 1. The two cursor pixels are saved and restored.

A marked tile is drawn from the section's highlight byte. Highlight 1, every ground plate, recolors the tile in place (expander mode 10). Highlight 0 skips the mask. Highlight 2 blends the tile over the buffer and walks the pulse selector. Which files use which pair, and the reading of them as ground, a farther plate, and a foreground shimmer, are in [Map](map.md). The player's picker runs while the aim mask is still on the grid, so that is the area on screen. The effect list is painted and then cleared by `FUN_00010b20` with no compose between the two calls.

`FUN_0002c430` lays pictures on tiles around the cursor pixel when `DAT_00069cd0` is 1 through 5. That global is the cursor leash: confirm is a strict less-than against it. A spell stores byte `+4` plus 2 there before aiming, and the zero byte-`+3` path then forces it to 1. Value 6 writes cost 0 on the cursor tile and draws nothing. Any other value draws nothing. `FUN_0002c9b0` copies one 24×24 picture from `Cusor.cel`, the file `FUN_00029630` stores at `DAT_000643c8`, when the pixel sits in the camera window. Offsets below are tiles, picture index in parentheses.

```
# FUN_00011e50. Cost 0xff is outside the mask.
# FUN_00010de0 writes 0 on the origin and does not clear.

def paint(x, y, shape, inner):
    if shape < 0x10:
        flood(class_0_move_row, x, y, budget=shape)
        if inner != 0:
            set cost to 0xff where |dx| + |dy| < inner
    else:
        radius = shape - 0x10
        set cost to 0 where the tile shares x or y
            and |dx| <= radius or |dy| <= radius

def line(cursor, origin, length, side):       # FUN_00013670
    if cursor.x == origin.x:
        step = (0, -1) if cursor.y < origin.y else (0, 1)
    else:
        step = (-1, 0) if cursor.x < origin.x else (1, 0)
    tile = origin
    hits = []
    repeat length times:
        tile = tile + step
        if tile is on the map:
            id = unit under that pixel          # FUN_0002d830, or none
            if id exists and (side == 0) == (unit.side != 0):
                hits.append(id)
    return hits

# FUN_0002c430. Pictures, not the hit test.
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

def player_aim(caster):                        # FUN_00027bf0
    leash = spell[+4] + 2                      # DAT_00069cd0
    if spell[+3] == 0:
        leash = 1
        list = paint_and_list(cursor, spell[+4], side=0)
    else:
        list = paint_and_list(cursor, spell[+3], side=spell[+6])
        if the picker confirms:
            clear the grid                        # FUN_00010b20
            if spell[+3] <= 15:
                list = paint_and_list(cursor, spell[+4], side=spell[+6])
            else:
                list = line(cursor, caster.tile, spell[+3] - 0x10, side=1)
    return list

def cpu_spell_area(caster):                    # FUN_00013420
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

`FUN_00012230` is the swing. It reads the weapon through `FUN_00025110(unit, 0)` and `FUN_00018b30`, flood-fills with budget `+0x3b` on `FUN_00018b60(class + 1)`, and asks `FUN_00011da0` for the reachable tiles. `FUN_00011da0` lists every tile whose cost byte is not `0xff`, in row-major order, and returns the count. `FUN_000118f0` writes `0xff` into that byte for the other visible units on one side of the filter. The same two calls choose where a CPU walk stops, in [Turns](turns.md). From each stand tile, `FUN_00011e50` lists targets with `shape` = weapon byte `+0xc`, `inner` = byte `+0xb`, and `side` = 1 when the phase filter is 0, else 0. A phase filter of 0 is the side-`0` walk, so that walk's swing list is every visible unit whose side is not 0. Side `1` passes filter 1, and its swing list is side 0. For a target the band is 0 when `attack - defense` is below 3, else 8. When that margin is greater than the target's `+0x40`, the margin is doubled and the band becomes `0x12`. `FUN_000125c0` returns 1 only when the attacker's `+0x26` is 0, the two tiles are one step apart on a side (`FUN_0003d0d4` is the absolute value, and the two absolutes sum to 1), the weapon-group lookup finds a pair, and that record's byte `+0xb` is below 2. Any other case returns −1. A return of 1 adds the attacker's `+0x4a` minus the target's `+0x48` to the margin. A target whose byte `+8` is 0 multiplies the margin by 3/2. The kept candidate is the highest band, and on a tie the larger margin. An equal band and an equal margin keeps the earlier stand tile, and within a tile the earlier unit index. It stores the target in `DAT_00063f74` and the stand tile in `DAT_00063f80` and `DAT_00063f84`.

`FUN_00013420` is the spell. `FUN_00027810` fills the id list, the same call that enables menu slot 1, and byte `+0x27` must be 0. A spell is skipped unless byte `+5` of its `FUN_00018bc0` row is at or below the word at unit `+0x44`. The flood fill uses budget byte `+3` of that row and the class-0 move row. The reached tiles are copied, the grid is cleared, and each of them is then a center for the area mask in [The spell area](#the-spell-area). `FUN_00011e50` lists targets with `shape` = row byte `+4`, `inner` = 0, and a side taken from row byte `+6`. The grid is cleared again after that list. When the phase filter is 0, byte `+6` equal to 0 becomes list side `1`, and any other value becomes list side `0`. When the phase filter is not 0, byte `+6` is the list side as stored. `FUN_00013920` scores that list, and the kept candidate is the higher score, then the larger first short of the row. An equal score and an equal short keeps the earlier tile. The stand tile is `DAT_00063f9c` and `DAT_00063fa0`, and the spell id is `DAT_00063f90`.

`FUN_00013920` sums a per-target band. Ids `0x0e`, `0x0f`, `0x10`, and `0x21` score the target's pool against its `+0x42`: 8 when the pool is below a third, 3 when it is below a half, otherwise 0, and bit 0 of `+0x34` doubles that. Id `0x11` adds 6 for each target that still has a spell list and whose `+0x27` is 0. Id `0x18` adds 6 for each target whose `+0x25`, `+0x26`, or `+0x27` is nonzero. Id `0x12` adds 10 for each target whose `+0x25` is 0. Id `0x13` does the same for `+0x26`. Id `0x14` calls that counter three times, for `+0x22`, `+0x23`, and `+0x24`, and keeps only the last return, so the score is 4 per target whose `+0x24` is 0. The counter is `FUN_00013c20`. Every other id adds 8, or `0x18` when the pool is below the row's first short. Ids `0x0a` and `0x0b` skip a target that `FUN_00012550` accepts. A target whose byte `+8` is 0 replaces that band with the value `FUN_0003d25c` leaves on the FPU stack. That helper rounds toward zero. The value loaded before the call was not separated.

`FUN_00013040` is the carried item. `FUN_00025210` is the count, the same call that enables menu slot 2. Index `i` reads the id at unit `+0x0b + i * 2` and the record from `FUN_00018b30`. Byte `+0x0d` of that record must be nonzero. The stand tiles come from one `FUN_00011e50` at the unit's own tile whose list is discarded: byte `+0x10` below `0x10` is the `shape` and `inner` is 0, and a byte at or above `0x10` is painted with `shape` 1 and `inner` 1. From each stand tile the target list uses record byte `+0x12` as `shape` and `inner` 0 when byte `+0x10` is below `0x10`. At or above `0x10` the list is the line in [The spell area](#the-spell-area), called as `(stand x, stand y, buffer, unit x, unit y, byte +0x10 - 0x10, side)`. The side is record byte `+0x11`, with the same fold the spell uses: a phase filter of 0 turns byte 0 into list side `1` and any other byte into list side `0`. `FUN_000132b0` scores that list, and a strictly higher score replaces `DAT_00063f8c`. The stand tile is `DAT_00063f98` and `DAT_00063f94`, and the slot index is `DAT_00063f7c`.

`FUN_000132b0` returns 0 unless byte `+0x0d` is `0x0b` or `0x1e`. Kind `0x0b` uses signed division toward zero. A target whose `+0x40` is at or below `+0x42 / 3` adds 8. Above that and at or below `+0x42 / 2` adds 3. Above half adds 0. Bit `0x80` of `+0x34` multiplies that term by 3. Kind `0x1e` adds `0x12` when `+0x40` is at or below the short at record `+0x0e`, and 8 when it is above that short.

## The CPU routine

This is `FUN_00012c10` together with the three scorers. Rows 0, 1, 2, 3, and 5 of the script table call it first. Rows 10 and 11 do not: row 10 takes the item when that score is above 5, then the swing when its score is 6 or more, and otherwise the budget-100 walk. Row 11 is that shape with the spell and `FUN_00013c90` in place of the item. Division is toward zero.

```
# phase is the filter FUN_00010010 was given.
# 0 is the side-0 walk. 1 is the side-1 walk.
# A unit is visible when bit 0 of byte +5 is clear.

def folded_side(phase, byte):
    if phase == 0:
        return 1 if byte == 0 else 0
    return byte

# FUN_00011e50. Writes ids in unit-index order.
# side 0 keeps side 0. side 1 keeps any side other than 0.
# side 2 keeps side 1. side 3 keeps side 2.
def targets(x, y, shape, inner, side):
    paint(x, y, shape, inner)                       # the mask above
    return visible units on a tile whose cost is not 0xff
        and whose side matches `side`

def swing_margin(attacker, target, stand):             # FUN_00012230
    margin = attacker[+0x48] - target[+0x4a]
    band = 0 if margin < 3 else 8
    if target[+0x40] < margin:
        margin = margin * 2
        band = 0x12
    if FUN_000125c0(target, stand) == 1:
        margin = margin + attacker[+0x4a] - target[+0x48]
    if target[+8] == 0:
        margin = (margin * 3) / 2
    return band, margin

def score_swing(unit, phase):                          # FUN_00012230
    best = (0, none)
    weapon = equipped pair of type 1..0x15             # FUN_00025110(unit, 0)
    if weapon is missing:
        return best
    row = Item.dat[weapon]
    stamp(phase)                                       # FUN_00010b90
    fill(ProMap[class + 1], unit.tile, budget = unit[+0x3b])
    punch the other units on the mover's side          # FUN_000118f0
    side = 1 if phase == 0 else 0
    for stand in tiles whose cost is not 0xff:         # FUN_00011da0, row-major
        for target in targets(stand, row[+0xc], row[+0xb], side):
            band, margin = swing_margin(unit, target, stand)
            if band > best.band or (band == best.band and margin > best.margin):
                best = (band, margin, target, stand)
    return best

def spell_band(spell_id, targets):                     # FUN_00013920
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
        total = 10 * count of targets whose +0x25 == 0     # FUN_00013c20
    else if spell_id == 0x13:
        total = 10 * count of targets whose +0x26 == 0
    else if spell_id == 0x14:
        total = 4 * count of targets whose +0x24 == 0
        # the same count for +0x22 and for +0x23 is computed and dropped
    else if spell_id == 0x18:
        total = 6 * count of targets whose +0x25, +0x26, or +0x27 is nonzero
    else:
        for target in targets:
            if spell_id in (0x0a, 0x0b) and FUN_00012550(target) != 0:
                continue
            term = 0x18 if target[+0x40] < row.first_short else 8
            if target[+8] == 0:
                term = trunc(the value loaded before FUN_0003d25c)
                # that load was not separated from the call
            total = total + term
    return total

def score_spell(unit, phase):                          # FUN_00013420
    best = (0, none)
    if unit[+0x27] != 0 or the unit has no spell list:
        return best
    for spell_id in the learned list:                  # FUN_00027810
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

def item_band(record, targets):                        # FUN_000132b0
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

def score_item(unit, phase):                           # FUN_00013040
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
                # that body was not decompiled
            if listed is empty:
                continue
            score = item_band(record, listed)
            if score > best:
                best = (score, slot, stand)
    return best

def choose_action(unit, phase):                        # FUN_00012c10
    swing = score_swing(unit, phase)                   # DAT_00063f78
    spell = score_spell(unit, phase)                   # DAT_00063f88
    item = score_item(unit, phase)                     # DAT_00063f8c
    if swing.band < 6 and spell.score < 6 and item.score < 6:
        return no action
    prefer_swing = bit 0x40 of unit[+0x34]
    defender = the unit id score_swing stored           # DAT_00063f74, unchanged when no swing candidate
    if swing.band > spell.score and swing.band > item.score:
        play the swing                                  # FUN_00012e50
    else if swing.band == spell.score and item.score < spell.score:
        if spell.id < 0x12:
            if MagicDat[spell.id].first_short < unit[+0x48] - defender[+0x4a]:
                play the swing
            else:
                cast                                    # FUN_00013c90
        else if prefer_swing:
            play the swing
        else:
            cast
    else if swing.band == item.score and spell.score < item.score:
        if prefer_swing: play the swing
        else: use the item                              # FUN_00027150
    else if swing.band < spell.score and item.score <= spell.score:
        cast
    else if swing.band < item.score and spell.score < item.score:
        use the item
    # a three-way tie at 6 or above calls none of these
    return acted
```

`FUN_00013c90` casts when the spell band is at least 6. It lists targets from the stored stand tile with range byte `+4` of the spell row, moves the cursor there, waits 200, and plays the clips. `DAT_00060010 == 1` calls `FUN_0001a4a0`, which subtracts the spell row's byte `+5` through `FUN_00028590`. Any other value calls `FUN_000288c0`, which subtracts that byte at `0x28942`. It then runs the death spin and the death-record walk with `DAT_00063f74`, clears the experience term, and returns 1.

`FUN_000274b0` fills that list. It copies the three bytes at `+0x31` when flag bit 0 is clear, `+0x40` is below 1, and the first of those bytes is 2, 3, 4, or 5. `FUN_00026150`, used after a swing, copies a first byte other than `0xff` and does not require that range.

`FUN_00027150` uses the stored item slot. Range byte `+0x10` below `0x10` lists targets from the stand tile with byte `+0x12`. At or above `0x10` it faces the first listed id, fades the palette from white back to the installed colors, and moves the cursor `range - 0x10` tiles from the camera tile toward the stand tile, clamped to the map. `FUN_00026270` then applies the item. The kind is byte `+0x0d` of the record, and the short at `+0x0e` is the amount passed to the helper. The experience term is cleared, and the death spin runs. `FUN_00027150` returns 0, so a script that called it continues.

| Kind | What `FUN_00026270` does |
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
| `0x16`, `0x18` | Clear `+0x25` or `+0x26`, play `Cure.saf`, and call `FUN_0001f8e0` with `0xff`. The pair is removed. |
| `0x1e` | Subtract from each target's `+0x40`. The pair stays. |
| `0x21` | When the first target's character id is 9, add 30 to `+0x37` and `+0x39`, add 1 to `+0x3b`, call `FUN_00028280` with `0x1d`, and remove the pair. Any other character only shows text `0x21d`. |
| `0x22` | Character 9 gains 100 on `+0x42` and the pair is removed. Any other character shows text `0x21d`. |
| `0x23` | When byte `+8` is 8 and `FUN_00034290` finds id `0xa3`, that pair and the used index are removed and id `0xbe` is given. Otherwise text `0x220` or `0x21d` is shown. |

`FUN_00026200` walks the targets and subtracts. `FUN_00026fa0` plays `Posion.saf` and adds. Both draw the number that the helper returns, then call `FUN_0001f310`. The arithmetic is the same shape in `FUN_00028430` (subtract from `+0x40`), `FUN_00027040` (add to `+0x40`, capped at `+0x42`), and `FUN_00027570` (add to `+0x44`, capped at `+0x46`). `rand` is `FUN_00042a68`. Integer division is toward zero.

```
spread = amount * 9 / 10 + (rand % 100) * amount / 1000
```

The drawn number is `spread`. A cap or a floor can move the pool by less than that. `FUN_00028430` writes `max(0, +0x40 - spread)`. When the target's side byte is 0 it adds to the experience term. The row is `FUN_00018b00(character - 0x3c)`, and the added term is byte 9 of that row times `+0x21`. While the pool stays above 0, that term is multiplied by `spread / +0x42`.

`FUN_00027040` writes `min(+0x42, +0x40 + spread)`. When the character id is below `0x3c` it adds to the experience term. The scale starts at `+0x21` and gains `0x1e` when the character id is above `0x0e` and below `0x22`. The added term is `scale * 0x19 * written / +0x42`, where `written` is the amount the pool actually rose.

`FUN_0001f660` does not change a pool. The unit's tile x runs from the camera tile through 12 tiles to the right, and y from one tile above the camera through 8 below. Inside that window it appends four entries and adds 4 to `DAT_00064378`. The frame bytes are 1, 8, 13, and 19. The four bytes copied from `DAT_0001c2a2` were not read.

## The number

`rand` is `FUN_00042a68`. The arithmetic below is `FUN_00019f60` on the clip path and `FUN_0001c4f0` on the immediate path. The two bodies match. `FUN_00019f60` does not write the pool. It returns six dwords. Dword 0 is 1, and a landed roll stores 0. Dword 1 is 1 when defense was halved. Dword 5 is the damage. The clip player spreads dword 5 across the hit frames. A miss leaves dword 5 at 0, so the pool write subtracts nothing.

`FUN_00012550` returns 1 when the class byte is `0x16`, `0x17`, `0x18`, `0x1f`, or `0x25`. That fighter skips the terrain percent. The status write for weapon kinds 1 and 4 asks `FUN_00029050`. It returns 1, and the status is skipped, when the class is `0x19`, `0x21`, `0x22`, `0x24`, `0x25`, or `0x26`, or the character id is from `0x3c` through `0x44`. A spell applies the same kind of count through `FUN_00028f40`, in [Units](units.md).

```
attack  = attacker[+0x48]
defense = defender[+0x4a]
hp, max  = defender[+0x40], defender[+0x42]
hit      = attacker[+0x4c] - defender[+0x4e]
crit     = class_row[8]                 # ProMap.dat row for attacker[+0x20]

if FUN_00012550(attacker) == 0:
    attack  += attack  * attack_percent[terrain] / 100
if FUN_00012550(defender) == 0:
    defense += defense * defense_percent[terrain] / 100

if kind == 3: crit += arg
if kind == 4 and rand % 100 < arg and FUN_00029050(defender) == 0:
    defender[+0x25] = rand % 4 + 2
if kind == 1 and rand % 100 < arg and FUN_00029050(defender) == 0:
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
row = FUN_00018b00(defender[+7] - 0x3c)
scale = attacker[+0x21]
if attacker[+7] > 10: scale += 0x1e
gain = defender[+0x21] * byte(row + 9) / scale
if hp_after != 0: gain = gain * damage / max
DAT_00069cec = gain
```

The immediate path uses a different condition, a side-`2` attacker and a defender whose character id is above `0x3b`, and it writes the same shape of term. Inferred: the term is experience, because `FUN_0001dd00` adds it to byte `+0x3c` and raises `+0x21` when that byte crosses 100.

`FUN_000196b0` rolls `rand % 100 < 3` twice. Either success, or weapon byte `+9 == 2`, sets the swing count to 2. The count is decremented before each swing, so the common case plays once. A pool that reaches 0 cancels the swing that would have followed. The immediate path's second pass is the one already described for `FUN_0001c370`.

Hit frames apply the damage, from `FUN_000196b0`. `start` is the defender's pool at the beginning of that swing. `n` counts hit frames as they are shown. `hits` is how many frames in the clip have byte `+5` set, or 1 if the clip has none.

```
on the first tick of a hit frame:
    n += 1
    hp = start - (n * damage) / hits
    if hp < 0: hp = 0
    defender[+0x40] = hp
```

The function returns that `hp`. The caller treats a nonzero return as "the defender can still answer." A counterattack is a second call of `FUN_000196b0` with the two units swapped, and only when `FUN_000137e0` returned 1.

## After the pools change

Both callers then do the same three steps, in a different order. The menu passes the attacker. `FUN_00012e50` passes the defender.

```
records = FUN_00026150()     # every visible unit whose pool is below 1
FUN_0001d690()               # spin, hide, play Explo.Saf on the map

# command menu, the unit passed through is the attacker
DAT_00069cec = DAT_00069cec * 15 / 10
FUN_0001dd00(attacker)
FUN_0001d960(attacker, records)

# phase walker, the unit passed through is the defender
FUN_0001d960(defender, records)
DAT_00069cec = DAT_00069cec * 15 / 10
FUN_0001dd00(defender)
```

`FUN_0001d690` collects units whose flag bit 0 is clear and whose word at `+0x40` is 0. For 13 steps it sets every such unit's facing to `step % 4` and redraws the map, so the sprite turns in place. It then stores `1` in byte `+5`, which hides the sprite. If the list was not empty it plays every frame of `Explo.Saf` on the map buffer, once per corpse, at that unit's tile with y shifted up by 6. The visible copy is the map window, buffer+`0x21d8`. Only the first corpse is blitted with the sample flag set, so only that one starts the frame's sample. There is no separate death clip on the fight screen. The fight has already returned to the map before this runs.

`FUN_00026150` runs before that hide. It copies the three bytes at `+0x31` from each still-visible unit whose pool is below 1 and whose first byte is not `0xff`. `FUN_0001d960` walks the copies. The first byte selects the step, and the next two are read as a short:

```
0: if the unit passed in is not side 2, or FUN_000109b0 is nonzero, return.
   Otherwise show text 0x1e6, store short + 0xc9 in DAT_00064030, and call
   FUN_00025cf0(unit, short). A result of -1 shows text 0x1e7 and then either
   FUN_00025990 or text 0x1e8.
1: same side test. Show text 0x1e9 and add the short to DAT_000643b8.
2: call (&DAT_000601c4)[short](unit).
above 2: if the short is not 0xff and not -1, show that short as a text id.
   4 then stores 2 in the outcome dword. 5 stores 1.
```

`FUN_00025cf0`, `FUN_00025990`, and the text calls were not followed. Outcome `1` and `2` are the session's game-over and scenario-end paths, in [Session](session.md).

`FUN_0001dd00` returns immediately when the term is 0, or when `FUN_000109b0` is nonzero. Character id `9` also returns at level `0x63`. Any other character returns at level `0x28`. Otherwise the term is capped at 99, added to byte `+0x3c`, and a number is drawn rising off the unit's tile for 15 map frames. If the sum passes 99, `Levup.wav` is started, `+0x21` increases by 1, the sum drops by 100, and a picture from `DAT_000643a0` is held over the map until a key below `0x80` or 250 frames. The new level is capped again: character `9` at 99, anything else at `0x28`, and the remainder byte is cleared when a cap hits. One crossing subtracts 100 once, so one fight raises the level by at most 1.

The row is `FUN_00018ad0` of the character id. `FUN_0001e340` adds one rolled amount to each of five words. The pairs are bytes 0, 2, 4, 6, and 8 of that row, added to `+0x37`, `+0x39`, `+0x3e`, `+0x42`, and `+0x46`. The current pools at `+0x40` and `+0x44` are not raised with the maximums. `FUN_00024d40` then rebuilds the combat words. `FriLevUp.dat` byte 10, unless it is `0xff`, selects a 12-byte row of `GetMgTab.dat` through `FUN_00018bf0`. The loop at `0x1e020` walks six pairs. When the first byte equals unit `+0x21`, the second byte is passed to `FUN_00028280`, which sets the learned-id bit in [Units](units.md). The same call with id `0x1d` is item kind `0x21`. A third call, at `0x3a190`, was not read.

```
lo = pair[0]
span = pair[1] - lo          # unsigned bytes, so a lower second byte wraps
added = lo if span == 0 else lo + rand % span
word = word + added
```

`rand` is `FUN_00042a68`. The added amount is passed to `FUN_00017520` with `0xa4`. That drawer was not decompiled.
