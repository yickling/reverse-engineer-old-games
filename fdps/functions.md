# Functions and tables

Part of the [FDPS notes](README.md). Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game.

This is the status list. The behavior stays in the topic file. A row is where the body sits, how it was read, and one line of what it does. When a body is read, add the row and take it out of [Gaps](gaps.md). A body that was only seen stays under Not read and in Gaps.

Where is `object N + offset`, from that object's base in the executable, as in [Binary](binary.md). A row is decompiled unless this file says it was disassembled or not read. The session loop, the thirty openers, the thirty endings, the thirty after-action checks, and the step handlers were disassembled, because Ghidra had not created functions there.

Decompiled: 260, plus the picture-mode bodies in the table under Pictures. Disassembled: the blocks below. Not read: the list at the end.

## Disassembled

No Ghidra function existed, or the body was read from the bytes. The topic file says which.

| Address | What it is | Note |
| --- | --- | --- |
| `object 1 + 0x33008` | Real entry. A short jump over the Watcom banner into the CRT. | [Binary](binary.md) |
| `object 1 + 0x33080` | CRT. The startup at `object 1 + 0x3dcbc` calls `object 1 + 0x191f0`. | [Binary](binary.md) |
| `object 1 + 0x191f0` | The session loop. Outcome 1 plays the loss, outcome 2 runs the ending, outcome 3 saves. | [Session](session.md) |
| `object 2 + 0x74` | Thirty openers, the first at `object 1 + 0x10e60`. Each loads the map, plays the icon script, shows the chapter card, and centers a slot. | [Session](session.md) |
| `object 2 + 0x304` | Thirty endings, `object 1 + 0x2a180` through `object 1 + 0x2b7f0`. Indexes 0 through 25, 27, and 28 store the next index. Index 26 quits unless two items are present. Index 29 quits. | [Session](session.md) |
| `object 2 + 0x28c` | Thirty after-action checks, `object 1 + 0x2a120` through `object 1 + 0x2b7c0`. | [Turns](turns.md) |
| `object 2 + 0x1c4` | Fifty step handlers. The ones a map row names are the table in Scenario files. | [Scenario files](scenario.md) |
| `object 1 + 0x6120` | Draws the command diamond. | [Pictures](pictures.md) |
| `object 1 + 0x278e0` | Handler 21. Kills side 0, then either stores outcome 2 or hides slots 0 through 8 except 4, and slot 0x34. | [Scenario files](scenario.md) |
| `object 1 + 0x209c0` | Once a tick, and every 75 ticks restarts the track at `object 2 + 0x9d54`. | [Turns](turns.md) |
| `object 1 + 0x2d0e5` | Returns a block of the size it is passed. The heap walk is `object 1 + 0x2d0f3`. | [Pictures](pictures.md) |
| `object 1 + 0x2d284` | Copies its count from the second pointer onto the first. | [Pictures](pictures.md) |
| `object 1 + 0x32a28` | Writes one byte to a port. | [Pictures](pictures.md) |
| `object 1 + 0x32a40` | Fills its count with the byte it is passed. | [Pictures](pictures.md) |
| `object 1 + 0x20520` | Timer tick. No function was created. Increments `object 2 + 0x9d64` and calls rand. | [Session](session.md) |
| `object 1 + 0x32a8a` | Stores its argument into the rand seed at `object 2 + 0x39c`. No direct call was found. | [Combat](combat.md) |
| `object 1 + 0x37080` | Stores the sample playback rate at handle `+0x3c`. | [Pictures](pictures.md) |
| `object 1 + 0x37150` | Stores the sample loop count at handle `+0x30`. | [Pictures](pictures.md) |
| `object 1 + 0x37160` | Starts the sample. Calls `object 1 + 0x2da33` with `0x401` when the driver has not been started. | [Pictures](pictures.md) |
| `object 1 + 0x2b84e` | Allocates the CD request block and the data block. | [File formats](formats.md) |
| `object 1 + 0x2b8ed` | Sends the request through interrupt 0x2f with AX 0x1510. | [File formats](formats.md) |
| `object 1 + 0x3332c` | Copies the CD request into the real-mode block and copies the result back. | [File formats](formats.md) |
| `object 1 + 0x2bd15` | Reads the disc's first track, last track, and lead-out. | [File formats](formats.md) |
| `object 1 + 0x2be38` | Reads one CD track's start. | [File formats](formats.md) |
| `object 1 + 0x2b9af` | Splits a dword into three bytes. | [File formats](formats.md) |
| `object 1 + 0x2b9e8` | Turns those three bytes into a sector address. | [File formats](formats.md) |
| `object 1 + 0x2c0bf` | Reads the device-status dword. | [File formats](formats.md) |
| `object 1 + 0x2c458` | Returns 1 when bit 9 of the driver status word is clear. | [File formats](formats.md) |
| `object 1 + 0x2c573` | Picks the start and end sectors for the track. | [File formats](formats.md) |
| `object 1 + 0x2c1c2` | Plays the sector span. Command byte 0x84. | [File formats](formats.md) |
| `object 1 + 0x2c3a6` | Asks interrupt 0x2f whether a CD-ROM drive is present, then reads the disc. | [File formats](formats.md) |
| `object 1 + 0x2c42c` | Sends output byte 5 and returns the not-busy test. No direct call. | [File formats](formats.md) |
| `object 1 + 0x2c469` | Sends control byte 9 and returns the following byte. No direct call. | [File formats](formats.md) |
| `object 1 + 0x2c602` | Plays from one track's position to another's. No direct call. | [File formats](formats.md) |
| `object 1 + 0x2c656` | Plays from sector 0 to the lead-out. No direct call. | [File formats](formats.md) |
| `object 1 + 0x2c681` | Returns 1 when the track-control byte is not 0x40. No direct call. | [File formats](formats.md) |
| `object 1 + 0x2d0e0` | Jumps to `object 1 + 0x33a20`, which waits on DOS time function 0x2c. | [Session](session.md) |
| `object 1 + 0x4677d` | Picture mode 0. Hand-written, no prologue. The stored byte is written unchanged. | [Pictures](pictures.md) |
| `object 1 + 0x46927` | Picture mode 3. Hand-written. Writes (sample & 2) + 0x80. | [Pictures](pictures.md) |
| `object 1 + 0x46b39` | Skips one compressed source row inside the scale modes. | [Pictures](pictures.md) |
| `object 1 + 0x472c1` | Picture mode 7. Mirror left to right. | [Pictures](pictures.md) |
| `object 1 + 0x4735d` | Picture mode 8. Mirror top to bottom. | [Pictures](pictures.md) |
| `object 1 + 0x47503` | Picture mode 10. Same tables as mode 9, and the destination pixel is not read. | [Pictures](pictures.md) |

## Decompiled

One line is the body the topic file records.

### [Session](session.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x10c30` | Draws Chapter.saf under Chapter.pal and fades the palette sixteen steps down and back up. |
| `object 1 + 0x12720` | Loads the map. Clears the outcome, zeroes the camera and cursor, and sets the turn counter to 1. |
| `object 1 + 0x13950` | Copies each battle record onto the matching roster record. Called by every ending except index 26. |
| `object 1 + 0x19410` | Frees the interface, font, text, icon cache, unit array, and one triple of buffers per loaded section. |
| `object 1 + 0x19630` | Loads the shared interface from MISC.VFS and FIELD.VFS: both palettes, the cursor, command window, shadow, status, message box, digits, selection bar, level-up picture, window, bars… |
| `object 1 + 0x1b870` | Keeps the map until the outcome dword is nonzero or the system menu returns nonzero, and only then does `object 1 + 0x191f0` look at that outcome. |
| `object 1 + 0x1d8e0` | Clears bit 0x80 of byte +5 on every slot. |
| `object 1 + 0x20270` | (0x19) starts the two sound devices (eight channels on the second) and passes 0x19 on to `object 1 + 0x20540`. |
| `object 1 + 0x20330` | Calls the sound shutdown. |
| `object 1 + 0x20540` | Registers the tick at `object 1 + 0x20520`, requests frequency `0x19`, and starts the timer. |
| `object 1 + 0x2df06` | Forwards the tick. The log string names AIL_register_timer. |
| `object 1 + 0x2e15a` | Forwards the handle and `0x19`. The log string names AIL_set_timer_frequency. |
| `object 1 + 0x2e323` | Forwards the handle. The log string names AIL_start_timer. |
| `object 1 + 0x20960` | Stores n and asks the CD driver for track n + 1. |
| `object 1 + 0x209c0` | On each new tick counts to 0x4b and, when the track is set and a status call is nonzero, starts that track again. |
| `object 1 + 0x20cb0` | Shuts sound down, blanks the palette, and passes {prefix}\fd.exe, {prefix}\FD1.Vid, and {prefix}\FD1.Aud to CRT `object 1 + 0x3df59`. |
| `object 1 + 0x21930` | Called from this village step, cycles which roster record is shown and leaves on confirm. |
| `object 1 + 0x24290` | (slot, id) returns the pair index of that id on that roster slot, or −1. |
| `object 1 + 0x29b80` | Stores 0 into +0x40 of every side-0 unit, then runs the death spin. |
| `object 1 + 0x29be0` | Opens Relive.cel. Runs after an ending's icon script and before the next-index store. |
| `object 1 + 0x2c217` | Stops CD audio. Command byte 0x85. |
| `object 1 + 0x2c5cb` | Plays one CD track, from its start to the next track's start. |
| `object 1 + 0x2d622` | Shuts sound down. |
| `object 1 + 0x32b5b` | Prints an error string. |

### [Turns](turns.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x10` | One unit's phase. Called for side 1 and then for side 0. |
| `object 1 + 0x9b0` | (slot) returns bit 0 of that unit's byte +5. |
| `object 1 + 0xb90` | Stamps the hunted units before each movement fill. |
| `object 1 + 0x1460` | In mode 2, keeps the visible enemy on the cheapest reachable tile. |
| `object 1 + 0x18f0` | Writes 0xff into the cost byte of every other visible unit on the mover's side of the filter. |
| `object 1 + 0x19b0` | ORs bit 0x80 into byte +5 when an action is committed. |
| `object 1 + 0x19e0` | (destX, destY, unit, filter) stops short of a tile it cannot enter. |
| `object 1 + 0x20d0` | Rests: if +0x40 is already +0x42, or +0x25 or +0x26 is nonzero, it returns 0. |
| `object 1 + 0x26b0` | Chooses a tile and hands it to the walk. |
| `object 1 + 0x27c0` | Ranks by Manhattan distance. |
| `object 1 + 0x2960` | Walks side 0 in two passes after the enemy phase clip. |
| `object 1 + 0x2b20` | Walks side 1. Calls the phase for each eligible unit, then the same callback tables as the player's action. |
| `object 1 + 0x4aa0` | The command diamond opened when confirm finds nobody under the cursor. Result 1 walks each eligible side-2 unit to the cursor. |
| `object 1 + 0x4e90` | The system menu, and the writer of FDE.SAV. |
| `object 1 + 0x5460` | Passes the unit's tile and 1 after `object 1 + 0x19b0` when a move is followed by a menu result other than −1, and when `object 2 + 0x4` is set on a cancelled menu. |
| `object 1 + 0x5b80` | Draws the 25×22 item-type mark from COMMAND.CEL. |
| `object 1 + 0x5bd0` | Writes palette indexes 8 through 15 from a 16-step cycle. |
| `object 1 + 0x5cf0` | Keeps four disable flags. |
| `object 1 + 0x61a0` | Closes the command diamond. Plays OpWin.wav and steps the circle back down. |
| `object 1 + 0x61f0` | Reads the command diamond. Arrows move when that corner's flag is 0. Enter returns 1 and Escape returns −1. |
| `object 1 + 0x7980` | Returning anything other than 0 shows string 0x20c and leaves the tile alone. |
| `object 1 + 0x83c0` | Four toggles. Corner 2 of the command diamond. |
| `object 1 + 0x84e0` | The search on the fourth command corner. |
| `object 1 + 0xe3c0` | The turn change. |
| `object 1 + 0xead0` | Plays the phase clip. The enemy clip is followed by the side-0 walk. |
| `object 1 + 0xfa00` | Walks the units whose side byte equals that argument and whose flag bit 0 is clear. |
| `object 1 + 0x13df0` | Reads the save buffer back and restores the battle at the front of FDE.SAV. |
| `object 1 + 0x14d40` | Rebuilds the four combat words from the bases and the equipped items. |
| `object 1 + 0x14e70` | (slot, row, dest, pitch) draws the eight pairs. |
| `object 1 + 0x15280` | Draws a second menu through `object 1 + 0x6120` and reads it with `object 1 + 0x61f0`. |
| `object 1 + 0x15990` | Plays OpWin1.wav and returns what `object 1 + 0x15af0` chooses. |
| `object 1 + 0x15af0` | The choice the item list returns. |
| `object 1 + 0x15d70` | Row 2 of the item menu. Lists the pairs. |
| `object 1 + 0x15fb0` | Returns 1 when one of six bytes from `object 1 + 0x8b90`(class) equals the item record's first byte. |
| `object 1 + 0x16040` | Clears bit 0x40 on other pairs in the same group, then stores 0x40 in the chosen pair's flag. |
| `object 1 + 0x17bf0` | Stays in a spell list until one cast is confirmed. |
| `object 1 + 0x18100` | Reads up and down in a spell list. A window of eight rows follows the selection. |
| `object 1 + 0x1a280` | The title. Returns only after a menu choice, and opens StSel.cel and StBoard.cel. |
| `object 1 + 0x1d0f0` | One of the four walk steps. Passes the cursor tile divided by 24, and 0. |
| `object 1 + 0x1d210` | One of the four walk steps. Passes the cursor tile divided by 24, and 0. |
| `object 1 + 0x1d320` | One of the four walk steps. Passes the cursor tile divided by 24, and 0. |
| `object 1 + 0x1d430` | One of the four walk steps. Passes the cursor tile divided by 24, and 0. |
| `object 1 + 0x1d7e0` | Reads a roster slot and slides the camera to that tile. |
| `object 1 + 0x1d9b0` | Walks the battle slots for one id. |
| `object 1 + 0x1da80` | Draws ADWin.cel picture 0 when both panel bytes are set. |
| `object 1 + 0x1dd20` | Allocates (`object 2 + 0x150` + 1) * 0x50 bytes, copies that many bytes out of the unit array, clears `object 2 + 0x150` * 0x50 bytes of the old array, frees it, and keeps the new pointer. |
| `object 1 + 0x1ddc0` | Loads the tile under a unit, and may store a handler index when the terrain matches. |
| `object 1 + 0x1de50` | Walks the sixteen rows at byte 3 of the map file, in [Scenario files](scenario.md): a row whose first byte is the turn counter and whose third byte is this argument calls the handler indexed by the middle byte, passing… |
| `object 1 + 0x1e7a0` | Looks for a side-2 unit that is still eligible (flag bits 0x81 clear, +0x26 clear). |
| `object 1 + 0x20a30` | Reads the CD track byte at `object 1 + 0x20230` + scenario * 2 + argument and starts that track. |
| `object 1 + 0x220e0` | (0xa8208, 0x140) draws command pictures 0x34 through 0x36 at VGA (8, 104) and that dword in eight digits. |
| `object 1 + 0x22150` | A village menu that stays until the selection is −1. |
| `object 1 + 0x222e0` | Plays ShopWin.Cel in nine steps through expander mode 4. |
| `object 1 + 0x23440` | Picks a roster index. |
| `object 1 + 0x23cf0` | Picks a roster index and calls `object 1 + 0x6a90`, the status window. |
| `object 1 + 0x23d70` | A village list. Picks a roster index, then a pair, and sells it. |
| `object 1 + 0x23f80` | Picks a pair, shows string 0x1fd, and picks a second roster index. |
| `object 1 + 0x24190` | A village list. Calls the equip list on the chosen roster index. |
| `object 1 + 0x2a050` | The check most after-action bodies call. Stores outcome 2, then 0 again if any side-0 unit is still standing. |
| `object 1 + 0x2d0d4` | Returns the absolute value. |
| `object 1 + 0x46509` | The key byte the map visit polls. |

### [Scenario files](scenario.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x11620` | The icon script. Plays one Icon##.dat from IconAni.vfs. |
| `object 1 + 0x11e00` | Icon opcode 5. Slides the camera toward a tile, then snaps the cursor there. |
| `object 1 + 0x123e0` | Icon opcode 14. Waits, then fades the palette down by a bias. |
| `object 1 + 0x12bb0` | Opens ICON.CEL (the string at `object 2 + 0x1a03`, mode at `object 2 + 0x1a00`) and loads map%02d.cod from FIELD.VFS into `object 2 + 0x140`. |
| `object 1 + 0x13800` | (scenario, group, arg) opens ICON.CEL and loads map%02d.cod from FIELD.VFS into `object 2 + 0x140` through `object 1 + 0x193d0`. |
| `object 1 + 0x151d0` | The value a shop multiplies by 5 and shifts right by 2, then subtracts from the price. |
| `object 1 + 0x1bc40` | Redraws the map. |
| `object 1 + 0x21470` | (group, dest) copies bytes from group * 12 until 0xff or 12 bytes, each byte widened to a dword item id, and returns the count. |
| `object 1 + 0x22480` | The shop list for one group. Returns the chosen id, or −1 on cancel. |
| `object 1 + 0x268d0` | Writes the low nibble of unit +0x34. |

### [Map](map.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0xb20` | Sets each pair's second byte to 0xff and masks the first with 0x3f. |
| `object 1 + 0xc30` | ORs 0x40 into the first byte of that unit's pair, and ORs 0x80 into the first byte of each of the four orthogonal neighbors that sit on the map. |
| `object 1 + 0xde0` | Movement flood fill. Writes 0 on the origin and does not clear the other tiles. |
| `object 1 + 0x127b0` | Stores the section's third dword as the horizontal scale (`object 2 + 0x9c80`) and the fourth as the vertical scale (`object 2 + 0x9c68`). |
| `object 1 + 0x1b790` | The tile query. Reads the map cell at x, y. |
| `object 1 + 0x1bcf0` | Paints every section whose order byte is below 10, then the cursor pictures, then the units, then every section whose order byte is above 10. |
| `object 1 + 0x1c0c0` | Paints one section as 14 columns by 9 rows of 24×24 tiles, which is the 320×200 window with a partial tile at the right and bottom edges. |

### [Units](units.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x8920` | Is the call that passes the nine names, each a member of MISC.VFS, and the pointer each one is stored in: `object 2 + 0x3fd8` for Friaprda.dat, `object 2 + 0x3fec` for FriLevUp.dat, `object 2 + 0x3fe0` for… |
| `object 1 + 0x8aa0` | Returns the Friaprda.dat row. 60 rows of 0x18. |
| `object 1 + 0x8ad0` | Returns the FriLevUp.dat row. 60 rows of 0x0b. |
| `object 1 + 0x8b00` | Returns the EnemyDat.dat row of character id minus 0x3c. 91 rows of 0x0a. |
| `object 1 + 0x8b30` | Returns the Item.dat row. 251 rows of 0x17, at `object 2 + 0x3fe0`. |
| `object 1 + 0x8b60` | Returns the ProMap.dat row at class + 1. 41 rows of 0x0a, at `object 2 + 0x3fd0`. |
| `object 1 + 0x8b90` | Returns the ProEqu.dat row. 36 rows of 6, at `object 2 + 0x3fe4`. |
| `object 1 + 0x8bc0` | Returns the MagicDat.dat row. 40 rows of 7, at `object 2 + 0x3ff0`. |
| `object 1 + 0x8bf0` | Returns the GetMgTab.dat row. 60 rows of 0x0c, at `object 2 + 0x3fe8`. |
| `object 1 + 0x8c20` | Returns the RankUp.dat row. 9 rows of 0x0c, at `object 2 + 0x3fdc`. |
| `object 1 + 0x13280` | A spawner. Fills a unit from the class rows and takes its tile from the COD record of the same index. |
| `object 1 + 0x13920` | (index) returns the roster record at `object 2 + 0x4108` + index * 0x50. |
| `object 1 + 0x13a90` | Adds the equipped item shorts into attack, defense, hit, and avoid, and stores the four sums at +0x48 through +0x4e. |
| `object 1 + 0x13b90` | (characterId) appends one roster record at `object 2 + 0x4108 + object 2 + 0x4114 * 0x50` and then adds 1 to the count. |
| `object 1 + 0x15110` | (unit, 0) returns the first equipped pair whose type is from 1 through 0x15. |
| `object 1 + 0x15c90` | Slides the later pairs down over the removed index and stores 0x80 at +0x18. |
| `object 1 + 0x15cf0` | Writes an id into the first empty pair and clears bit 0x80. |
| `object 1 + 0x18280` | Sets one learned-id bit. |
| `object 1 + 0x18f40` | (kind, id) looks the unit up and, when rand % 100 is below byte +2 of a MagicDat.dat row and the chosen byte is still 0, stores rand % 2 + 2. |
| `object 1 + 0x193d0` | (archive, name, dest) stores the pointer `object 1 + 0x29940`(name, archive) returns. |
| `object 1 + 0x212b0` | Points the battle array at the roster, loads the scenario text and the shop file, frees the three pointer tables, and opens ICON.CEL. |
| `object 1 + 0x238f0` | Passes 0 when the bought item's type is at most 0x15, and 1 when the type is greater. |
| `object 1 + 0x24310` | Compares byte 0 of the row with byte 0 of the selected triple, stores byte 1 at `object 2 + 0x4034`, and stores byte 2 at `object 2 + 0x4038` before the text call at `object 1 + 0x246f6`. |
| `object 1 + 0x24980` | Selects its triple with argument * 3. |
| `object 1 + 0x25030` | Called from the rank window at `object 1 + 0x244b5`, reads RankUp of unit byte +8 at `object 1 + 0x251e1`. |
| `object 1 + 0x46510` | The failure call when an archive member is missing, beside the exit. |

### [Combat](combat.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x9f0` | Finds a side-0 unit on a tile. |
| `object 1 + 0x1da0` | Lists every tile whose cost byte is not 0xff, in row-major order, and returns the count. |
| `object 1 + 0x1e50` | Lists targets with shape = row byte +4, inner = 0, and a side taken from row byte +6. |
| `object 1 + 0x2230` | The swing. Reads the weapon, flood-fills with the move budget, and lists the reachable tiles. |
| `object 1 + 0x2550` | Returns 1 when the class byte is 0x16, 0x17, 0x18, 0x1f, or 0x25. |
| `object 1 + 0x25c0` | Returns 1 only when the attacker's +0x26 is 0, the two tiles are one step apart on a side (`object 1 + 0x2d0d4` is the absolute value, and the two absolutes sum to 1), the weapon-group lookup finds… |
| `object 1 + 0x2c10` | Fills the three scores below and returns 0 when all three are below 6. |
| `object 1 + 0x2e50` | The swing. Centers the camera on the attacker and walks toward the defender. |
| `object 1 + 0x3040` | The carried-item scorer. |
| `object 1 + 0x32b0` | Scores that list, and a strictly higher score replaces `object 2 + 0x3f8c`. |
| `object 1 + 0x3420` | Clears between the two paints. |
| `object 1 + 0x3670` | (cursor x, cursor y, dest, origin x, origin y, length, side) does not use the cost grid. |
| `object 1 + 0x37e0` | Returns 1 when a counterattack is allowed: +0x26 is 0, the units are one tile apart, and +0xb is 1. |
| `object 1 + 0x3920` | Scores that list, and the kept candidate is the higher score, then the larger first short of the row. |
| `object 1 + 0x3c20` | Counts targets whose status byte is 0. Id 0x14 calls it for +0x22, +0x23, and +0x24 and keeps the last return. |
| `object 1 + 0x3c90` | Casts when the spell band is at least 6. |
| `object 1 + 0x96b0` | Rolls rand % 100 < 3 twice. |
| `object 1 + 0x9f60` | Does not write the pool. |
| `object 1 + 0xc2b0` | Compares absolute dx with absolute dy. |
| `object 1 + 0xc370` | The immediate combat path. Redraws the map and applies the pools in place. |
| `object 1 + 0xc4f0` | The roll on the immediate path. The body matches `object 1 + 0x9f60`. |
| `object 1 + 0xd690` | Collects units whose flag bit 0 is clear and whose word at +0x40 is 0. |
| `object 1 + 0xd960` | Walks the death copies. The first byte selects the step. |
| `object 1 + 0xdd00` | Returns immediately when the term is 0, or when `object 1 + 0x9b0` is nonzero. |
| `object 1 + 0xe340` | Adds one rolled amount to each of five words. |
| `object 1 + 0xf310` | Called after a pool helper has drawn its number. |
| `object 1 + 0xf4e0` | (amount, base, id) formats the amount with %d at `object 2 + 0x17bc` into a buffer that starts as four spaces. |
| `object 1 + 0xf660` | Appends the four miss glyphs. Frames 1, 8, 13, and 19. Pictures 0x34, 0x35, 0x36, and 0x36. |
| `object 1 + 0xf7a0` | Uses the same frames and the next four bytes, 0x37, 0x38, 0x39, and 0x3a, at `object 1 + 0xc2a6`. |
| `object 1 + 0xfbd0` | Stores each nonzero byte of a four-byte run at that byte's own index. |
| `object 1 + 0x15210` | Is the count, the same call that enables menu slot 2. |
| `object 1 + 0x16150` | Copies the three bytes at +0x31 from each still-visible unit whose pool is below 1 and whose first byte is not 0xff. |
| `object 1 + 0x16200` | Walks the targets and subtracts. |
| `object 1 + 0x16270` | Applies the item after the aim. |
| `object 1 + 0x16dd0` | Plays the formatted clip on the map. Draws it twice per frame. |
| `object 1 + 0x16fa0` | Plays Posion.saf and adds. |
| `object 1 + 0x17040` | Writes min(+0x42, +0x40 + spread). |
| `object 1 + 0x17150` | Returns 0, so a script that called it continues. |
| `object 1 + 0x174b0` | Copies the three bytes at +0x31 into the death list when the pool is below 1 and the first byte is 2, 3, 4, or 5. |
| `object 1 + 0x17570` | Adds to the pool at +0x44, capped at +0x46. |
| `object 1 + 0x17810` | Fills the id list, the same call that enables menu slot 1, and byte +0x27 must be 0. |
| `object 1 + 0x182f0` | (caster, target, spell) reads the signed short at the start of the spell row. |
| `object 1 + 0x18430` | Takes amount * 9 / 10 plus (rand % 100) * amount / 1000 off the target's word at +0x40, and floors that word at 0. |
| `object 1 + 0x18590` | Subtracts the spell cost. |
| `object 1 + 0x185e0` | Opens Mag11.saf. |
| `object 1 + 0x188c0` | Clears `object 2 + 0x9cd0` and sets it back to 1 before returning. |
| `object 1 + 0x18eb0` | (target) walks +0x25, +0x26, and +0x27. |
| `object 1 + 0x19050` | Returns 0 when a status byte may be written. |
| `object 1 + 0x1b280` | The cursor picker. Moves one tile at a time. |
| `object 1 + 0x1c430` | Lays pictures on tiles around the cursor pixel when `object 2 + 0x9cd0` is 1 through 5. |
| `object 1 + 0x1c9b0` | Copies one 24×24 picture from Cusor.cel, the file `object 1 + 0x19630` stores at `object 2 + 0x43c8`, when the pixel sits in the camera window. |
| `object 1 + 0x1d060` | Plays a tile as six redraws. |
| `object 1 + 0x1d550` | (x, y) slides the cursor pixel, `object 2 + 0x9cd4` and `object 2 + 0x9ccc`, toward that point. |
| `object 1 + 0x2d25c` | Rounds toward zero. Stores the control word, sets the high byte to 0x1f, runs FRNDINT, and restores the word. |
| `object 1 + 0x32a62` | Returns the rand seed, the dword at `object 2 + 0x39c`. |
| `object 1 + 0x32a68` | Stores `seed * 0x41c64e6d + 0x3039` and returns bits 16 through 30. |

### [Pictures](pictures.md)

The mode switch is `object 1 + 0x4664b`. These bodies are the mode table there. Modes 0, 3, 7, 8, and 10 are under Disassembled.

| Address | What it does |
| --- | --- |
| `object 1 + 0x467fd` | Mode 1. Looks each stored byte up in the 256-byte table passed as the sixth argument. |
| `object 1 + 0x46895` | Mode 2. The same writes as mode 1. Opcode 0xc0 skips and does not read the destination. |
| `object 1 + 0x469ce` | Mode 4. Scales to the output width and height in the sixth argument. |
| `object 1 + 0x46b9a` | Mode 5. Steps by two signed words, in units of 1/4096 of a pixel. |
| `object 1 + 0x46e84` | Mode 6. Mode 4's width test, then mode 5's step. |
| `object 1 + 0x4738b` | Mode 9. Blends the sample onto the pixel already in the buffer. |
| `object 1 + 0x47686` | Mode 11. Mode 9's tables, with the added term taken once from the blend record. |
| `object 1 + 0x477e4` | Mode 12. Mode 9's blend, only for samples inside a low and high index. |

The other picture functions:

| Address | What it does |
| --- | --- |
| `object 1 + 0x3ed0` | Reads one compressed cell of a SAF chunk. |
| `object 1 + 0x3fd0` | Walks the chunks of one SAF frame. |
| `object 1 + 0x40e0` | (file, index) returns one frame. |
| `object 1 + 0x4140` | Blits the current frame into a compose buffer. |
| `object 1 + 0x42d0` | Starts the sample on a frame when the sample flag is set. |
| `object 1 + 0x44d0` | Returns the frame count. |
| `object 1 + 0x4540` | Steps a clip cursor. Mode 1 resets the index and the tick and returns 0. Any other mode advances, and returns 1 when the clip has finished one pass. |
| `object 1 + 0x5850` | Draws the four command pictures around the cursor, into that buffer, then performs this copy. |
| `object 1 + 0x62f0` | Stamps the sheet onto that picture at pitch 0x140. |
| `object 1 + 0x6830` | Opens Status.cel. |
| `object 1 + 0x6a90` | The status window. |
| `object 1 + 0x6e70` | One frame of the window open. Steps 0 through 8 on the status sheet. |
| `object 1 + 0x7730` | Draws one status bar: the filled picture, then picture 0 for the remainder. |
| `object 1 + 0x70b0` | Waits while text is up, and it is the call that passes expander mode 8. |
| `object 1 + 0x7520` | (dest, pitch, value, width, signed) expands NUMBER.CEL. |
| `object 1 + 0x77c0` | (dest, pitch, index) frees any picture it loaded before. |
| `object 1 + 0x7c90` | Names WinFail.Cel at `object 1 + 0x7d30`. |
| `object 1 + 0x8d50` | Builds the fight screen. |
| `object 1 + 0x92f0` | Use the defender during the strike and the attacker as well when there was no preamble. |
| `object 1 + 0x94c0` | Slides the two standing clips in from the side over nine composed frames before `object 1 + 0x96b0` plays the attack. |
| `object 1 + 0xa350` | Follows: eight frames slide one backdrop out and the other in by 40 pixels a frame, carrying the standing clip. |
| `object 1 + 0xa4a0` | (attacker, spellId, targetCount, targets). |
| `object 1 + 0xba10` | The ending reel. Draws the backdrop, the stand, the act, and the scenario string. |
| `object 1 + 0xcad0` | Draws a 41-step bar, separate from the fight bars. |
| `object 1 + 0xe810` | Called before PlyPhase.saf plays. |
| `object 1 + 0x12290` | Plays that file on the map. |
| `object 1 + 0x12f10` | Writes VGA colors 0 through 255 from the block at `object 2 + 0x43e4`. |
| `object 1 + 0x13020` | Is called with the character id as its first argument. |
| `object 1 + 0x14620` | Opens LoadKon.cel. |
| `object 1 + 0x176c0` | Draws the list, and the same margins run back down. |
| `object 1 + 0x1a1c0` | Plays Miss.wav. |
| `object 1 + 0x1a920` | Plays GameOver.saf, runs sixteen blend steps, and waits on a key. |
| `object 1 + 0x1ca60` | (unit, `object 2 + 0x168`) then picks a 24×11 mark from ICONSTS.CEL at `object 2 + 0x43d8`. |
| `object 1 + 0x1cb30` | Picks the map sprite. The index is slot * 12 + facing * 3 + step. |
| `object 1 + 0x1d830` | Picks the unit under the cursor. |
| `object 1 + 0x1d930` | (cel, index, dest, pitch, x, y, remap, mode) is the blit that reads the size. |
| `object 1 + 0x107f0` | Dismisses the message box in six steps, then copies the plain window back. |
| `object 1 + 0x1e840` | Pulses a run of palette entries on the scenarios in the Pictures table. |
| `object 1 + 0x1efd0` | Writes count palette entries, three bytes each, after vertical retrace. |
| `object 1 + 0x1f080` | (src, srcPitch, dest, destPitch, width, height) copies height rows of width bytes. |
| `object 1 + 0x1f120` | The same arguments. Writes a source byte only when it is not 0. |
| `object 1 + 0x1fda0` | Blends the screen through the two remap tables. |
| `object 1 + 0x20790` | Starts a named wave. |
| `object 1 + 0x255d0` | Opens Item.cel. |
| `object 1 + 0x25810` | Opens Church.cel. |
| `object 1 + 0x25a30` | Opens BarShop.cel. |
| `object 1 + 0x25d40` | Opens Weapon.cel. |
| `object 1 + 0x25f80` | Opens Secret.cel. |
| `object 1 + 0x2d254` | Reads a port. Port 0x3da is the vertical retrace. |
| `object 1 + 0x2edde` | Forwards the slot, the sample bytes, and the length. The log string names AIL_set_sample_address. |
| `object 1 + 0x2ee60` | Forwards the slot, the selector, and 2. The log string names AIL_set_sample_type. |
| `object 1 + 0x2eee2` | Forwards the slot. The log string names AIL_start_sample. |
| `object 1 + 0x2f096` | Forwards the slot and the rate. The log string names AIL_set_sample_playback_rate. |
| `object 1 + 0x2f1f8` | Forwards the slot and 1. The log string names AIL_set_sample_loop_count. |
| `object 1 + 0x37010` | Stores the sample address at handle `+8` and the length at `+0x10`. |
| `object 1 + 0x37040` | Stores the selector at handle `+0x34` and 2 at `+0x38`, and calls `object 1 + 0x35cc0` when either changes. |
| `object 1 + 0x4664b` | Stores the width, height, and pitch, then calls one body for the mode byte: |

### [Text](text.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x78e0` | The key read inside the map wait. Returns a byte at `object 3 + 0x6` when it differs from the previous one. |
| `object 1 + 0x8340` | (side) counts slots whose byte +6 equals that side and whose flag bit 0 is clear. |
| `object 1 + 0xfd50` | Stamps one cell. |
| `object 1 + 0xff30` | (block, index, dest, pitch, ink, fill, shadow) walks one string. |
| `object 1 + 0x10580` | The portrait path taken when the text lookup returns −1. |
| `object 1 + 0x10a40` | Draws the portrait. A lookup of −1 uses the missing-portrait path. Otherwise it centres the camera and opens the message box. |
| `object 1 + 0x1cfa0` | Returns `object 2 + 0x9cd8` + slot * 0x50. |
| `object 1 + 0x20f80` | Stores 1 into the byte at `object 1 + 0x21066` and stores ShopWin.Cel at `object 2 + 0x9d84`, then stores 0 at `object 1 + 0x2122c`. |
| `object 1 + 0x46523` | Copies the key ring's read index onto the other index, so the next read is empty. |
| `object 1 + 0x4652e` | Returns one byte from the ten-byte key ring, or 0xff when the indexes match. |

### [Archives](archives.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x1a110` | (archiveName, memberName) is the usual caller: open, `object 1 + 0x29940` to extract one member into a malloc block, free the directory. |
| `object 1 + 0x29820` | Opens an archive in "rb", seeks to 7, reads a dword count, seeks to 5, reads a word directory offset, and reads count * 26 directory bytes. |
| `object 1 + 0x29940` | Reads the size from entry+0x0d and seeks to entry+0x16. |
| `object 1 + 0x2d1e8` | Frees the blocks an archive member was extracted into. |

### [File formats](formats.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0xfea0` | Takes the high bit of a byte as the leftmost pixel and shifts left for the next pixel. |

### [Save](save.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x141b0` | Writes one title slot of FDE.SAV, and opens Save.cel. |
| `object 1 + 0x14460` | Reads a slot at 0x312b + slot * 0xa28. |
| `object 1 + 0x1e6a0` | Advances the marked tiles, the map is redrawn, PlyPhase.saf plays, and the phase music is called with argument 0. |

### [Binary](binary.md)

| Address | What it does |
| --- | --- |
| `object 1 + 0x32b7f` | Exits. Argument 1 is the failure exit the CRT uses. |

## Not read

Seen, and the body is not in a topic file. The longer note is in [Gaps](gaps.md).

| Address | What it is believed to be |
| --- | --- |
| `object 1 + 0x6790` | A FACE.CEL call whose arguments were not read. |
| `object 1 + 0x14605` | A call inside the save loader. |
| `object 1 + 0x1bfb0` / `object 1 + 0x1cfd0` | Called by the map compose around the range pictures. |
| `object 1 + 0x1fbd0` / `object 1 + 0x1ffc0` | Reveal the spell rectangle. |
| `object 1 + 0x200f0` | Copies the rising experience strip. |
| `object 1 + 0x1b030` | The channel bytes of the scenario palette pulse. Not split per scenario. |
| `object 1 + 0x261d0` | Opens Bonus-1.saf and Bonus.wav. The frames were not walked. |
| `object 1 + 0x2d0f3` | The heap walk `object 1 + 0x2d0e5` returns. A size of 0 returns 0. The rest was not read. |
| `object 1 + 0x2ec6b` / `object 1 + 0x2f26e` | Called on the sample slot before the address is set. |
| `object 1 + 0x34cb2` / `object 1 + 0x2d3e6` / `object 1 + 0x34ef3` | The log gate around the sample wrappers. |
| `object 1 + 0x35cc0` | Called when the sample type changes. |
| `object 1 + 0x2da33` | The driver call sample start issues with `0x401`. |
| `object 1 + 0x34cbe` / `object 1 + 0x34e50` / `object 1 + 0x34d78` | The Miles bodies the timer wrappers forward to. |
| `object 1 + 0x2f439` | Called when the register-timer wrapper logs. |
| `object 1 + 0x68d0` | Runs the status blit for steps 5 down through 0. The rest of the body was not read. |

## Data tables

A table the topic file already lays out. This list keeps the base, the stride, and the row count. The fields stay in the linked note.

### Code pointers

| Address | Count | What it selects | Note |
| --- | --- | --- | --- |
| `object 2 + 0x74` | 30 | The opener for scenario index n. | [Session](session.md) |
| `object 2 + 0x28c` | 30 | The after-action check for index n. | [Turns](turns.md) |
| `object 2 + 0x304` | 30 | The ending for index n. | [Session](session.md) |
| `object 2 + 0x1c4` | 50 | The step handler a map row names. The table runs up to `object 2 + 0x28c`. | [Scenario files](scenario.md) |

### Loaded rows

`object 1 + 0x8920` loads these nine members of `MISC.VFS`. `object 1 + 0x193d0` stores the pointer and does not read the rows.

| File | Base | Index | Stride | Rows | Note |
| --- | --- | --- | --- | --- | --- |
| `Friaprda.dat` | `object 2 + 0x3fd8` | `object 1 + 0x8aa0(character)` | `0x18` | 60 | [Units](units.md) |
| `FriLevUp.dat` | `object 2 + 0x3fec` | `object 1 + 0x8ad0(character)` | `0x0b` | 60 | [Units](units.md) |
| `EnemyDat.dat` | `object 2 + 0x3fd4` | `object 1 + 0x8b00(character − 0x3c)` | `0x0a` | 91 | [Units](units.md) |
| `Item.dat` | `object 2 + 0x3fe0` | `object 1 + 0x8b30(id)` | `0x17` | 251 | [Units](units.md) |
| `ProMap.dat` | `object 2 + 0x3fd0` | `object 1 + 0x8b60(class + 1)` | `0x0a` | 41 | [Units](units.md) |
| `ProEqu.dat` | `object 2 + 0x3fe4` | `object 1 + 0x8b90(class)` | `6` | 36 | [Units](units.md) |
| `MagicDat.dat` | `object 2 + 0x3ff0` | `object 1 + 0x8bc0(id)` | `7` | 40 | [Units](units.md) |
| `GetMgTab.dat` | `object 2 + 0x3fe8` | `object 1 + 0x8bf0(index)` | `0x0c` | 60 | [Units](units.md) |
| `RankUp.dat` | `object 2 + 0x3fdc` | `object 1 + 0x8c20(index)` | `0x0c` | 9 | [Units](units.md) |

### Other tables

| Where | What it is | Note |
| --- | --- | --- |
| `object 2 + 0x9cd8`, stride `0x50` | The battle unit array. Count is `object 2 + 0x150`. | [Units](units.md) |
| `object 2 + 0x4108`, stride `0x50` | The roster. Count is `object 2 + 0x4114`. `object 1 + 0x13920` returns one record. | [Units](units.md) |
| `object 2 + 0x13c + 0x83`, stride `0x1a` | The 26-byte placement records of one map. | [Scenario files](scenario.md) |
| `map%02d.cod`, records at `+9`, stride 6 | Id, x, and y. Placement reads x and y from two bytes later and does not read the id. | [File formats](formats.md) |
| `Shop%02d.dat`, 36 bytes | Three groups of 12 item ids, at `object 2 + 0x9d80`. | [Scenario files](scenario.md) |
| `dsc%02d.dat` | Section count, then 8 dwords a section. | [Scenario files](scenario.md) |
| `attr` records | One 4-byte terrain record per tile picture, from file `+0x11`. | [Map](map.md) |
| `object 1 + 0x20230`, 60 bytes | CD track numbers minus one. `object 1 + 0x20a30` reads `scenario * 2 + argument`. | [Turns](turns.md) |
| `object 2 + 0x53f0` (`0x4800`) and `object 2 + 0x43f0` (`0x1000`) | The two remap tables. Fight and map each have a file. | [Pictures](pictures.md) |
| `object 3 + 0xf`, 10 bytes | The key ring. `object 3 + 0x19` is the read index and `object 3 + 0x1d` is the other index. | [Text](text.md) |
| `object 2 + 0x9cb0`, `object 2 + 0x9c20`, `object 2 + 0x9c98` | One pointer triple per `object 2 + 0x9cdc` entry. `object 1 + 0x212b0` frees them. What they hold was not read. | [Gaps](gaps.md) |
| `object 1 + 0x4778`, four runs of 9 dwords | The four rectangles of one window-open frame. | [Pictures](pictures.md) |
| `object 2 + 0x39c` | The rand seed. The image dword is 1. | [Combat](combat.md) |

