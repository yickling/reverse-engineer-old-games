# Verdicts

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

## Reconstruction

A reconstruction of the battle, the campaign, a character, and the town is possible.

Written in the topic files:

- The grid, placement, and damage
- The spell amount and the phase scripts
- The CPU walk
- The thirty successors, the fork at 26, and the quit at 29
- Each index's win and loss
- The five village menus, the shop prices, and the equipment rows
- The four save slots, the byte sum, and the walk that scrambles the buffer
- The icon opcodes

Discarded. The study is the gameplay, so these are not open gaps. The addresses are in [Functions](functions.md):

- The sample driver, including `object 1 + 0x2da33` and `object 1 + 0x35cc0`. A new presentation plays the sample from the fields in [Pictures](pictures.md).
- The Miles bodies
- The CD device requests
- The heap walk
- The gift selector
- The four studio files

The original music is CD audio. The recordings were not among the files that were walked. The track numbers, the two discs, and the request are in [File formats](formats.md). An index below 18 is disc 1. An index of 18 or more is disc 2. `FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud` are named in [Session](session.md). The handoff is in [Opening](opening.md).

## Remake

A modernised remake can start. The gameplay list in [Gaps](gaps.md) is complete.

The battle rules, the campaign order, the win and loss of an index, the town, a character, and the screen are written. The pieces discarded above stay outside the remake. A remake supplies its own music. The screen a new engine keeps is the last section of [Pictures](pictures.md). Handler 21 is in [Scenario files](scenario.md). No map row selects it.
