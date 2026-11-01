# Analyzing a game in this repository

Instructions for a later session. Read this before studying a new game, and read that game's `README.md` before continuing one already started. Then open only the topic file for the question in front of you.

The goal is game design and construction: how the game is put together, how its content is represented, and how those pieces reach the player. Discover the structure this program actually has. Do not arrive with a genre in mind, and do not go looking for systems this game may not have.

Write the notes in the shape in [note-shape.md](note-shape.md). [fdps/README.md](fdps/README.md) is one filled-in example of that shape. Copy the shape, not that game's filenames or systems.

Write every finding into those notes before the session ends. A reply in the chat is not a record. The next session will not see it. The same is true of an address that was seen and not read: it goes in the index, not only in the reply.

## Where things go

- One folder per game. The entry note is `<game>/README.md`.
- The root [README.md](README.md) lists those notes. Add a row when a game folder gains one.
- `__stash/` holds local programs waiting to be studied. Leave it out of the notes, out of commits, and out of the license. Do not name that directory in a note.
- This repository does not ship games. Keep binaries, archives, art, audio, and other assets on the machine doing the study. Notes describe structure. They do not paste assets, scenario text, or other copyrighted content.
- Original notes are [CC BY 4.0](LICENSE). That license does not cover any game.

## How to study

1. Identify the container before decompiling. If the tool rejects it, build whatever image the tool can open, and record the path, the hash, the load address, and the rule that turns an address into a file offset. The note says which file was actually opened. In the first study the executable was a Watcom Linear Executable inside an MZ stub, the tool rejected it, and the session analyzed a relocated flat image instead.
2. Record the load map: where code and data sit, the real entry, and how a wrong entry hides the startup function. Read the startup and the outer loop before naming anything those functions call. A pointer table's role is the call site that uses it. In the first study one table opens a scenario and a different table runs when that scenario ends; calling both "the scenario start" sent the next session to the wrong functions.
3. Follow filenames. Strings such as archive names and `printf` patterns lead to the loaders. Decompile the loader, then check the on-disk bytes against what it reads. A layout is settled when the reader's field offsets and a walk of the file agree, including a check that no member runs past the end of the file.
4. Follow use, not just storage. A count, a frame advance, or a formula comes from the function that plays it or applies it, then the same layout is counted across the files. Write a rule that should be reproducible as pseudocode. Say which function the arithmetic was read from.
5. Name each function and each global by what it does, and keep the address. The address is how the next session reopens it. The plain name is how a person making a game reads it. When the startup path was disassembled because no function existed there, say that. Decompiler output is not original source.
6. Stop when the question in front of you is answered. List what was seen and not read. Do not fill the gap.

A bare address that is not an existing function can be mistaken for a file offset and decompile the wrong body. Ask for a byte that already sits inside a function, or disassemble the bytes. Static analysis does not execute the game. Say that when no run was observed.

If a protection check appears, report the branch that exists. Do not write a bypass.

When the study of a binary session is finished, close it.

## What the notes look like

Follow [note-shape.md](note-shape.md). The index holds how to reopen the image and everything still unread. Each topic file holds one subject this program actually has. Mark each claim observed, inferred, or unknown, as that file describes.
