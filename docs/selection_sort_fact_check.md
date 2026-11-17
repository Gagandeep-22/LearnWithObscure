# Selection Sort fact check

Reviewed on 2026-11-17: `selection_sort_trace.py`, the Java listing it exports,
the complete `SelectionSortDemo` narration, and the storyboard.

The guarded Java algorithm is correct for non-null integer arrays. No sorting
defect was found. The explanation correctly teaches a complete minimum search
before each exchange, a growing fixed prefix, and the difference between
remembering an index and modifying the array.

## Verified claims

| Claim | Result |
| --- | --- |
| Main example `[5, 1, 4, 2, 8]` | `[1, 2, 4, 5, 8]`, 4 passes, 10 value comparisons, 2 swaps |
| Comparisons | Exactly `n * (n - 1) / 2`, including already sorted input; excludes loop/index tests |
| Swaps | At most `n - 1` for nonempty input; zero for empty or already sorted input |
| Array writes | Two per completed swap; at most `2 * (n - 1)` for nonempty input; zero for empty input |
| Running time | Best, average, and worst are `Theta(n^2)` as input size grows |
| Java auxiliary space | `O(1)`; the input array is rearranged in place |
| Stability | The ordinary long-swap implementation is unstable, even with strict `<` |
| Stability example | Comparing numeric keys only, `[2A, 2B, 1]` becomes `[1, 2B, 2A]` |
| Early exit | `[1, 3, 2]` has no swap in pass one but still needs pass two |
| Empty/singleton | Zero passes, value comparisons, swaps, and array-element reads |
| Reverse input `[4, 3, 2, 1]` | 6 comparisons and 2 swaps; reverse order need not attain the swap bound |
| Negatives/duplicates `[0, -2, 0, -5]` | `[-5, -2, 0, 0]`, 6 comparisons, 1 swap |
| Descending order | Reverse the comparison to select the maximum of the remaining suffix |

The general algorithm, quadratic comparison work, instability, and constant
auxiliary memory agree with Sedgewick and Wayne's
[Selection implementation](https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/Selection.java).
Their version performs an exchange on every outer iteration, including
self-exchanges. Our version skips the last destination and guards exchanges
with `minIndex != start`; its swap count is therefore different. The bounds
above follow from our exact loops and assignments.

## Precision corrections made

- Qualified the `n - 1` swap bound for nonempty arrays. Applied without that
  qualification, it incorrectly gives a negative upper bound when `n = 0`.
- Replaced the ambiguous spoken phrase “two times n minus one array writes”
  with two writes per swap and at most one swap per pass.
- Kept comparison narration on the comparison's effect; `minIndex` moves only
  when the following assignment executes.
- Hide `start` after the Java outer loop ends. The trace retains its final
  value for diagnostics, which is now documented. This follows Java's
  [scope rules for loop-local variables](https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.3).

The `O(1)` space claim describes the Java sorting method. The Python teaching
helper deliberately stores `Theta(n^2)` event snapshots, each containing `n`
array values, and therefore uses `Theta(n^3)` time and storage to materialize a
complete trace. This distinction is stated in the narration and helper docs.

The fewer-swaps motivation is a tradeoff, not a claim that Selection Sort is
always fastest or minimizes writes among every sorting algorithm.

## Verification and limits

- All 24 repository tests passed, including 364 exhaustive small arrays.
- An independent check passed 6,414 inputs: every permutation through length
  seven, plus 500 deterministic random arrays with negative and duplicate
  values through length thirty.
- Checked sorted results, comparison counts, swap bounds, fixed prefixes,
  separate swap assignments, and the stability counterexample.
- The Java listing was reviewed against the reference source. No Java
  compiler is installed in this environment, so Java bytecode execution was
  not performed; the executable model tests run in Python.
- The revised full silent render completed and decoded successfully. Reviewed
  the final Java variable display and complexity screen visually.

Four narration lines changed. Audio preparation will reuse the other cached
clips and generate the revised clips when valid Gemini access is available.
