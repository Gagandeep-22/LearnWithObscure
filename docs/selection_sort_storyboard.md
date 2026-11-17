# Selection Sort lesson plan

The audience should leave able to trace Selection Sort, explain why each pass
fixes one position, connect its Java statements to array changes, and discuss
its cost and limitations. Preserve the lavender palette, short speaker-tagged
captions, distinct character voices, and voice-led timing established in
Binary Search and Bubble Sort.

## Coverage carried forward

| Existing lesson feature | Selection Sort treatment |
| --- | --- |
| Concrete learner problem before explanation | Sort `[5, 1, 4, 2, 8]` when comparisons are cheap but moving values is expensive |
| Visual explanation before code | Scan for a minimum, remember its index, swap after the scan |
| Ascending and descending order | Select the minimum with `<`; select the maximum with `>` |
| Java connected to state | Highlight each executed statement; show pointers, comparisons, and array assignments |
| Learner questions that reveal reasoning | Why scan after finding a smaller value? Why reset the candidate? Can one no-swap pass end the sort? |
| Complexity overview followed by reasoning | Quadratic time for all input orders; exact comparison count; bounded swaps; constant extra space |
| Useful context and limitations | Simple in-place sorting, fewer writes, quadratic comparisons, instability |
| Complete usable implementation | Full Java method, call, and expected output |
| Character-led close | Obscure explains the idea back and invites the audience to keep learning |

## Storyboard

| Beat | Learner question or purpose | What appears and changes | Conversation |
| --- | --- | --- | --- |
| Hook | Can we sort this array while keeping swaps down? | Unsorted array and goal: ascending order with fewer expensive moves | Obscure states the problem without proposing the algorithm; Zeno introduces Selection Sort and its one-swap-per-pass limit |
| Visual vocabulary | What do the three pointers mean? | Destination `start`, scanning `scan`, and candidate `minIndex`; fixed array indices | Zeno distinguishes an index from the value stored there |
| First pass | Is the first smaller value automatically the minimum? | Start with 5 as candidate; discover 1; continue through 4, 2, 8; swap only after scanning | Obscure predicts; Zeno explains “smallest seen so far” |
| Remaining passes | Why can we leave the prefix alone? | `[1, 5, 4, 2, 8]` becomes `[1, 2, 4, 5, 8]`; later destinations need no swap | Obscure identifies the next minimum; Zeno explains the invariant |
| Order reversal | What about largest to smallest? | `<` selects a minimum; `>` selects a maximum | Obscure connects the comparison change to Bubble Sort |
| Java trace | How do those variables produce the animation? | Statement highlight and immutable event snapshots; separate assignments during swaps | Explain the first occurrence fully, then use contextual remarks and readable silent steps |
| Early-exit challenge | No swap means sorted, right? | `[1, 3, 2]` needs no swap at `start = 0`, but its suffix remains unsorted | Zeno distinguishes a correct destination from a fully sorted array |
| Additional cases | What changes with input order or unusual values? | Sorted, reverse, duplicate, negative, empty, and single-element examples | Let Obscure make predictions and explain the result back |
| Stability | Does strict `<` preserve equal-item order? | `[2A, 2B, 1]` becomes `[1, 2B, 2A]` after the first swap | Obscure spots the reversal; Zeno defines stability using the labels |
| Complexity overview | What are the costs? | Best/average/worst `O(n^2)`, auxiliary `O(1)`, at most `n - 1` swaps | Zeno separates finding a value from moving a value |
| Time derivation | Why is sorted input still quadratic? | `(n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2`; five values need ten comparisons | Obscure asks whether fewer swaps also means fewer comparisons |
| Space and practical guidance | Where is it useful? | Fixed helper variables, advantages/limitations, comparison with Bubble Sort | Zeno discusses tiny inputs and cases where writes matter, with appropriate limits |
| Complete Java | Can I run this myself? | Readable method and usage/output pages | Relate bounds and swap guard to the trace |
| Recap and close | What should we remember? | Select, finish scanning, swap if needed, advance | Obscure summarizes, then makes a short natural channel invitation |

## Dialogue direction

Obscure is a learning partner, never a punchline. His questions should change
what Zeno explains next. Include predictions with an actual pause before the
answer, rather than asking a question and immediately answering it in the same
line. Zeno answers directly, demonstrates the evidence, then adds dry humor
only where it reinforces the idea.

For example, a minimum candidate is provisional: “Smallest so far. It has not
survived the whole interview yet.” A memory joke can reinforce that changing
`minIndex` only changes the remembered position; the array has not moved.
Avoid recurring catchphrases, repeated “Exactly!”, and a joke on every beat.
Use different narration for a new candidate, a rejected candidate, a finished
scan, a skipped swap, and a boundary check. Keep captions shorter than speech.

## Technical and visual checks

- Main example after each completed pass: `[1, 5, 4, 2, 8]`,
  `[1, 2, 4, 5, 8]`, `[1, 2, 4, 5, 8]`, `[1, 2, 4, 5, 8]`.
- It makes ten value comparisons and two swaps. The last element needs no
  separate pass because every earlier destination has been fixed.
- Reset `minIndex = start` each pass; initialize `scan` to `start + 1`;
  scan while `scan < arr.length`; advance the destination while
  `start < arr.length - 1`. In the complexity formulas, `n` means `arr.length`.
- A scan changes the candidate index, not the input array. Do not show a
  final minimum before the entire suffix has been considered.
- A swap is guarded by `minIndex != start`. In the Java trace, show the
  temporary value first, then the destination assignment (including its
  temporary duplicate), then the assignment that completes the swap.
- A no-swap pass proves only that its destination was already correct.
  `[1, 3, 2]` is the explicit counterexample to reusing Bubble Sort's exit rule.
- For nonempty input, at most `n - 1` swaps occur; empty input makes zero.
  Each completed swap writes two array slots, so the bound is `2 * (n - 1)`
  array writes for nonempty input and zero for empty input. Assignments to
  local helper variables are not counted as array writes.
  Sorted input still makes `n(n - 1) / 2` value comparisons but zero guarded
  swaps. A reverse input does not necessarily require `n - 1` swaps; that is
  an upper bound, not a claim about every difficult input.
- Negatives follow the same comparison rule. Equal values do not replace the
  current candidate under strict `<`. Empty and single-element inputs perform
  no comparisons or swaps and require no special array access.
- Ordinary swap-based Selection Sort is unstable: `[2A, 2B, 1]` becomes
  `[1, 2B, 2A]`. Compare numeric keys only; the letters identify original order.
- The algorithm uses `O(1)` auxiliary space. The animation's trace snapshots
  are teaching infrastructure, not storage required by the Java algorithm.
  The Python trace builder stores `Theta(n^2)` snapshots of `n` values, so
  building that complete trace takes `Theta(n^3)` time and storage. Its final
  `start` value is diagnostic; hide the Java pointer and badge once it leaves
  scope after the outer loop.
- Few swaps can be useful when writes cost more than reads, but quadratic
  comparison work still limits scale. Avoid promising that this is the best
  production sort for a particular device or workload.
- Review pointer collisions, fixed slot positions, captions, code highlights,
  temporary-value display, screen cleanup, and mobile-size text readability.

## References

The core selection procedure and quadratic comparison behavior are described
in Princeton's [Elementary Sorts](https://algs4.cs.princeton.edu/21elementary/).
Its [Java implementation](https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/Selection.java.html)
also documents constant extra memory and instability. Our teaching version
stops after `n - 1` destinations and skips self-swaps; its swap count therefore
differs from Princeton's implementation, which exchanges on every outer pass.
