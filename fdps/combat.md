# Combat numbers

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

Two presentations share one formula. `FUN_00012e50` calls `FUN_00018d50` (the full `SAF` fight) when `DAT_00060010` is nonzero, and otherwise calls `FUN_0001c370`, which writes the pool immediately. The full fight computes the same number in `FUN_00019f60` and lets `FUN_000196b0` apply it on hit frames. `FUN_0001c4f0` is the immediate writer. The arithmetic in the two functions matches. How the fight is drawn is in [Pictures](pictures.md).

`rand` is `FUN_00042a68`. The equipped weapon is slot 0 through `FUN_00025110` and `FUN_000251d0`, then the record from `FUN_00018b30`. Weapon byte `+9` and byte `+10` are `kind` and `arg`. The unit words are in [Units](units.md). The terrain percents are in [Map](map.md).

```
attack  = attacker[+0x48]
defense = defender[+0x4a]
hp, max  = defender[+0x40], defender[+0x42]
hit      = attacker[+0x4c] - defender[+0x4e]
crit     = class_row[8]                 # ProMap.dat row for attacker[+0x20]

if terrain bonus applies to the attacker:
    attack  += attack  * attack_percent[terrain] / 100
if terrain bonus applies to the defender:
    defense += defense * defense_percent[terrain] / 100

if kind == 3: crit += arg
if kind == 4 and rand % 100 < arg: defender[+0x25] = rand % 4 + 2
if kind == 1 and rand % 100 < arg: defender[+0x26] = rand % 2 + 2
# the immediate path also refuses those two writes when class == 0x19
# the clip path asks FUN_00029050 instead

landed = rand % 100 < hit
if landed:
    if rand % 100 < crit: defense = defense / 2
    damage = (attack - defense) * 9 / 10
    if damage < 0: damage = 0
    if damage / 9 != 0: damage += rand % (damage / 9)
    hp = max(0, hp - damage)
```

Integer division is toward zero, as the compiled `/` on these ints does. A miss leaves the pool unchanged. `kind == 2`, or a roll below 3, makes `FUN_0001c370` run that whole resolution twice. The clip player has the same second-swing test.

On the immediate path, a side-`2` attacker and a defender whose character id is above `0x3b` also write `DAT_00069cec`:

```
row = FUN_00018b00(defender[+7] - 0x3c)
scale = attacker[+0x21]
if attacker[+7] > 10: scale += 0x1e
gain = defender[+0x21] * byte(row + 9) / scale
if hp != 0: gain = gain * damage / max
```

The clip path writes the same term only when the defender's side byte is `0`, which is a different condition. `FUN_0001e3c0` later does `DAT_00069cec = DAT_00069cec * 15 / 10` from `FUN_00012e50` before `FUN_0001dd00`. What the term is spent on was not followed. Inferred: it is the experience award, because it grows with damage dealt and shrinks against `scale`.

The bar drawn by `FUN_0001cad0` has `(hp * 0x29 + max - 1) / max` lit segments, so the bar is 41 steps. A counterattack happens when `FUN_000137e0` returns 1: the defender's `+0x26` is 0, the two units are one tile apart (absolute dx + dy equals 1), and the defender's equipped record has byte `+0xb == 1`.
