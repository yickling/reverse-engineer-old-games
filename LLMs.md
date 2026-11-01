# Analyzing a game in this repository

Instructions for a later session. Read this before studying a new game, and read that game's `README.md` before continuing one already started.

The goal is game design and construction: how the game is put together, how its content is represented, and how those pieces reach the player. Discover the structure this program actually has. Do not arrive with a genre in mind, and do not go looking for systems this game may not have.

## Where things go

- One folder per game. The entry note is `<game>/README.md`. A long study keeps topic files beside it. The README links to them and keeps how to reopen the binary and what is still open.
- The root [README.md](README.md) lists those notes. Add a row when a game folder gains one.
- `__stash/` holds local programs waiting to be studied. Leave it out of the notes, out of commits, and out of the license.
- This repository does not ship games. Keep binaries, archives, art, audio, and other assets on the machine doing the study. Notes describe structure. They do not paste assets, scenario text, or other copyrighted content.
- Original notes are [CC BY 4.0](LICENSE). That license does not cover any game.

## How the first study was done

Flame Dragon Plus is the worked example in [fdps/README.md](fdps/README.md). The sequence below is the method. The file formats and functions named there belong to that program only.

1. Identify the container before decompiling. `FDPS.EXE` is a Watcom Linear Executable wrapped in an MZ stub. The analysis tool rejected that container, so the session built a relocated flat image, recorded its base address and hash, and analyzed the image. The note says which file was actually opened.
2. Record the load map: object bases, the real entry, and how file offsets convert to addresses. A wrong entry left the startup function undiscovered. The outer loop was then read from disassembly and labeled as disassembly, separate from decompiled functions.
3. Follow filenames. Strings such as archive names and `printf` patterns lead to the loaders. Decompile the loader, then check the on-disk bytes against what it reads. A directory layout is settled when the reader's field offsets and a walk of the file agree, including a check that no member runs past end of file.
4. Follow use, not just storage. A sprite file's frame count came from the playback function (where it reads the count, how it advances, which byte marks an event), then the same layout was counted across the files.
5. Write the note so another session can resume: how to reopen the binary, addresses of the functions worth opening next, and an explicit list of what is still unknown.

## What to produce

Write `<game>/README.md` for a person who will make games and for a later session that will continue the study. Lead with what the program is and how to reopen it. Put a long topic in its own file next to the README, and link it from there. Cover, for whatever this game actually has:

- How a session starts and what the outer loop does.
- The records the game keeps for its actors, space, and rules, with offsets that were read in code.
- How content is stored, how it is loaded, and where it is used.
- How presentation is sequenced: what a frame is, what selects the next picture, what is a separate clip.
- How progress is written back to disk.
- A short table of functions worth opening next.
- What is still unknown.

Separate three kinds of claim:

- **Observed.** A decompiled body, a disassembly listing, or bytes in a file. Name the address or offset. Decompiler output is not original source. Say so when the startup path was disassembled because no function existed there.
- **Inferred.** A role guessed from how a field is written and read, such as calling a word "health" because attacks subtract from it. Say that it is an inference.
- **Unknown.** A file or function that was seen and not decoded. List it. Do not fill the gap.

Static analysis does not execute the game. Say that when no run was observed.

If a protection check appears, report the branch that exists. Do not write a bypass.

When the study of a binary session is finished, close it. Leave the note able to reopen the same image: path, hash, load address, and the address-to-offset rule.
