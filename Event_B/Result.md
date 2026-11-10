# Event B – Result

Run: 10 Nov 2026, Mateusz's MacBook Air, roughly 67 minutes.
Prediction: `Event_B/Prediction.md`
Evidence: `Event_B/results.csv`, `Event_B/summary.csv`, `Event_B/run_log.txt`

## Results

| Size | Tests | Original | M4 version | M4 faster by | Memory |
|---|---|---|---|---|---|
| ¼× | 1,589 | 8 s | 0.03 s | 263× | same for both |
| ½× | 3,178 | 32 s | 0.05 s | 600× | same for both |
| 1× | 6,357 | 2 min 7 s | 0.10 s | 1,285× | same for both |
| 2× | 12,714 | 5 min 18 s | 0.12 s | 2,627× | same for both |
| 4× | 25,428 | over 15 min (stopped) | 0.25 s | – | original stopped |

## What happened
- Same answers: yes, every time both finished. At 4× the original could not finish, but the M4 version's answer matched the value worked out by hand.
- Speed: yes. The M4 version's lead grew from 263× to 2,627×. At 4× the original took over 15 minutes and the M4 version took a quarter of a second.
- One miss: the original was supposed to get at least 3× slower each time the size doubled from 1× up. From 1× to 2× it only got 2.5× slower. Below 1× it was almost exactly 4×. The reason is not known.
- Memory: both used roughly the same. The extra memory we predicted did not happen.

## Alternative responses considered
- Keep the M4 version unchanged (chosen). It gave the same answers, was much faster at every size and used about the same memory.
- Go back to the original pairwise version. Rejected: same answers but far slower, and it could not finish at 4×.
- Change the M4 version further (e.g. track which tests cover each method, or run projects in parallel). Rejected: nothing showed a problem that needed fixing, and running in parallel could change byte-buddy's answer from 0.70 to 0.09.
- Stop counting the blank entries as a "method". Rejected for now: it would change the metric and stop our numbers matching the original study.

## Decision
Keep the M4 change as it is. Nothing showed a reason to change it.

## Trade-offs we accept
- Above 2× the M4 version's answers cannot be checked against the original, because the original is too slow.
- byte-buddy has 4,414 rows with no recorded methods. Both versions count these as one shared "method". This is kept so our numbers still match the original study.
- Risk for the future: this only works because of how Python stores the blank entries. If the way the data is loaded or passed around changes (e.g. running projects in parallel), byte-buddy's answer could silently change from 0.70 to 0.09.

## Limitations

- The 2× and 4× sizes are copies, not real growth.
- Everything ran on one laptop in one session.
- byte-buddy's normal answer (0.70) was already known, and a short test run was done first, so the run was not blind.
- The memory measurement only counts Python's own memory use.
- One M4 run had a slow blip (0.07 s instead of 0.03 s).
- The first full run was stopped early and restarted from scratch.

## Conclusion
Event B supports the M4 change. As the test suite grew, the M4 version gave the same answers, got much faster than the original and used about the same memory. The prediction was partly confirmed: the same-answers and better-scaling parts held, but one speed threshold was missed (1× to 2×) and the extra memory we expected did not appear.