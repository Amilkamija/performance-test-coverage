# Event A – Result and decision (HdrHistogram, held-out)

**Prediction (frozen before execution):** `Event_A/Prediction.md`, commit `4f7275f` (after `PRE_EVENT_A` = `3eaaedb`).
**Run:** Mateusz, 28 Oct 2026, macOS, Python 3.10.11, fresh venv.
**Raw evidence:** `Event_A/run_log.txt` (output and timing of each script, plus the diff check) and `Event_A/hdrhistogram_rows.txt` (HdrHistogram rows from the regenerated output CSVs).

## Frozen method applied

- The same four scripts as M2 (`analysis/1-Overlap-JMH.py`, `2-Overlap-JUnit.py`, `3-Coverage-JMH.py`, `4-Coverage-JUnit.py`), run unchanged, in the prescribed order, from `analysis/`.
- The same metrics and decision rule as M1/M2. Nothing was retuned after seeing the output.
- **Only deviation (same as M2):** the `numpy==1.24.2` pin conflicts with `imbalanced-learn==0.13.0`, so packages were installed from a copy of `requirements.txt` with `numpy==1.24.3`. The repository's `requirements.txt` was not edited.

## Result (frozen first result)

| Project | Methods | JMH cov % | JMH direct % | JMH overlap | Benchmarks | JUnit cov % | JUnit direct % | JUnit overlap | JUnit tests* |
|---|---|---|---|---|---|---|---|---|---|
| **HdrHistogram (Event A)** | 780 | **15.38** | 3.72 | **0.77** | 12 | **70.64** | 24.10 | **0.78** | 147 |
| byte-buddy (M2) | 5,046 | 2.12 | 0.46 | 1.00 | 39 | 12.80 | 9.63 | 0.70 | |
| fastjson (M2) | 17,524 | 0.37 | 0.02 | 0.91 | 4 | 34.54 | 27.84 | 0.15 | |
| commons-bcel (M2) | 3,132 | 12.64 | 3.38 | 0.09 | 3 | 34.71 | 4.25 | 0.66 | |
| SquidLib (M2) | 5,663 | 7.79 | 3.43 | 0.80 | 236 | 6.20 | 3.05 | 0.50 | |

All four regenerated output files match the supplied originals once CRLF/LF line endings are ignored (`git diff --ignore-cr-at-eol`: no differences; logged in `run_log.txt`).

\* `coverageJUnit.csv` counts 147 JUnit tests with coverage data. The 570 JUnit tests quoted in `Prediction.md` come from `inputs/Summary.csv` (timing summary), which is a different count.

## Comparison with M2

**Transfers**
- **The method.** The unchanged pipeline ran to completion on HdrHistogram and reproduced the supplied values exactly, with no change to the calculation rules. None of the challenge conditions in `Prediction.md` occurred.
- **JMH coverage remains low in absolute terms.** Most of HdrHistogram's methods (84.6%) are not reached by any benchmark.

**Does not transfer**
- **JMH coverage below JUnit coverage.** This held for 3 of 4 M2 projects (SquidLib was the exception, 7.79% vs 6.20%). It holds for HdrHistogram (15.38% vs 70.64%), so it is not a universal pattern.
- **JMH overlap above JUnit overlap.** This held for 3 of 4 M2 projects (commons-bcel was the exception). For HdrHistogram the two are effectively equal (0.77 vs 0.78).
- **Coverage levels.** HdrHistogram's JMH coverage (15.38%) is higher than every M2 project (maximum 12.64%), and its JUnit coverage (70.64%) is about double the highest M2 value (34.71%). HdrHistogram is also much smaller (780 methods vs 3,132–17,524).

**Strongest evidence:** the diff of the regenerated outputs against the supplied files shows no differences, and the HdrHistogram rows in `hdrhistogram_rows.txt` come from that same run.

## Decision

The prediction is confirmed and the M2 conclusion holds. The bounded coverage/overlap pipeline transfers unchanged to a held-out project from the replication package. Cross-project patterns in the values (which suite covers more, which has higher overlap) are project-specific and should not be generalised from the four-project M2 sample.

## Threats / limitations

- **Not blind.** HdrHistogram rows were already present in the M2 script outputs (M2 report, Fig. 3–4: 0.77 and 0.78), so its values were visible before Event A.
- **Same replication package.** HdrHistogram's data comes from the same supplied inputs and wrangling. This tests transfer of the analysis scripts, not of the data-collection pipeline.
- **Source version unknown.** The exact HdrHistogram source version could not be identified (see `Prediction.md`), so the frozen repository snapshot identifies the dataset.
- **Scope.** As in M2, only the coverage/overlap component is tested. The source-feature relationship (the modelling in RQ1's wording) was not run.
- **Run location.** The scripts were run in a clone of `4f7275f` inside an iCloud-synced folder. `git status` failed there (`mmap failed`), so the two evidence files were copied unchanged into a fresh clone at the same commit for committing.
