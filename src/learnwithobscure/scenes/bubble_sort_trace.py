"""Statement-by-statement state for the Java Bubble Sort demonstration.

The line numbers match the twelve-line snippet in ``bubble_sort.py``. This
module has no Manim dependency: animation consumes the immutable snapshots
rather than guessing what the array should look like during a swap.
"""

from dataclasses import dataclass
from typing import Iterable, Literal


EventKind = Literal[
    "outer_init", "outer_check", "reset_swapped", "inner_init", "inner_check",
    "compare", "save_temp", "assign_left", "assign_right", "mark_swapped",
    "inner_increment", "pass_complete", "early_exit_check", "break",
    "outer_decrement", "done",
]


@dataclass(frozen=True, slots=True)
class BubbleSortEvent:
    """State immediately after a statement or condition is evaluated.

    ``condition`` is the result for a loop check, pair comparison, or early
    exit check; it is ``None`` for assignments. ``sorted_from`` marks the
    suffix proved to be in its final position, initially ``len(values)``.
    ``temp`` becomes ``None`` when its block scope ends at ``inner_increment``.
    ``i`` becomes ``None`` at ``pass_complete`` when its for-loop scope ends;
    the preceding failed ``inner_check`` still shows ``i == end``.
    ``pass_complete`` and ``done`` are explanatory events without a code line.
    A failed outer check identifies the candidate pass; ``done`` identifies
    the number of completed passes (zero for empty and singleton inputs).
    """

    kind: EventKind
    line_index: int | None
    values: tuple[int, ...]
    pass_number: int
    end: int
    i: int | None
    temp: int | None
    swapped: bool
    condition: bool | None
    sorted_from: int


def bubble_sort_events(initial_values: Iterable[int]) -> tuple[BubbleSortEvent, ...]:
    """Execute optimized ascending Bubble Sort and record every Java step.

    The input is copied and is never mutated. In particular, the two array
    assignments are distinct events: copying the right value into the left
    slot temporarily displays two equal numbers, while ``temp`` retains the
    displaced value until the second assignment restores it on the right.
    """
    values = list(initial_values)
    end = len(values) - 1
    i = None
    temp = None
    swapped = False
    sorted_from = len(values)
    pass_number = 1
    completed_passes = 0
    events: list[BubbleSortEvent] = []

    def emit(kind: EventKind, line_index: int | None, condition: bool | None = None):
        events.append(BubbleSortEvent(
            kind=kind,
            line_index=line_index,
            values=tuple(values),
            pass_number=pass_number,
            end=end,
            i=i,
            temp=temp,
            swapped=swapped,
            condition=condition,
            sorted_from=sorted_from,
        ))

    # Line 0: for (int end = arr.length - 1; end > 0; end--)
    emit("outer_init", 0)
    while True:
        emit("outer_check", 0, end > 0)
        if end <= 0:
            break

        # Line 1: boolean swapped = false;
        swapped = False
        emit("reset_swapped", 1)

        # Line 2: for (int i = 0; i < end; i++)
        i = 0
        emit("inner_init", 2)
        while True:
            emit("inner_check", 2, i < end)
            if i >= end:
                break

            # Line 3: if (arr[i] > arr[i + 1])
            should_swap = values[i] > values[i + 1]
            emit("compare", 3, should_swap)
            if should_swap:
                # Lines 4-7 intentionally remain four separate statements.
                temp = values[i]
                emit("save_temp", 4)
                values[i] = values[i + 1]
                emit("assign_left", 5)
                values[i + 1] = temp
                emit("assign_right", 6)
                swapped = True
                emit("mark_swapped", 7)

            # Leaving the if block ends temp's scope; it is not a Java reset.
            temp = None
            i += 1
            emit("inner_increment", 2)

        completed_passes += 1
        sorted_from = end
        i = None
        emit("pass_complete", None)

        # Line 10: if (!swapped) break;
        emit("early_exit_check", 10, not swapped)
        if not swapped:
            sorted_from = 0
            emit("break", 10)
            break

        # The outer loop's update executes only when break was not taken.
        end -= 1
        i = None
        emit("outer_decrement", 0)
        pass_number += 1

    sorted_from = 0
    pass_number = completed_passes
    emit("done", None)
    return tuple(events)
