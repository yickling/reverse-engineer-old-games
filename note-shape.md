# Note shape

How to lay out the notes for one game. Read [LLMs.md](LLMs.md) for how to study the program. This file is only the shape of what that study writes. Copy this shape, not one game's filenames or systems. The root README is the index of analysed games. Do not name a game in this file.

A game folder is an index plus one file per system that program actually has. Do not create a file for a system it does not have. Merge two subjects into one file when the program does not separate them.

## Index

`<game>/README.md` is the index. It is not the whole study.

1. What the program is, in one paragraph. Say that decompiler output is not original source. Say that the game was not run, unless it was. If the outer loop was disassembled because no function existed there, say that and point at the session topic.
2. How to reopen the program from the file as shipped. Name the container, the bases or sections the file records, and the offset rule a finding uses. Do not name a machine path, a tool install, a temporary image, the base a tool chose, or a symbol the tool generated from that base. If the container had to be rebuilt before a tool could read it, say how, using only values from the file. Name the traps that move a tool onto the wrong body: a wrong entry, a selector that is not already a function, a handler the analyzer never turned into a function. One sentence on any program beside it that is not the game logic, such as an extender or a launcher.
3. A table of the topic files. One row is a link and one line for what that file holds. Under the table, tell the next session to add a finding to that file, and to add anything still unread to `<game>/gaps.md`, under the same heading. When the folder has scripts, name `<game>/scripts/` there and say what each script writes. The layout stays in the topic file.
4. `<game>/gaps.md` is the open list, kept for perusal. The index links to this file and does not copy it. The file opens with two verdicts, then the unread items under the same headings as the topic files. Keep both verdicts in this file. A separate document would hide the answer the open list is opened to find. A function worth opening is a row: the address, and what it is believed to be. A file or a field worth reading is a sentence that says where it was seen.

Each verdict is a heading whose first sentence is the answer.

- Reconstruction. The first sentence says whether the systems the notes describe can be rebuilt from those notes. When they cannot, the next sentence names the gap that has to be closed before they can. When they can, the next sentence names any piece still outside that reconstruction, and the gap before that piece can be rebuilt.
- Remake. The first sentence says whether a modernised remake can start from the notes. When it cannot, the next sentence names what still has to be deciphered before a design starts. When it can, the next sentence says the unread items under the later headings do not block that design.

## Topic file

The first paragraph links back to the index and repeats the caution: decompiler output is not original source, and the game was not run unless it was.

The rest is the findings for that subject. An observed claim names an offset from a base the file records, or a file offset in the program as shipped. It does not name a path, a tool install, or an address that exists only at the base a tool chose. A formula that should be reproducible is pseudocode, and it says which function the arithmetic was read from. When a claim belongs to another subject, link there instead of copying it. The topic file does not repeat the open list.

New findings go in the topic file. A newly seen address that was not read goes in `<game>/gaps.md`, under that topic's heading, and the row is removed when the finding is written. Do that in the files. A chat reply does not count, because the next session does not read the chat.

## Scripts

Write a script when a finding is a walk the next session would otherwise repeat: pulling frames out of a picture file, turning stored indexes into text, or dumping a table. A formula that fits in the topic file does not need one.

Put the script in `<game>/scripts/`. It takes the data directory as an argument. It does not embed a machine path, and it does not write into the local copy of the program. What it produces goes in `<game>/extract/`.

The topic file names the script and what it writes, and it keeps the layout the script implements. The notes do not paste the scenario text, pictures, or other copyrighted output the script writes.

## Subjects

Create a file when that subject is long enough to continue on its own. Name the file for the subject. These are the subjects, as questions. Skip one this program cannot answer.

| Subject | Question the file answers |
| --- | --- |
| Image | How is the program loaded, where is the real entry, and how do addresses map back to the file? |
| Session | What runs from startup until quit, and what does the outer loop do with the outcome of one visit? |
| Visit | What is one pass of play: input, selection, a turn or a phase, and how an outcome is raised for the session loop? |
| Content | What does one stage, scenario, or level load, and how are actors placed? |
| Space | How is the space drawn, how are its attributes encoded, and how does movement use them? |
| Actors | What record is kept per actor, at the offsets that were read? |
| Rules | What formula resolves an action, and how do attributes interact? |
| Pictures | What is a frame, what selects the next picture, what is a separate clip, and how are the pictures extracted? |
| Text | How is text stored, and how is it extracted? |
| Archives | How is packed content addressed? |
| Progress | How is progress written back, field by field? |

## Claims

- **Observed.** A decompiled body, a disassembly listing, or bytes in a file. Name the address or offset. Decompiler output is not original source. Say so when a path was disassembled because no function existed there.
- **Inferred.** A role guessed from how a field is written and read, such as calling a word "health" because attacks subtract from it. Say that it is an inference.
- **Unknown.** A file or a function that was seen and not read. List it in `<game>/gaps.md`. Do not fill the gap.

`__stash/` is the local copy of programs under study. Read it. Do not create or change files there. Notes go in the game folder. A repeatable extractor goes in `<game>/scripts/`. Every other produced file goes in `<game>/extract/`. Notes describe structure. They do not paste scenario text or other copyrighted writing.
