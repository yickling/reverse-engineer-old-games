# Combat numbers

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. How the fight screen is drawn is in [Pictures](pictures.md). The unit words are in [Units](units.md).

## From the map to the fight

Two callers reach the same clip player.

The command menu is `FUN_00015cf0`, opened when a move ends on the unit's current tile. Slot 0 is the attack. It reads the equipped record (`FUN_00025110` slot 0, then `FUN_00018b30`). Weapon bytes `+0xb` and `+0xc` go to `FUN_00011e50` as the range, with side filter 0, so the list is visible units whose side byte is `0` and whose occupancy byte is not `0xff`.

`FUN_00011e50` marks that occupancy grid, then `FUN_0002b280` lets the cursor move a tile at a time. `Z` (`0x2c`) and keypad 5 (`0x4c`) step through the list and center on that unit. Confirm (`0x39` or `0x1c`) accepts when `FUN_0002b790` stored an occupancy byte other than `0xff` and `FUN_000109f0` finds a side-`0` unit on that tile. The menu sets `DAT_00069cd0` to 1 before the picker, and the distance test is strict less-than that value, so the unit has to be on the cursor tile. Escape (`0x01`) or delete (`0x53`) returns −1 and the menu stays up. A chosen target is faced with `FUN_0001c2b0`, then `FUN_00018d50` plays the clips. The menu does not read `DAT_00060010`. It always plays the screen.

The phase walker is `FUN_00010010`, called for side `1` and then side `0` from `FUN_0001e3c0`. Its low nibble at unit `+0x34` picks a script. Several of those scripts call `FUN_00012c10`, which scores three ranges into `DAT_00063f78`, `DAT_00063f88`, and `DAT_00063f8c` and then either swings (`FUN_00012e50`), casts (`FUN_00013c90`), or takes the third action (`FUN_00027150`). Those two alternatives were not decompiled. `FUN_00012e50` is the swing:

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

## The number

`rand` is `FUN_00042a68`. The arithmetic below is `FUN_00019f60` on the clip path and `FUN_0001c4f0` on the immediate path. The two bodies match. `FUN_00019f60` does not write the pool. It returns six dwords. Dword 0 is 1, and a landed roll stores 0. Dword 1 is 1 when defense was halved. Dword 5 is the damage. The clip player spreads dword 5 across the hit frames. A miss leaves dword 5 at 0, so the pool write subtracts nothing.

`FUN_00012550` returns 1 when the class byte is `0x16`, `0x17`, `0x18`, `0x1f`, or `0x25`. That fighter skips the terrain percent. The status write for weapon kinds 1 and 4 asks `FUN_00029050` instead of the class-`0x19` test the immediate path uses. `FUN_00029050` was not decompiled.

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

`FUN_0001dd00` returns immediately when the term is 0, or when `FUN_000109b0` is nonzero. Character id `9` also returns at level `0x63`. Any other character returns at level `0x28`. Otherwise the term is capped at 99, added to byte `+0x3c`, and a number is drawn rising off the unit's tile for 15 map frames. If the sum passes 99, `Levup.wav` is started, `+0x21` increases by 1, the sum drops by 100, and a picture from `DAT_000643a0` is held over the map until a key below `0x80` or 250 frames. Five words are redrawn through `FUN_0001e340` from the class row. A matching byte in the table from `FUN_00018bf0` calls `FUN_00028280`. Both of those were not decompiled. The new level is capped again: character `9` at 99, anything else at `0x28`, and the remainder byte is cleared when a cap hits. One crossing subtracts 100 once, so one fight raises the level by at most 1.
