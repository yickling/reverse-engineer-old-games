# Reverse engineering old games

Notes on how old games were built, written so we can reuse the ideas when making games.

The interest is game design and construction: how a session is put together, how the world and its actors are represented, how content is stored and brought on screen, how progress is saved, the mechanics and algorithms that resolve play, and the file formats that store the assets. Each game is a folder with its own `README.md`, so a later session can continue from it. Conclusions stay tied to a file offset or a function address, and observations stay separate from guesses.

Later analysis sessions follow [procedure.md](procedure.md). How one reading is done, including how a body is decompiled or disassembled, is [LLMs.md](LLMs.md). The shape of a game's notes is [note-shape.md](note-shape.md). Programs a later study can run on another game are in [tools/README.md](tools/README.md). Write findings into those notes. A chat reply is not a record the next session can read.

## How to start a session

[PROMPT.md](PROMPT.md) is the template. Copy the block, fill the two brackets, and paste it as the first message of a new session. One session does that one task.

Replace every `<game>` with the folder name, the same name you will add as a row in the index below. The program for that folder is already in the local copy. The note names the folder, not that copy.

The `Task` line is one of the two choices in the template, not both.

- A new game, or a game whose next phase in [procedure.md](procedure.md) is still open: `Start the study at the first open phase.` The session stops when that phase's done line is met.
- A game that already has notes: `Do the open item "<title>" and nothing else.` The title is the heading of one unchecked item in that game's work log, or one row still open in its `gaps.md`. The session does that item and stops.

When the session ends, the finding is in the topic file, and the game index states the coverage percentage for the gameplay mechanics and the presentation. The next session starts from a fresh paste, with the next phase or the next open item.

## Notes

| Note | Game | Gaps |
| --- | --- | --- |
| [fdps/README.md](fdps/README.md) | Flame Dragon Plus (炎龙骑士团外传), DOS | [fdps/gaps.md](fdps/gaps.md) |
| [xia/README.md](xia/README.md) | Xia (俠影記), DOS | [xia/gaps.md](xia/gaps.md) |

This table is the index of analysed games. A study adds a row here, a folder with a `README.md`, and a `gaps.md` in that folder. It does not name the game in any other top-level file.

## Local copies

`__stash/` is the local copy of programs under study. Read it. Do not create or change files there. It is not committed.

Notes go in the game folder. Extractor output goes in that game's `extract/`. For every game analysed here, that directory stays on disk and is not committed.

## Rights

Every game named here remains the property of its original owner. Titles, characters, and trademarks belong to those owners. All rights in the games are reserved by them.

The notes describe structure and design. They grant no right to copy, play, or redistribute a game. Extracted pictures kept for identification live in that game's `extract/` and are not covered by the license below.

## License

The original notes in this repository are released under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE).

That license covers this writing only. It does not cover any game, anything in `__stash/`, or the extracted pictures in a game's `extract/`.
