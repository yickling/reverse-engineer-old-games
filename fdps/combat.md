# Combat numbers

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. How the fight screen is drawn is in [Pictures](pictures.md). The unit words are in [Units](units.md).

## From the map to the fight

Two callers reach the same clip player.

The command menu is `FUN_00015cf0`, opened when a move ends on the unit's current tile. Slot 0 is the attack. It reads the weapon with `FUN_00025110(unit, 0)`, the first equipped pair whose type is from 1 through `0x15`, then `FUN_00018b30`. Weapon bytes `+0xb` and `+0xc` go to `FUN_00011e50` as the range, with side filter 0, so the list is visible units whose side byte is `0` and whose occupancy byte is not `0xff`.

`FUN_00011e50` marks that occupancy grid, then `FUN_0002b280` lets the cursor move a tile at a time. `Z` (`0x2c`) and keypad 5 (`0x4c`) step through the list and center on that unit. Confirm (`0x39` or `0x1c`) accepts when `FUN_0002b790` stored an occupancy byte other than `0xff` and `FUN_000109f0` finds a side-`0` unit on that tile. The menu sets `DAT_00069cd0` to 1 before the picker, and the distance test is strict less-than that value, so the unit has to be on the cursor tile. Escape (`0x01`) or delete (`0x53`) returns −1 and the menu stays up. A chosen target is faced with `FUN_0001c2b0`, then `FUN_00018d50` plays the clips. The menu does not read `DAT_00060010`. It always plays the screen.

The phase walker is `FUN_00010010`, called for side `1` and then side `0` from `FUN_0001e3c0`. Which script runs is in [Turns](turns.md). `FUN_00012c10` fills the three scores below and returns 0 when all three are below 6. Otherwise the largest score wins:

```
swing = DAT_00063f78    # FUN_00012230
spell = DAT_00063f88    # FUN_00013420
item  = DAT_00063f8c    # FUN_00013040
prefer_swing = bit 0x40 of unit[+0x34]

if swing > spell and swing > item: swing
else if swing == spell and item < spell:
    if spell_id < 0x12:
        swing when the spell row's first short is below attack - defense
        else cast
    else if prefer_swing: swing
    else cast
else if swing == item and spell < item:
    item action when prefer_swing is clear, else swing
else if swing < spell and item <= spell: cast
else if swing < item and spell < item: item action
```

`attack` and `defense` there are the attacker's `+0x48` and the defender stored by the swing scorer, its `+0x4a`. The spell id is `DAT_00063f90`, and its row is `FUN_00018bc0`. A three-way tie at 6 or above matches none of those tests: the function still returns 1, and it does not call an action. The swing is `FUN_00012e50`. The cast is `FUN_00013c90` and the item action is `FUN_00027150`, both below. `FUN_00012e50` is the swing:

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

`DAT_00060010` is also read from `0x13d6d`, `0x15268`, `0x18411`, `0x184ad`, `0x2414e`, `0x24363`, and `0x245af`. Which of those stores it was not separated from the reads.

The walk in `FUN_000119e0` flood-fills with the attacker's move budget. Each path byte is one tile: `0` +Y, `1` −X, `2` −Y, anything else +X. `FUN_0002d060` plays a tile as six redraws. `FUN_0002d0f0` (the +Y step; the other three facings are the same shape) sets facing, then writes sub-tile byte `+4` from 1 through 6 and adds 4 to the camera and the cursor on each redraw. Six steps of 4 pixels is one 24-pixel tile. A key byte of `0x02` or `0x03` skips the intermediate redraws. After the last step the tile coordinate increments and `+4` returns to 0.

Facing, from `FUN_0001c2b0`, compares absolute dx with absolute dy. The larger axis wins. Defender to the left is facing 1, to the right is 3, above is 2, below is 0.

Range marking, from `FUN_00011e50`. `+0xc` below `0x10` rebuilds the grid with the class-0 move row, then if `+0xb` is nonzero every tile whose Manhattan distance from the attacker is below `+0xb` is set to `0xff`. `+0xc` at or above `0x10` instead writes `0` along the attacker's row and column out to `+0xc - 0x10`. Tiles left at `0xff` are the ones confirm rejects. `FUN_0002b790` stores that same occupancy byte at `DAT_00069d0c`. The counter test is a third use of `+0xb`: `FUN_000137e0` returns 1 when the defender's `+0x26` is 0, the two units are one tile apart, and `+0xb` is 1.

## The three scores

Each scorer writes 0, then raises its global only when it finds a candidate. All three return 0. The numbers they store are bands, not the damage formula.

`FUN_00012230` is the swing. It reads the weapon through `FUN_00025110(unit, 0)` and `FUN_00018b30`, flood-fills with budget `+0x3b` on `FUN_00018b60(class + 1)`, and asks `FUN_00011da0` for the reachable tiles. From each tile, `FUN_00011e50` lists targets using weapon bytes `+0xb` and `+0xc`. For a target the band is 0 when `attack - defense` is below 3, else 8. When that margin is greater than the target's `+0x40`, the margin is doubled and the band becomes `0x12`. `FUN_000125c0` returns 1 only when the attacker's `+0x26` is 0, the two tiles are one step apart on a side (`FUN_0003d0d4` is the absolute value, and the two absolutes sum to 1), the weapon-group lookup finds a pair, and that record's byte `+0xb` is below 2. Any other case returns −1. A return of 1 adds the attacker's `+0x4a` minus the target's `+0x48` to the margin. A target whose byte `+8` is 0 multiplies the margin by 3/2. The kept candidate is the highest band, and on a tie the larger margin. It stores the target in `DAT_00063f74` and the stand tile in `DAT_00063f80` and `DAT_00063f84`. `FUN_000118f0` was not decompiled. `FUN_00011da0` returns the tile count; its body was not read.

`FUN_00013420` is the spell. `FUN_00027810` fills the id list, the same call that enables menu slot 1, and byte `+0x27` must be 0. A spell is skipped unless byte `+5` of its `FUN_00018bc0` row is at or below the word at unit `+0x44`. The flood fill uses budget byte `+3` of that row and the class-0 move row. `FUN_00013920` scores the targets on one stand tile, and the kept candidate is the higher score, then the larger first short of the row. The stand tile is `DAT_00063f9c` and `DAT_00063fa0`, and the spell id is `DAT_00063f90`.

`FUN_00013920` sums a per-target band. Ids `0x0e`, `0x0f`, `0x10`, and `0x21` score the target's pool against its `+0x42`: 8 when the pool is below a third, 3 when it is below a half, otherwise 0, and bit 0 of `+0x34` doubles that. Id `0x11` adds 6 for each target that still has a spell list and whose `+0x27` is 0. Id `0x18` adds 6 for each target whose `+0x25`, `+0x26`, or `+0x27` is nonzero. Id `0x12` adds 10 for each target whose `+0x25` is 0. Id `0x13` does the same for `+0x26`. Id `0x14` calls that counter three times, for `+0x22`, `+0x23`, and `+0x24`, and keeps only the last return, so the score is 4 per target whose `+0x24` is 0. The counter is `FUN_00013c20`. Every other id adds 8, or `0x18` when the pool is below the row's first short. Ids `0x0a` and `0x0b` skip a target that `FUN_00012550` accepts. A target whose byte `+8` is 0 replaces that band with the value `FUN_0003d25c` leaves on the FPU stack. That helper rounds toward zero. The value loaded before the call was not separated.

`FUN_00013040` is the carried item. `FUN_00025210` is the count, the same call that enables menu slot 2. Index `i` reads the id at unit `+0x0b + i * 2` and the record from `FUN_00018b30`. Byte `+0x0d` of that record must be nonzero. Byte `+0x10` below `0x10` lists targets with `FUN_00011e50`; at or above `0x10` it uses `FUN_00013670` with that byte minus `0x10`. `FUN_000132b0` scores the stand tile, and a higher score replaces `DAT_00063f8c`. The stand tile is `DAT_00063f98` and `DAT_00063f94`, and the slot index is `DAT_00063f7c`. `FUN_00013670` was not decompiled.

`FUN_000132b0` returns 0 unless byte `+0x0d` is `0x0b` or `0x1e`. Kind `0x0b` scores each target's pool against its `+0x42`: 8 at or below a third, 3 above a third and at or below a half, otherwise 0. Bit `0x80` of `+0x34` multiplies that by 3. Kind `0x1e` adds `0x12` when the pool is at or below the short at record `+0x0e`, and 8 otherwise.

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
