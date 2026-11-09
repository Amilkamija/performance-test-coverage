
# M4 Design Decision

CS4928 · Group G17 · Project P23

## RQ2 and scope

For RQ2, the JUnit overlap calculation measures how much of each project's covered method set is exercised by more than one distinct JUnit test. The M4 design question was whether we could compute the same metric faster while preserving comparability with the replication results. During M2, the JUnit overlap script was interrupted or exceeded the time limit in two of four recorded runs. Its pairwise test comparisons presented a potential performance limitation, which we investigated during M4.

For each project, the overlap ratio is the number of distinct methods covered by at least two distinct tests divided by the total number of distinct methods covered by any test. Coverage is represented as a set per test, so repeated records for the same test and method contribute once. The function returns zero for fewer than two tests or an empty covered-method set.

## Alternatives considered

- **A: Retain pairwise intersections:** Keep the replicated implementation, which intersects each unordered pair of test coverage sets and accumulates the distinct shared methods. This is straightforward to trace back to the baseline, but it processes every test pair even when their coverage is disjoint.
- **B: Count distinct tests per method:** Update a Python `Counter` once per method in each test's coverage set. Count methods with frequency at least two for the numerator and use the number of counter keys for the denominator. This removes pair enumeration and keeps the implementation local to the overlap function.
- **C: Build a method-to-tests index:** Store the set of covering test names for each method and use the size of each set. This also removes pair enumeration and can identify which tests share a method, but retaining those associations adds storage and is unnecessary for the ratio

## Decision and rationale

We selected alternative B, a Substitute Algorithm refactoring, for [the active JUnit analysis script](../analysis/2-Overlap-JUnit.py). A method appears in the union of pairwise intersections exactly when it belongs to at least two distinct test coverage sets. The keys in the counter are exactly the union of all coverage sets. These two facts preserve both parts of the ratio. The change is confined to the overlap calculation and its standard-library import. The script continues to use the same input files and writes the same project-level CSV schema with two-decimal formatting.

We left `1-Overlap-JMH.py` unchanged because it already completed within seconds during M2. Combining the JMH and JUnit scripts into a shared calculation was also considered, but we decided against a wider refactoring because it would introduce unnecessary changes for this optimisation.

## Complexity and trade-offs

For one project, let *T* be the number of tests, *K* the maximum number of methods covered by any test, *E* the number of distinct test–method associations, and *U* the number of distinct covered methods. After grouping coverage into sets, the original implementation visits *T(T − 1)/2* pairs. With expected constant-time hash operations, the pairwise phase is bounded by O(T²K) for nonempty coverage sets.

The frequency-based calculation takes expected O(E + U) time after grouping. This describes the overlap calculation separately from CSV processing and grouping.

The counter holds O(U) entries alongside the grouped sets. The baseline also uses O(U) auxiliary space for its accumulated intersections and union, while a method-to-tests index would store O(E + U) entries and associations. A counter stores an integer for each key, and the measurements do not quantify peak memory.

## Evidence

The recorded same-laptop run under Python 3.10.11 went from 402.3842379 seconds to 4.338967 seconds, about 92.7× faster. The CSV comparison matched all 19 projects and all 25 unrounded checks passed. Each timing is a single observation. See [Verification.md](Verification.md) for the procedure and evidence. The original JUnit overlap script is included in the [Original JUnit overlap script](evidence/2-Overlap-JUnit-original.py) so the comparison can be rerun from that version.
