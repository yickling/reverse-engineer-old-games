# Procedure

The order of a study. How one reading is done is [LLMs.md](LLMs.md). The shape of what gets written is [note-shape.md](note-shape.md). The prompt to paste is [PROMPT.md](PROMPT.md).

The study is the gameplay: a battle, a town, a character, a visit, and a save. A body that only starts a device, walks the heap, or picks a gift the play does not depend on is discarded. It is listed in the ledger and it is not a gap.

A session does one task. The task is either the next phase whose done line is still open, or the one open item named in the prompt. Read the game folder before writing. Other work may already be in the files.

A finding goes in the topic file for that subject before the session ends. When the finding is something the player sees, the same paragraph says what they see, in the same terms as the offsets. An address, file, or field that was seen and not read goes in `<game>/gaps.md` under that topic. The row comes out when the topic file records the finding. Cite as [LLMs.md](LLMs.md) requires.

## 1. Open the study

Add a row to the root index. Create `<game>/README.md` and `<game>/gaps.md`. The index says what the program is, how to reopen it, and links the topic files that exist. The two verdicts are present. Their first sentences can still be unanswered.

Done when a later session can open the folder and know which file to read, and the game is named only in the root index and in that folder.

## 2. Load map

Identify the container. Record where code and data sit, the real entry, and how a wrong entry or a bare selector opens the wrong body. Name any program beside it that is not the game. Read startup far enough to find the outer loop, and stop at the functions that loop calls.

Done when a finding can be reopened from the file as shipped, and the outer loop's outcomes are named.

## 3. Session

Read the outer loop. Write what runs from startup until quit, and what that loop does with the outcome of one visit. A pointer table takes its name from the call site that uses it.

Done when the path from title to quit is in the session topic, and each outcome the loop branches on is named.

## 4. Archives and records

Follow filenames to the loaders. Check the reader's field offsets against a walk of the file, including that no member runs past the end. Write each record as the packed struct in [note-shape.md](note-shape.md). When the walk is one the next session would repeat, add the script that [note-shape.md](note-shape.md) describes.

Done when each container the play loads has a directory, and each record the program reads can be seen without reassembling it from the prose.

## 5. One visit

Read input, selection, the turn or the phase, and the function that raises an outcome for the session loop.

Done when one pass of play can be followed from the first command to the outcome, and the formulas that should be reproducible are pseudocode naming the function they were read from.

## 6. Content, space, and actors

Read what one stage loads, how actors are placed, how the space is drawn, and how movement uses it. Read the record kept per actor. Count a table across the files, not only in one file.

Done when a stage index selects its files, a placed actor can be found in the actor record, and the space topic says what a tile costs and what is drawn.

## 7. Rules and names

Read each action the player can order. An id the player uses, such as a spell, an item, or a status, gets its effect in the rules topic. When the program draws a label from an id, the id-to-name tables go in one names file. The names file does not hold the formula, and the rules topic points at it.

Done when each such id has an effect, and each label the program draws is in the names file.

## 8. Pictures, text, and progress

Read a frame, what selects the next picture, and what is a separate clip. Read how text is stored and drawn. Read how progress is written and how a load restores it, field by field. A file the archives do not hold is recorded as absent.

Done when a picture can be extracted again from the script, a string index can be found from the drawer, and a save can be laid back onto the records in the notes.

## 9. Ledger

Add a row for each body that was read: the address, whether it was decompiled or disassembled, and one line. The behavior stays in the topic file. Mark a discarded body in the ledger.

Done when a body named in a topic file has a ledger row, and a discarded body is not also a gap.

## 10. Close

Answer the two verdicts. The first sentence of each is the answer, in the shape in [note-shape.md](note-shape.md). The gameplay list holds only an address that changes play and was seen and not read. When that list is empty, its first sentence says the gameplay is complete.

A page built from the notes is not a finding. Where it still differs from the program is the second list in `<game>/gaps.md`. The program side is already in the topic file. Remove a line when the page matches.

The work log holds the questions still to read. Check an item when its finding is in the topic file and its gap row is gone.

Done when both verdicts are answered, the gameplay list is either empty or each remaining row is an unread gameplay address, and a page difference is not listed as an unread address.
