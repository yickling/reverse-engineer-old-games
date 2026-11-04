# Opening

Part of the [FDPS notes](README.md). This is the reconstruction of the two sequences that run before the first battle. Decompiled functions are Ghidra output, not original source. Nothing here was checked by running the game. The calls were read in [Session](session.md) and [Scenario files](scenario.md).

A reconstruction plays the studio logo, then the external movie, then the title. New game is title row 0. That row calls the opener below, and the map loop starts when the opener returns.

## Studio logo

On the title, before the menu, play `LOGO.SAF` from `MISC.VFS` under `DYNASTY.PAL`. Each frame waits for the vertical retrace. A key below `0x80`, or the last frame, leaves the clip. The frame hold is the `SAF` stepper in [Pictures](pictures.md). The frames are in [extract/videos](extract/videos/title/logo).

## External movie

`object 1 + 0x20cb0` then shuts sound down, blanks the palette, and passes three paths to `object 1 + 0x3df59`: `{prefix}\fd.exe`, `{prefix}\FD1.Vid`, and `{prefix}\FD1.Aud`. The prefix is the third string read from `Disk.no`, in [Session](session.md). When the menu counts out `0x5dc` ticks without a choice, the title returns to the logo and the number is 2, so the next movie is `FD2.Vid` and `FD2.Aud`.

`FD1.Vid`, `FD1.Aud`, `FD2.Vid`, and `FD2.Aud` were not among the data files. A reconstruction keeps this handoff. The frames and the audio stay outside until those files are present.

Sound then starts again with `0x19`, and the title asks the drive for CD track 2, in [File formats](formats.md). The menu is `StBoard.cel` and `StSel.cel`.

## New game

Title row 0 stores scenario index 0 and the roster threshold 0, calls the opener, and stores 1 at `object 2 + 0x158`.

The opener is `object 1 + 0x10e60`.

1. Append character 0. What the append writes is in [Units](units.md).
2. Load scenario 0 through `object 1 + 0x12720`. That clears the outcome, zeroes the camera and the cursor, and sets the turn counter to 1. Group 0 is already on the map, in [Scenario files](scenario.md).
3. Play `ICON00.DAT` from `ICONANI.VFS`. The program is below. It loads scenarios 32, 34, and 35, and its last load stores 0 again, so the battle that follows is still scenario 0.
4. Play `CHAPTER.SAF` under `CHAPTER.PAL`. `object 1 + 0x10c30` fades the palette sixteen steps down and sixteen steps back up.
5. On slot 2, store `0xb` at `+0x25` and 100 at `+0x40`.
6. Center slot 0 through `object 1 + 0x1d7e0`.

The visit in [Session](session.md) starts when this opener returns.

## `ICON00.DAT`

`object 1 + 0x11620` walks the file until opcode 0. There is no header. The lengths and the other opcodes are the table in [Scenario files](scenario.md). This file uses the ones below.

A walk redraws six frames, and on the sixth frame of each pass the named slots move one tile along the facing. A shake adds each signed pair to the camera and then writes the camera back. A text line is an id in that scenario's text block. The words are not copied here. A spawn is `object 1 + 0x13800` with the group and the argument. A unit is visible while bit 0 of byte `+5` is clear, in [Units](units.md). Music byte `n` asks for CD track `n + 1`, and `0xff` stops it. The wait on a fade is `object 1 + 0x2d0e0`, in [Session](session.md).

### Scenario 32

1. Ask for CD track 8.
2. Slide the camera to tile (1, 3).
3. Walk. Redraw each of the six frames 3 times, for 3 passes. slot 1 facing 1.
4. Walk. Redraw each of the six frames 3 times, for 1 pass. slot 0 facing 3.
5. Show scenario text 9.
6. Walk. Redraw each of the six frames 4 times, for 2 passes. slot 1 facing 2.
7. Set flag bit 0 on slot 1.
8. Stop the music.
9. Walk. Redraw each of the six frames 4 times, for 5 passes. slot 0 facing 3.
10. Ask for CD track 5.
11. Slide the camera to tile (2, 5).
12. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 0 facing 0.
13. Set flag bit 0 on slot 0.
14. Spawn group 2, argument 1.
15. Spawn group 1, argument 1.
16. Face, then redraw 10 times. slot 10 facing 2.
17. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 10 facing 2.
18. Face, then redraw 3 times. slot 10 facing 0.
19. Show scenario text 10.
20. Spawn group 4, argument 1.
21. Spawn group 5, argument 1.
22. Show scenario text 11.
23. Spawn group 6, argument 1.
24. Spawn group 7, argument 1.
25. Spawn group 8, argument 1.
26. Show scenario text 12.
27. Spawn group 9, argument 1.
28. Spawn group 10, argument 1.
29. Spawn group 11, argument 1.
30. Spawn group 3, argument 1.
31. Face, then redraw 20 times. slot 9 facing 1.
32. Face, then redraw 20 times. slot 9 facing 2.
33. Set flag bit 0 on slot 9.
34. Spawn group 12, argument 1.
35. Fade the palette down, waiting `object 1 + 0x2d0e0(40)`.
36. Slide the camera to tile (4, 46).
37. Slide the camera to tile (3, 45).
38. Slide the camera to tile (2, 44).
39. Slide the camera to tile (1, 43).
40. Face, then redraw 25 times. slot 20 facing 2.
41. Fade the palette up, waiting `object 1 + 0x2d0e0(80)`.
42. Face, then redraw 15 times. slot 20 facing 1.
43. Face, then redraw 15 times. slot 20 facing 3.
44. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 20 facing 0.
45. Set flag bit 0 on slot 20.
46. Fade the palette down, waiting `object 1 + 0x2d0e0(40)`.
47. Slide the camera to tile (0, 34).
48. Fade the palette up, waiting `object 1 + 0x2d0e0(40)`.
49. Spawn group 13, argument 1.
50. Walk. Redraw each of the six frames 4 times, for 2 passes. slot 21 facing 2.
51. Show scenario text 13.
52. Walk. Redraw each of the six frames once, for 4 passes. slot 21 facing 3.
53. Slide the camera to tile (5, 27).
54. Walk. Redraw each of the six frames once, for 6 passes. slot 21 facing 2.
55. Walk. Redraw each of the six frames once, for 4 passes. slot 21 facing 3.
56. Walk. Redraw each of the six frames once, for 4 passes. slot 8 facing 1.
57. Show scenario text 14.
58. Walk. Redraw each of the six frames once, for 1 pass. slot 8 facing 1.
59. Show scenario text 15.
60. Slide the camera to tile (8, 24).
61. Walk. Redraw each of the six frames once, for 5 passes. slot 8 facing 3.
62. Walk. Redraw each of the six frames once, for 1 pass. slot 8 facing 2.
63. Slide the camera to tile (13, 23).
64. Show scenario text 16.
65. Shake the camera, redrawing once per step, then put it back. (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0).
66. Slide the camera to tile (13, 24).
67. Walk. Redraw each of the six frames once, for 5 passes. slot 21 facing 3.
68. Walk. Redraw each of the six frames once, for 2 passes. slot 7 facing 2.
69. Walk. Redraw each of the six frames once, for 1 pass. slot 6 facing 2.
70. Walk. Redraw each of the six frames once, for 2 passes. slot 5 facing 2.
71. Walk. Redraw each of the six frames once, for 1 pass. slot 4 facing 2.
72. Walk. Redraw each of the six frames once, for 1 pass. slot 3 facing 2.
73. Walk. Redraw each of the six frames once, for 1 pass. slot 2 facing 2.
74. Face, then redraw 15 times. slot 8 facing 0.
75. Show scenario text 17.
76. Fade the palette down, waiting `object 1 + 0x2d0e0(40)`.
77. Set flag bit 0 on slot 2.
78. Set flag bit 0 on slot 3.
79. Set flag bit 0 on slot 4.
80. Set flag bit 0 on slot 5.
81. Set flag bit 0 on slot 6.
82. Set flag bit 0 on slot 7.
83. Set flag bit 0 on slot 8.
84. Set flag bit 0 on slot 10.
85. Set flag bit 0 on slot 11.
86. Set flag bit 0 on slot 12.
87. Set flag bit 0 on slot 13.
88. Set flag bit 0 on slot 14.
89. Set flag bit 0 on slot 15.
90. Set flag bit 0 on slot 16.
91. Set flag bit 0 on slot 17.
92. Set flag bit 0 on slot 18.
93. Set flag bit 0 on slot 19.
94. Set flag bit 0 on slot 21.
95. Spawn group 14, argument 1.
96. Slide the camera to tile (1, 3).
97. Fade the palette up, waiting `object 1 + 0x2d0e0(80)`.
98. Walk. Redraw each of the six frames 4 times, for 4 passes. slot 22 facing 3.
99. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 22 facing 1.
100. Spawn group 15, argument 0.
101. Face, then redraw 20 times. slot 22 facing 1.
102. Walk. Redraw each of the six frames once, for 2 passes. slot 23 facing 0.
103. Walk. Redraw each of the six frames once, for 2 passes. slot 23 facing 3.
104. Spawn group 16, argument 0.
105. Walk. Redraw each of the six frames once, for 3 passes. slot 24 facing 0.
106. Face, then redraw 15 times. slot 24 facing 3.
107. Spawn group 17, argument 0.
108. Walk. Redraw each of the six frames once, for 1 pass. slot 25 facing 0.
109. Walk. Redraw each of the six frames once, for 1 pass. slot 25 facing 3.
110. Spawn group 18, argument 0.
111. Face, then redraw 14 times. slot 26 facing 3.
112. Show scenario text 18.
113. Walk. Redraw each of the six frames once, for 3 passes. slot 24 facing 3.
114. Walk. Redraw each of the six frames once, for 2 passes. slot 25 facing 3.
115. Fade the palette down, waiting `object 1 + 0x2d0e0(10)`.

### Scenario 34

1. Spawn group 1, argument 1.
2. Face, then redraw once. slot 0 facing 2.
3. Spawn group 2, argument 1.
4. Spawn group 3, argument 1.
5. Spawn group 4, argument 1.
6. Face, then redraw once. slot 3 facing 2.
7. Spawn group 5, argument 1.
8. Face, then redraw once. slot 4 facing 2.
9. Spawn group 6, argument 1.
10. Face, then redraw once. slot 5 facing 2.
11. Spawn group 7, argument 1.
12. Face, then redraw once. slot 6 facing 2.
13. Spawn group 8, argument 1.
14. Face, then redraw once. slot 7 facing 2.
15. Spawn group 9, argument 1.
16. Face, then redraw once. slot 8 facing 2.
17. Slide the camera to tile (2, 0).
18. Fade the palette up, waiting `object 1 + 0x2d0e0(120)`.
19. Face, then redraw 25 times. slot 2 facing 2.
20. Face, then redraw 25 times. slot 2 facing 3.
21. Show scenario text 9.
22. Slide the camera to tile (0, 0).
23. Slide the camera to tile (2, 0).
24. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 3 facing 2.
25. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 4 facing 2.
26. Spawn group 10, argument 1.
27. Spawn group 11, argument 1.
28. Spawn group 12, argument 1.
29. Spawn group 13, argument 1.
30. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 3 facing 0.
31. Face, then redraw 10 times. slot 3 facing 2.
32. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 4 facing 0.
33. Face, then redraw 10 times. slot 4 facing 2.
34. Face, then redraw 25 times. slot 2 facing 2.
35. Face, then redraw 10 times. slot 2 facing 2.
36. Shake the camera, redrawing once per step, then put it back. (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0) (+1,+0) (+1,-1) (+0,-1) (+0,+0) (-1,+0) (-1,+1) (+0,+1) (+0,+0).
37. Set flag bit 0 on slot 1.
38. Play `Icon0003.saf` on the map.
39. Walk. Redraw each of the six frames 2 times, for 1 pass. slot 3 facing 2.
40. Walk. Redraw each of the six frames 2 times, for 1 pass. slot 4 facing 2.
41. Walk. Redraw each of the six frames 2 times, for 1 pass. slot 7 facing 2.
42. Face, then redraw 10 times. slot 7 facing 1.
43. Face, then redraw 10 times. slot 7 facing 3.
44. Face, then redraw 10 times. slot 7 facing 2.
45. Show scenario text 10.
46. Play `Icon0002.saf` on the map.
47. Walk. Redraw each of the six frames 2 times, for 1 pass. slot 8 facing 0.
48. Face, then redraw 10 times. slot 8 facing 2.
49. Play `Icon0001.saf` on the map.
50. Walk. Redraw each of the six frames 2 times, for 1 pass. slot 3 facing 0.
51. Face, then redraw 10 times. slot 3 facing 2.
52. Play `Icon0000.saf` on the map.
53. Play `Icon0005.saf` on the map.
54. Spawn group 14, argument 1.
55. Play `Icon0004.saf` on the map.
56. Spawn group 15, argument 1.
57. Play `Icon0006.saf` on the map.
58. Spawn group 16, argument 1.
59. Set flag bit 0 on slot 9.
60. Set flag bit 0 on slot 10.
61. Set flag bit 0 on slot 11.
62. Set flag bit 0 on slot 12.
63. Show scenario text 11.
64. Move the camera and the cursor to tile (2, 0).
65. Set flag bit 0 on slot 2.
66. Play `Icon0007.saf` on the map.
67. Set flag bit 0 on slot 14.
68. Spawn group 19, argument 1.
69. Show scenario text 12.
70. Move the camera and the cursor to tile (2, 0).
71. Clear flag bit 0 on slot 14, and clear its six count bytes.
72. Set flag bit 0 on slot 16.
73. Play `Icon0008.saf` on the map.
74. Clear flag bit 0 on slot 2, and clear its six count bytes.
75. Show scenario text 13.
76. Play `Icon0001.saf` on the map.
77. Play `Icon0002.saf` on the map.
78. Walk. Redraw each of the six frames once, for 4 passes. slot 1 facing 0, slot 3 facing 0, slot 4 facing 0.
79. Play `Icon0000.saf` on the map.
80. Walk. Redraw each of the six frames once, for 4 passes. slot 5 facing 0, slot 6 facing 0, slot 7 facing 0, slot 8 facing 0.
81. Play `Icon0001.saf` on the map.
82. Walk. Redraw each of the six frames once, for 3 passes. slot 0 facing 0.
83. Fade the palette down, waiting `object 1 + 0x2d0e0(20)`.
84. Move the camera and the cursor to tile (8, 10).
85. Walk. Redraw each of the six frames once, for 3 passes. slot 0 facing 1.
86. Walk. Redraw each of the six frames once, for 4 passes. slot 5 facing 2, slot 6 facing 2, slot 7 facing 2, slot 8 facing 2.
87. Walk. Redraw each of the six frames once, for 4 passes. slot 1 facing 2, slot 3 facing 2, slot 4 facing 2.
88. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
89. Play `Icon0010.saf` on the map.
90. Fade the palette down, waiting `object 1 + 0x2d0e0(10)`.
91. Set flag bit 0 on slot 0.
92. Set flag bit 0 on slot 2.
93. Set flag bit 0 on slot 3.
94. Set flag bit 0 on slot 4.
95. Set flag bit 0 on slot 5.
96. Set flag bit 0 on slot 6.
97. Set flag bit 0 on slot 7.
98. Set flag bit 0 on slot 8.
99. Set flag bit 0 on slot 13.
100. Set flag bit 0 on slot 14.
101. Set flag bit 0 on slot 15.
102. Spawn group 18, argument 1.
103. Spawn group 17, argument 1.
104. Move the camera and the cursor to tile (10, 28).
105. Face, then redraw once. slot 17 facing 1.
106. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
107. Face, then redraw 25 times. slot 17 facing 1.
108. Show scenario text 14.
109. Face, then redraw 25 times. slot 17 facing 0.
110. Show scenario text 15.
111. Face, then redraw 25 times. slot 17 facing 2.
112. Show scenario text 16.
113. Face, then redraw 5 times. slot 17 facing 1.
114. Show scenario text 17.
115. Walk. Redraw each of the six frames once, for 4 passes. slot 17 facing 1.
116. Move the camera and the cursor to tile (10, 24).
117. Show scenario text 17.
118. Walk. Redraw each of the six frames once, for 6 passes. slot 17 facing 2.
119. Fade the palette down, waiting `object 1 + 0x2d0e0(10)`.
120. Move the camera and the cursor to tile (10, 20).
121. Face, then redraw 15 times. slot 17 facing 0.
122. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
123. Face, then redraw 15 times. slot 17 facing 1.
124. Show scenario text 17.
125. Face, then redraw 15 times. slot 17 facing 2.
126. Face, then redraw 15 times. slot 17 facing 3.
127. Show scenario text 17.
128. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 17 facing 1.
129. Face, then redraw 15 times. slot 17 facing 2.
130. Face, then redraw 15 times. slot 17 facing 3.
131. Face, then redraw 15 times. slot 17 facing 1.
132. Show scenario text 18.
133. Walk. Redraw each of the six frames once, for 3 passes. slot 17 facing 1.
134. Fade the palette down, waiting `object 1 + 0x2d0e0(10)`.
135. Move the camera and the cursor to tile (2, 20).
136. Face, then redraw once. slot 17 facing 1.
137. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
138. Show scenario text 19.
139. Walk. Redraw each of the six frames once, for 3 passes. slot 17 facing 1.
140. Face, then redraw 25 times. slot 17 facing 0.
141. Face, then redraw 25 times. slot 17 facing 2.
142. Show scenario text 20.
143. Face, then redraw 2 times. slot 17 facing 1.
144. Face, then redraw 15 times. slot 17 facing 0.
145. Walk. Redraw each of the six frames once, for 1 pass. slot 17 facing 0.
146. Set flag bit 0 on slot 17.
147. Set flag bit 0 on slot 18.
148. Spawn group 20, argument 1.
149. Face, then redraw 25 times. slot 19 facing 1.
150. Walk. Redraw each of the six frames once, for 6 passes. slot 19 facing 0.
151. Stop the music.
152. Fade the palette down, waiting `object 1 + 0x2d0e0(100)`.

### Scenario 35

1. Ask for CD track 6.
2. Move the camera and the cursor to tile (0, 11).
3. Face, then redraw once. slot 1 facing 0.
4. Spawn group 1, argument 1.
5. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
6. Face, then redraw 2 times. slot 1 facing 0.
7. Walk. Redraw each of the six frames once, for 1 pass. slot 1 facing 0.
8. Set flag bit 0 on slot 1.
9. Spawn group 2, argument 1.
10. Fade the palette down, waiting `object 1 + 0x2d0e0(100)`.
11. Move the camera and the cursor to tile (0, 20).
12. Face, then redraw once. slot 2 facing 0.
13. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
14. Face, then redraw 10 times. slot 2 facing 0.
15. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 2 facing 0.
16. Fade the palette down, waiting `object 1 + 0x2d0e0(100)`.
17. Set flag bit 0 on slot 2.
18. Move the camera and the cursor to tile (0, 29).
19. Face, then redraw once. slot 3 facing 0.
20. Fade the palette up, waiting `object 1 + 0x2d0e0(10)`.
21. Show scenario text 4.
22. Spawn group 3, argument 1.
23. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 3 facing 3.
24. Face, then redraw 10 times. slot 3 facing 0.
25. Face, then redraw 10 times. slot 3 facing 2.
26. Face, then redraw 10 times. slot 3 facing 3.
27. Spawn group 4, argument 1.
28. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 4 facing 1.
29. Show scenario text 5.
30. Set flag bit 0 on slot 3.
31. Set flag bit 0 on slot 4.
32. Fade the palette down, waiting `object 1 + 0x2d0e0(80)`.
33. Move the camera and the cursor to tile (6, 0).
34. Face, then redraw once. slot 0 facing 2.
35. Fade the palette up, waiting `object 1 + 0x2d0e0(40)`.
36. Face, then redraw 20 times. slot 0 facing 2.
37. Face, then redraw 10 times. slot 0 facing 0.
38. Face, then redraw 10 times. slot 0 facing 1.
39. Show scenario text 9.
40. Walk. Redraw each of the six frames 4 times, for 4 passes. slot 0 facing 1.
41. Show scenario text 10.
42. Move the camera and the cursor to tile (2, 0).
43. Walk. Redraw each of the six frames once, for 1 pass. slot 0 facing 0.
44. Walk. Redraw each of the six frames once, for 6 passes. slot 0 facing 1.
45. Face, then redraw 10 times. slot 0 facing 2.
46. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 0 facing 2.
47. Face, then redraw 10 times. slot 0 facing 2.
48. Walk. Redraw each of the six frames 4 times, for 2 passes. slot 0 facing 2.
49. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 0 facing 1.
50. Face, then redraw 10 times. slot 0 facing 1.
51. Show scenario text 6.
52. Face, then redraw 10 times. slot 0 facing 0.
53. Show scenario text 11.
54. Fade the palette down, waiting `object 1 + 0x2d0e0(200)`.

### Scenario 0

1. Move the camera and the cursor to tile (10, 16).
2. Face, then redraw once. slot 0 facing 2.
3. Ask for CD track 9.
4. Fade the palette up, waiting `object 1 + 0x2d0e0(200)`.
5. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 0 facing 2.
6. Show scenario text 9.
7. Walk. Redraw each of the six frames 4 times, for 2 passes. slot 0 facing 2.
8. Show scenario text 10.
9. Face, then redraw 10 times. slot 0 facing 3.
10. Face, then redraw 10 times. slot 0 facing 1.
11. Face, then redraw 10 times. slot 0 facing 0.
12. Face, then redraw 10 times. slot 0 facing 2.
13. Stop the music.
14. Move the camera and the cursor to tile (10, 0).
15. Spawn group 2, argument 0.
16. Ask for CD track 10.
17. Walk. Redraw each of the six frames once, for 1 pass. slot 1 facing 0.
18. Show scenario text 11.
19. Move the camera and the cursor to tile (8, 0).
20. Play `Icon0011.saf` on the map.
21. Spawn group 1, argument 0.
22. Face, then redraw 5 times. slot 0 facing 0.
23. Move the camera and the cursor to tile (8, 6).
24. Walk. Redraw each of the six frames once, for 4 passes. slot 2 facing 0.
25. Move the camera and the cursor to tile (8, 10).
26. Walk. Redraw each of the six frames 2 times, for 2 passes. slot 2 facing 0.
27. Face, then redraw 20 times. slot 2 facing 0.
28. Walk. Redraw each of the six frames 4 times, for 2 passes. slot 2 facing 0.
29. Set flag bit 0 on slot 2.
30. Play `Icon0012.saf` on the map.
31. Move the camera and the cursor to tile (8, 1).
32. Place slot 2 at tile (14, 14), facing 0.
33. Clear flag bit 0 on slot 2, and clear its six count bytes.
34. Walk. Redraw each of the six frames once, for 2 passes. slot 1 facing 1.
35. Walk. Redraw each of the six frames once, for 3 passes. slot 1 facing 0.
36. Show scenario text 12.
37. Spawn group 3, argument 0.
38. Face, then redraw 20 times. slot 4 facing 0.
39. Spawn group 4, argument 0.
40. Face, then redraw 20 times. slot 4 facing 0.
41. Spawn group 5, argument 0.
42. Face, then redraw 20 times. slot 4 facing 0.
43. Move the camera and the cursor to tile (8, 11).
44. Walk. Redraw each of the six frames once, for 2 passes. slot 0 facing 2.
45. Walk. Redraw each of the six frames 4 times, for 1 pass. slot 0 facing 2.
46. Show scenario text 13.

Opcode 0 ends the file. The opener then plays the chapter card, writes slot 2, centers slot 0, and returns into the first battle.
