"""Immutable execution snapshots for the lesson's Java Selection Sort.

The trace and the displayed Java share one source listing. No Manim dependency
is needed to verify the algorithm, the scope of its variables, or the temporary
duplicate values created by the two separate array assignments in a swap.
"""

from dataclasses import dataclass
from typing import Iterable, Literal


JAVA_TRACE_LINES = (
    "for (int start = 0; start < arr.length - 1; start++) {",
    "    int minIndex = start;",
    "    for (int scan = start + 1; scan < arr.length; scan++) {",
    "        if (arr[scan] < arr[minIndex]) {",
    "            minIndex = scan;",
    "        }",
    "    }",
    "    if (minIndex != start) {",
    "        int temp = arr[start];",
    "        arr[start] = arr[minIndex];",
    "        arr[minIndex] = temp;",
    "    }",
    "}",
)

JAVA_IMPLEMENTATION = (
    "public static void selectionSort(int[] arr) {\n"
    + "\n".join("    " + line for line in JAVA_TRACE_LINES)
    + "\n}"
)

EventKind = Literal[
    "outer_init", "outer_check", "reset_min", "inner_init", "inner_check",
    "compare", "update_min", "inner_increment", "scan_complete", "swap_check",
    "save_temp", "assign_start", "assign_min", "pass_complete",
    "outer_increment", "done",
]


@dataclass(frozen=True, slots=True)
class SelectionSortEvent:
    """State immediately after a statement or condition has executed.

    ``line_index`` is zero based within ``JAVA_TRACE_LINES``. The explanatory
    ``scan_complete``, ``pass_complete``, and ``done`` events have no code line.
    ``sorted_until`` is the exclusive end of the prefix proved final so far.
    ``condition`` holds a Boolean only for condition evaluations.

    ``scan`` leaves scope at ``scan_complete``; ``temp`` leaves scope at
    ``pass_complete``; ``min_index`` leaves scope at ``outer_increment``.
    A failed outer check identifies the candidate pass; ``done`` instead
    records the number of completed passes, zero for empty or singleton input.
    ``comparisons`` counts value comparisons, not loop or index checks.
    ``swaps`` increases only when the final assignment completes a real swap.
    ``start`` retains its final control value in ``done`` for diagnostics;
    Java's loop-local variable itself is out of scope at that point.
    """

    kind: EventKind
    line_index: int | None
    values: tuple[int, ...]
    pass_number: int
    start: int
    min_index: int | None
    scan: int | None
    temp: int | None
    condition: bool | None
    sorted_until: int
    comparisons: int
    swaps: int


def selection_sort_events(initial_values: Iterable[int]) -> tuple[SelectionSortEvent, ...]:
    """Execute the ascending, in-place Java algorithm on a private input copy.

    Each pass scans the entire remaining suffix before making at most one
    swap. A pass with no swap cannot prove the remaining suffix is sorted, so
    there is no Bubble Sort-style early exit. A strict comparison keeps the
    first minimum found, but long-distance swaps can still reverse equal keys.

    Unlike the Java method's constant auxiliary space, this teaching helper
    stores Theta(n^2) snapshots of n values. Materializing the complete trace
    therefore takes Theta(n^3) time and storage as the input size grows.
    """
    values = list(initial_values)
    start = 0
    min_index = scan = temp = None
    pass_number = 1
    completed_passes = sorted_until = comparisons = swaps = 0
    events: list[SelectionSortEvent] = []

    def emit(kind: EventKind, line_index: int | None, condition: bool | None = None):
        events.append(SelectionSortEvent(
            kind=kind,
            line_index=line_index,
            values=tuple(values),
            pass_number=pass_number,
            start=start,
            min_index=min_index,
            scan=scan,
            temp=temp,
            condition=condition,
            sorted_until=sorted_until,
            comparisons=comparisons,
            swaps=swaps,
        ))

    emit("outer_init", 0)
    while True:
        emit("outer_check", 0, start < len(values) - 1)
        if start >= len(values) - 1:
            break

        min_index = start
        emit("reset_min", 1)

        scan = start + 1
        emit("inner_init", 2)
        while True:
            emit("inner_check", 2, scan < len(values))
            if scan >= len(values):
                break

            smaller = values[scan] < values[min_index]
            comparisons += 1
            emit("compare", 3, smaller)
            if smaller:
                min_index = scan
                emit("update_min", 4)

            scan += 1
            emit("inner_increment", 2)

        scan = None
        emit("scan_complete", None)

        emit("swap_check", 7, min_index != start)
        if min_index != start:
            temp = values[start]
            emit("save_temp", 8)
            values[start] = values[min_index]
            emit("assign_start", 9)
            values[min_index] = temp
            swaps += 1
            emit("assign_min", 10)

        # These are scope changes, not extra Java assignments.
        temp = None
        completed_passes += 1
        sorted_until = start + 1
        emit("pass_complete", None)

        min_index = None
        start += 1
        emit("outer_increment", 0)
        pass_number += 1

    sorted_until = len(values)
    pass_number = completed_passes
    emit("done", None)
    return tuple(events)
