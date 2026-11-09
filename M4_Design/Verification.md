
# M4 Verification

CS4928 · Group G17 · Project P23

## End-to-end CSV comparison

The original and optimised JUnit overlap scripts were run against the same replication inputs. The resulting CSVs were identical across all 19 project rows, including the two-decimal overlap values. The normal output path is `outputs/Overlap_Ratios_Junit.csv`. The optimised comparison output was retained as [M4_Optimised_Junit.csv](evidence/M4_Optimised_Junit.csv).

## Unrounded equivalence

The [equivalence script](test_overlap_equivalence.py) imports the [original baseline](evidence/2-Overlap-JUnit-original.py) and the [optimised implementation](../analysis/2-Overlap-JUnit.py). It loads the [replication coverage input](../inputs/wrangled/u2m/00_combined_test_to_methods.csv), groups by project, and passes each project dataset to both implementations. It also passes six synthetic coverage datasets to both. Each check asserts that the absolute difference between the returned ratios is strictly less than `1e-12` before CSV formatting. The recorded run passed **25/25 checks**.

Run the check from the repository root with the project’s Python environment active.

**Windows:**

    python .\M4_Design\test_overlap_equivalence.py

**macOS/Linux:**

    python M4_Design/test_overlap_equivalence.py

The 19 passing projects were HdrHistogram, SquidLib, arrow, byte-buddy, cantaloupe, client_java, commons-bcel, fastjson, feign, imglib2, iri, jdbi, jgrapht, jooby, logbook, objenesis, panda, r2dbc-h2, and vert.x.

The six passing synthetic cases and their observed ratios were:

- **Single test**: 0.
- **No shared methods**: 0.
- **Shared method**: 1.
- **Identical coverage**: 1.
- **Mixed coverage**: one shared method out of three distinct methods, or 1/3.
- **Duplicate entries**: 1, with a repeated coverage row for one test and the same method covered by a second test.

The recorded run ended with `PASS: all original and optimised calculations match.`

## Runtime

The two elapsed script timings were recorded on the same laptop with Python 3.10.11.

- Original pairwise implementation: **402.3842379 seconds**.
- Optimised method-frequency implementation: **4.338967 seconds**.
- Observed speedup: **about 92.7×**, calculated by dividing the original runtime by the optimised runtime. This corresponds to about **98.9% less elapsed time** in the recorded comparison.

The M4 implementation preserved the reported RQ2 JUnit overlap values for all 19 projects, matched the baseline before rounding on all 25 checked datasets, and completed the recorded end-to-end run in less time. The [design decision](Decision.md) explains the algorithm and how the evidence relates to the historical replication freezes.


### Runtime measurement commands

Both implementations were measured using Windows PowerShell with the Python 3.10.11 virtual environment activated.

The original implementation was temporarily stored in the `analysis` directory during benchmarking. It was subsequently moved to `M4_Design/evidence/` to preserve the original version.

**To reproduce the measurements, first copy the original script back into the analysis directory.**

From the repository root, run:

```powershell
Copy-Item .\M4_Design\evidence\2-Overlap-JUnit-original.py .\analysis\2-Overlap-JUnit-original.py
```

Then navigate into the analysis directory:

```powershell
cd analysis
```

**Original pairwise implementation:**

```powershell
Measure-Command { python .\2-Overlap-JUnit-original.py }
```

**Optimised method-frequency implementation:**

```powershell
Measure-Command { python .\2-Overlap-JUnit.py }
```

PowerShell's `Measure-Command` records the elapsed execution time for each script.

The recorded M4 results were:

- Original implementation: **402.3842379 seconds**
- Optimised implementation: **4.338967 seconds**
- Observed speedup: **approximately 92.7×**

Both scripts use the same replication input data. They write to the same output path, so each execution overwrites the previous output CSV. The optimised output used for verification was separately preserved in `M4_Design/evidence/M4_Optimised_Junit.csv`.


