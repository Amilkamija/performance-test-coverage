# Event B – Prediction before execution

What was tested:Jakub’s faster M4 overlap script against the original script when the JUnit test suite gets bigger. Both scripts were used exactly as frozen at PRE_EVENT_B (58976b3).


Prediction:
The original will slow down a lot as the number of tests grows. M4 version will cope much better and give exactly the same answers, however it might use a bit more memory.

How we tested it:
Project: byte-buddy, the biggest test suite in the data (6,357 tests).
Sizes: ¼, ½, 1, 2 and 4 times the real number of tests. Smaller sizes are random samples of the tests. Bigger sizes are copies of the suite with renamed tests and methods.
Measured for each size:
time: 5 runs of M4 script and 3 of the original, using the middle value
memory: one separate run of each
the answer each version gives
Time limit: any run of the original over 15 minutes is stopped.

If the prediction is right:
Both versions give the same answer at every size where both finish.
M4 lead over the original grows as the size grows.
From 1× upwards, the original gets at least 3× slower each time the size doubles, and M4’s at most 2.5× slower.
If M4's version uses more memory, that part of the prediction is confirmed.

What would make us rethink M4’s change:

different answers
M4 not scaling better
M4 using more than 1.5× the memory
