# Analyzing a game in this repository

Instructions for a later session. Read this before studying a new game, and read that game's `README.md` before continuing one already started. Then open only the topic file for the question in front of you.

The goal is game design and construction: how the game is put together, how its content is represented, and how those pieces reach the player. Discover the structure this program actually has. Do not arrive with a genre in mind, and do not go looking for systems this game may not have.

Write the notes in the shape in [note-shape.md](note-shape.md). Copy the shape, not one game's filenames or systems.

Write every finding into those notes before the session ends. A reply in the chat is not a record. The next session will not see it. The same is true of an address that was seen and not read: it goes in `<game>/gaps.md`, not only in the reply. Remove the row when the topic file records the finding.

## Where things go

- One folder per game. The entry note is `<game>/README.md`.
- The root [README.md](README.md) is the index of analysed games. Add a row when a game folder gains one. Do not name that game in any other top-level file.
- `__stash/` is the local copy of programs under study. Read it. Do not create or change files there. Leave it out of commits and out of the license. Do not name that directory in a note.
- Notes go in `<game>/`. A repeatable extractor goes in `<game>/scripts/`, as in [note-shape.md](note-shape.md). Every other file this repository produces goes in `<game>/extract/`. For every game, that directory stays on disk and is not committed.
- Notes describe structure. They do not paste scenario text or other copyrighted writing. Picture sheets kept for identification go in `<game>/extract/`.
- Original notes are [CC BY 4.0](LICENSE). That license does not cover any game.

## How to study

1. Identify the container before decompiling. If the tool cannot open it, build the image it can open from values the file itself records, and describe that derivation. Do not record a machine path, a tool install path, a temporary image, or the address the tool chose as its base. A finding names an offset from a base stored in the file, such as a section or object base in the header, or a file offset in the program as shipped. Do not cite a symbol the tool generated from its own base. In the first study the executable was a Watcom Linear Executable inside an MZ stub, the tool could not load it, and the notes cite offsets from the object bases in that header.
2. Record the load map: where code and data sit, the real entry, and how a wrong entry hides the startup function. Read the startup and the outer loop before naming anything those functions call. A pointer table's role is the call site that uses it. In the first study one table opens a scenario and a different table runs when that scenario ends; calling both "the scenario start" sent the next session to the wrong functions.
3. Follow filenames. Strings such as archive names and `printf` patterns lead to the loaders. Decompile the loader, then check the on-disk bytes against what it reads. A layout is settled when the reader's field offsets and a walk of the file agree, including a check that no member runs past the end of the file. Write that layout as the packed struct in [note-shape.md](note-shape.md). A person should be able to read the record without reassembling it from the prose.
4. Follow use, not just storage. A count, a frame advance, or a formula comes from the function that plays it or applies it, then the same layout is counted across the files. Write a rule that should be reproducible as pseudocode. Say which function the arithmetic was read from. When that walk is long enough that the next session would repeat it, write the script described in [note-shape.md](note-shape.md).
5. Name each function and each global by what it does, and keep the address. The address is how someone else reopens it, on any setup. Write it as an offset from a base the file itself records, or as a file offset in the program as shipped. Do not write the tool's load address, a symbol it generated from that address, a path on the machine, or a hash of an image that exists only locally. The plain name is how a person making a game reads it. When the startup path was disassembled because no function existed there, say that. Decompiler output is not original source.
6. Stop when the question in front of you is answered. List what was seen and not read. Do not fill the gap.

When asking a tool for a body, give it a byte that already sits inside the function. A bare address can be mistaken for a file offset and open the wrong body. Static analysis does not execute the game. Say that when no run was observed.

If a protection check appears, report the branch that exists. Do not write a bypass.

When the study of a binary session is finished, close it.

## What the notes look like

Follow [note-shape.md](note-shape.md). The index holds how to reopen the image and links to `<game>/gaps.md`. That file is the open list. It opens with two verdicts: whether a reconstruction is possible, and whether a modernised remake can start. Each verdict's first sentence is the answer. When the answer is no, the next sentence is the gap that blocks it. Then everything still unread. Each topic file holds one subject this program actually has. Mark each claim observed, inferred, or unknown, as that file describes.
