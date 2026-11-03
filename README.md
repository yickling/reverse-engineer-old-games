# Reverse engineering old games

Notes on how old games were built, written so we can reuse the ideas when making games.

The interest is game design and construction: how a session is put together, how the world and its actors are represented, how content is stored and brought on screen, and how progress is saved. Each game is a folder with its own `README.md`, so a later session can continue from it. Conclusions stay tied to a file offset or a function address, and observations stay separate from guesses.

Later analysis sessions should follow [LLMs.md](LLMs.md) and [AGENTS.md](AGENTS.md). The shape of a game's notes is [note-shape.md](note-shape.md). Write findings into those notes. A chat reply is not a record the next session can read.

## Notes

| Note | Game | Gaps |
| --- | --- | --- |
| [fdps/README.md](fdps/README.md) | Flame Dragon Plus (炎龙骑士团外传), DOS | [fdps/gaps.md](fdps/gaps.md) |

This table is the index of analysed games. A study adds a row here, a folder with a `README.md`, and a `gaps.md` in that folder. It does not name the game in any other top-level file.

## Local copies

`__stash/` is the local copy of programs under study. Read it. Do not create or change files there. It is not committed.

Notes go in the game folder. Extractor output goes in that game's `extract/`.

## Rights

Every game named here remains the property of its original owner. Titles, characters, and trademarks belong to those owners. All rights in the games are reserved by them.

The notes describe structure and design. They grant no right to copy, play, or redistribute a game. Extracted pictures kept for identification live in that game's `extract/` and are not covered by the license below.

## License

The original notes in this repository are released under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE).

That license covers this writing only. It does not cover any game, anything in `__stash/`, or the extracted pictures in a game's `extract/`.
