# Instructions for agents

Read [LLMs.md](LLMs.md) before studying a game, then that game's `README.md`. Write the notes in the shape in [note-shape.md](note-shape.md).

Notes cite offsets from a base the file records, or file offsets in the program as shipped. They do not cite a machine path, a tool install, a temporary image, or an address that exists only at the base a tool chose.

Write every finding into those files before you finish. A chat reply is not a record. The next session will not see it. An address, file, or field you saw and did not read goes in the game's `gaps.md`, under that topic's heading. Remove the row when the topic file records the finding. That file opens with two verdicts, in the shape in [note-shape.md](note-shape.md): whether a reconstruction is possible, and whether a modernised remake can start. The first sentence of each is the answer. When the answer is no, the next sentence is the gap that blocks it.

`__stash/` is the local copy of programs under study. Read it. Do not create or change files there. Notes go in the game folder. A repeatable extractor goes in `<game>/scripts/`, as in [note-shape.md](note-shape.md). Every other file goes in `<game>/extract/`.

The root README is the index of analysed games. Add a row there when a study starts. Do not name the game in any other top-level file.

The chat may summarize what was written. Do not end with the result only in the chat.
