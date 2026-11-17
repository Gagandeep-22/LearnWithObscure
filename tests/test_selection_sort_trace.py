"""Verify the Java trace, loop invariants, complexity, and instability example."""

from dataclasses import FrozenInstanceError
from itertools import product
import unittest

from learnwithobscure.scenes.selection_sort_trace import (
    JAVA_IMPLEMENTATION,
    JAVA_TRACE_LINES,
    selection_sort_events,
)


class TaggedInt(int):
    """Expose the original order of equal keys without changing comparisons."""

    def __new__(cls, value, origin):
        result = super().__new__(cls, value)
        result.origin = origin
        return result


class SelectionSortTraceTests(unittest.TestCase):
    def test_lesson_input_needs_ten_comparisons_and_two_swaps(self):
        source = [5, 1, 4, 2, 8]
        events = selection_sort_events(source)
        self.assertEqual(source, [5, 1, 4, 2, 8])
        self.assertEqual(events[-1].values, (1, 2, 4, 5, 8))
        self.assertEqual(events[-1].comparisons, 10)
        self.assertEqual(events[-1].swaps, 2)
        self.assertEqual(events[-1].pass_number, 4)
        complete = [event for event in events if event.kind == "pass_complete"]
        self.assertEqual([event.values for event in complete], [
            (1, 5, 4, 2, 8), (1, 2, 4, 5, 8),
            (1, 2, 4, 5, 8), (1, 2, 4, 5, 8),
        ])
        self.assertEqual([event.condition for event in events if event.kind == "swap_check"],
                         [True, True, False, False])
        self.assertEqual([event.sorted_until for event in complete], [1, 2, 3, 4])

    def test_first_swap_has_separate_assignments_and_temporary_duplicates(self):
        events = selection_sort_events([5, 1, 4, 2, 8])
        index = next(i for i, event in enumerate(events) if event.kind == "save_temp")
        save, assign_start, assign_min, complete = events[index:index + 4]
        self.assertEqual([event.line_index for event in (save, assign_start, assign_min)],
                         [8, 9, 10])
        self.assertEqual(save.values, (5, 1, 4, 2, 8))
        self.assertEqual(assign_start.values, (1, 1, 4, 2, 8))
        self.assertEqual(assign_min.values, (1, 5, 4, 2, 8))
        self.assertEqual([event.temp for event in (save, assign_start, assign_min)], [5, 5, 5])
        self.assertEqual([event.swaps for event in (save, assign_start, assign_min)], [0, 0, 1])
        self.assertEqual(complete.kind, "pass_complete")
        self.assertIsNone(complete.temp)

    def test_minimum_is_an_index_and_changes_only_after_a_successful_comparison(self):
        events = selection_sort_events([7, 4, 5, 1])
        first_pass = [event for event in events if event.pass_number == 1]
        updates = [event for event in first_pass if event.kind == "update_min"]
        self.assertEqual([event.min_index for event in updates], [1, 3])
        for previous, event in zip(events, events[1:]):
            if event.kind == "compare":
                self.assertEqual(previous.min_index, event.min_index)
            if event.kind == "update_min":
                self.assertEqual(previous.kind, "compare")
                self.assertTrue(previous.condition)
                self.assertEqual(event.min_index, event.scan)
                self.assertEqual(event.values, previous.values)

    def test_sorted_and_equal_inputs_still_scan_all_suffixes_without_swaps(self):
        for source in ([1, 2, 3, 4], [2, 2, 2, 2]):
            with self.subTest(source=source):
                events = selection_sort_events(source)
                self.assertEqual(events[-1].comparisons, 6)
                self.assertEqual(events[-1].swaps, 0)
                self.assertEqual(events[-1].pass_number, 3)
                self.assertFalse(any(event.kind == "save_temp" for event in events))
                self.assertEqual(events[-1].values, tuple(source))

    def test_one_pass_without_a_swap_does_not_mean_the_suffix_is_sorted(self):
        events = selection_sort_events([1, 3, 2])
        checks = [event for event in events if event.kind == "swap_check"]
        self.assertEqual([event.condition for event in checks], [False, True])
        self.assertEqual(checks[0].values, (1, 3, 2))
        self.assertEqual(events[-1].values, (1, 2, 3))
        self.assertEqual(events[-1].comparisons, 3)

    def test_empty_and_singleton_inputs_never_read_an_array_slot(self):
        for source in ([], [7]):
            with self.subTest(source=source):
                events = selection_sort_events(source)
                self.assertEqual([event.kind for event in events],
                                 ["outer_init", "outer_check", "done"])
                self.assertFalse(events[1].condition)
                self.assertEqual(events[-1].values, tuple(source))
                self.assertEqual(events[-1].comparisons, 0)
                self.assertEqual(events[-1].swaps, 0)
                self.assertEqual(events[-1].pass_number, 0)

    def test_java_variable_scopes_match_explanatory_events(self):
        events = selection_sort_events([5, 1, 4, 2, 8])
        for previous, event in zip(events, events[1:]):
            if event.kind == "scan_complete":
                self.assertEqual(previous.kind, "inner_check")
                self.assertFalse(previous.condition)
                self.assertEqual(previous.scan, 5)
                self.assertIsNone(event.scan)
            if event.kind in ("swap_check", "save_temp", "assign_start", "assign_min",
                              "pass_complete", "outer_increment", "done"):
                self.assertIsNone(event.scan)
            if event.kind in ("outer_increment", "done"):
                self.assertIsNone(event.min_index)
                self.assertIsNone(event.temp)

    def test_strict_less_does_not_make_long_distance_swaps_stable(self):
        source = [TaggedInt(2, "A"), TaggedInt(2, "B"), TaggedInt(1, "C")]
        events = selection_sort_events(source)
        self.assertEqual([(int(value), value.origin) for value in events[-1].values],
                         [(1, "C"), (2, "B"), (2, "A")])
        self.assertEqual(events[-1].swaps, 1)
        # The equal two never replaces the first two as the current minimum.
        self.assertFalse(next(event for event in events if event.kind == "compare").condition)

    def test_snapshots_are_immutable_and_iterators_are_accepted(self):
        events = selection_sort_events(iter([3, 1, 2]))
        self.assertEqual(events[-1].values, (1, 2, 3))
        with self.assertRaises(FrozenInstanceError):
            events[0].start = 99

    def test_display_listing_and_complete_implementation_share_statements(self):
        self.assertEqual(len(JAVA_TRACE_LINES), 13)
        self.assertEqual(JAVA_TRACE_LINES[3].strip(), "if (arr[scan] < arr[minIndex]) {")
        self.assertEqual(JAVA_TRACE_LINES[7].strip(), "if (minIndex != start) {")
        self.assertEqual(JAVA_IMPLEMENTATION.splitlines()[1:-1],
                         ["    " + line for line in JAVA_TRACE_LINES])

    def test_small_inputs_obey_every_statement_bound_and_fixed_prefix(self):
        for length in range(6):
            for source in product((-1, 0, 1), repeat=length):
                with self.subTest(source=source):
                    events = selection_sort_events(source)
                    expected = tuple(sorted(source))
                    final = events[-1]
                    self.assertEqual(final.values, expected)
                    self.assertEqual(final.comparisons, length * (length - 1) // 2)
                    self.assertEqual(final.pass_number, max(0, length - 1))
                    self.assertLessEqual(final.swaps, max(0, length - 1))
                    self.assertEqual(final.sorted_until, length)
                    for previous, event in zip(events, events[1:]):
                        before = list(previous.values)
                        if event.kind == "assign_start":
                            before[event.start] = before[event.min_index]
                        elif event.kind == "assign_min":
                            before[event.min_index] = previous.temp
                        self.assertEqual(event.values, tuple(before))
                        self.assertEqual(event.values[:event.sorted_until],
                                         expected[:event.sorted_until])
                        self.assertEqual(event.comparisons - previous.comparisons,
                                         int(event.kind == "compare"))
                        self.assertEqual(event.swaps - previous.swaps,
                                         int(event.kind == "assign_min"))
                        if event.kind == "outer_check":
                            self.assertEqual(event.condition, event.start < length - 1)
                        elif event.kind == "inner_check":
                            self.assertEqual(event.condition, event.scan < length)
                        elif event.kind == "compare":
                            self.assertGreater(event.scan, event.start)
                            self.assertLess(event.scan, length)
                            self.assertGreaterEqual(event.min_index, event.start)
                            self.assertLess(event.min_index, event.scan)
                            self.assertEqual(event.condition,
                                             event.values[event.scan] < event.values[event.min_index])
                        elif event.kind == "swap_check":
                            self.assertEqual(event.condition, event.min_index != event.start)
                            self.assertEqual(event.values[event.min_index],
                                             min(event.values[event.start:]))
                        elif event.kind == "inner_increment":
                            self.assertEqual(event.scan, previous.scan + 1)
                        elif event.kind == "outer_increment":
                            self.assertEqual(event.start, previous.start + 1)
                        if event.line_index is not None:
                            self.assertIn(event.line_index, range(len(JAVA_TRACE_LINES)))


if __name__ == "__main__":
    unittest.main()
