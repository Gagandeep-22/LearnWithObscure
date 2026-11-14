"""Verify execution state, including temporary duplicates during Java swaps."""

from dataclasses import FrozenInstanceError
from itertools import product
import unittest

from learnwithobscure.scenes.bubble_sort_trace import bubble_sort_events


def sort_without_early_exit(source):
    """Independent shrinking-pass version with no swapped flag or break."""
    values = list(source)
    comparisons = passes = 0
    for end in range(len(values) - 1, 0, -1):
        passes += 1
        for i in range(end):
            comparisons += 1
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
    return tuple(values), comparisons, passes


class TaggedInt(int):
    """An integer carrying its original position to expose equal-key order."""

    def __new__(cls, value, origin):
        result = super().__new__(cls, value)
        result.origin = origin
        return result


class BubbleSortTraceTests(unittest.TestCase):
    def test_lesson_example_has_four_swaps_and_early_exit_on_pass_three(self):
        source = [5, 1, 4, 2, 8]
        events = bubble_sort_events(source)
        self.assertEqual(source, [5, 1, 4, 2, 8])
        self.assertEqual(events[-1].values, (1, 2, 4, 5, 8))
        self.assertEqual(events[-1].pass_number, 3)
        self.assertEqual(sum(event.kind == "compare" for event in events), 9)
        self.assertEqual(sum(event.kind == "mark_swapped" for event in events), 4)
        checks = [event for event in events if event.kind == "early_exit_check"]
        self.assertEqual([event.condition for event in checks], [False, False, True])
        self.assertEqual([event.end for event in checks], [4, 3, 2])
        self.assertEqual([event.swapped for event in checks], [True, True, False])
        self.assertEqual([event.pass_number for event in events if event.kind == "break"], [3])
        self.assertEqual(events[-1].sorted_from, 0)

    def test_first_swap_keeps_array_slots_and_temp_distinct(self):
        events = bubble_sort_events([5, 1, 4, 2, 8])
        start = next(index for index, event in enumerate(events) if event.kind == "save_temp")
        save, left, right, flag, increment = events[start:start + 5]
        self.assertEqual([event.line_index for event in (save, left, right, flag)], [4, 5, 6, 7])
        self.assertEqual(save.values, (5, 1, 4, 2, 8))
        self.assertEqual(left.values, (1, 1, 4, 2, 8))
        self.assertEqual(right.values, (1, 5, 4, 2, 8))
        self.assertEqual([event.temp for event in (save, left, right, flag)], [5] * 4)
        self.assertEqual([event.swapped for event in (save, left, right, flag)], [False, False, False, True])
        self.assertEqual(increment.kind, "inner_increment")
        self.assertEqual(increment.i, 1)
        self.assertIsNone(increment.temp)

    def test_already_sorted_and_equal_values_finish_after_one_pass(self):
        for source in ([1, 2, 3, 4], [2, 2, 2, 2]):
            with self.subTest(source=source):
                events = bubble_sort_events(source)
                self.assertEqual(sum(event.kind == "compare" for event in events), 3)
                self.assertFalse(any(event.kind == "save_temp" for event in events))
                self.assertEqual(events[-1].values, tuple(source))
                self.assertEqual(events[-1].pass_number, 1)
                self.assertTrue(any(event.kind == "break" for event in events))

    def test_empty_and_singleton_inputs_never_read_a_neighbor(self):
        for source in ([], [7]):
            with self.subTest(source=source):
                events = bubble_sort_events(source)
                self.assertEqual([event.kind for event in events], ["outer_init", "outer_check", "done"])
                self.assertFalse(events[1].condition)
                self.assertEqual(events[-1].values, tuple(source))
                self.assertEqual(events[-1].pass_number, 0)

    def test_reverse_input_exits_when_outer_condition_fails(self):
        events = bubble_sort_events([4, 3, 2, 1])
        self.assertEqual(events[-1].values, (1, 2, 3, 4))
        self.assertFalse(any(event.kind == "break" for event in events))
        self.assertEqual(events[-2].kind, "outer_check")
        self.assertFalse(events[-2].condition)
        self.assertEqual(events[-2].end, 0)
        self.assertEqual(sum(event.kind == "compare" for event in events), 6)

    def test_inner_loop_variable_leaves_scope_after_failed_check(self):
        events = bubble_sort_events([5, 1, 4, 2, 8])
        completed = []
        for previous, event in zip(events, events[1:]):
            if event.kind == "pass_complete":
                completed.append(event.pass_number)
                self.assertEqual(previous.kind, "inner_check")
                self.assertFalse(previous.condition)
                self.assertEqual(previous.i, previous.end)
                self.assertIsNone(event.i)
                self.assertIsNone(event.temp)
            elif event.kind in ("early_exit_check", "break", "outer_decrement", "done"):
                self.assertIsNone(event.i)
        self.assertEqual(completed, [1, 2, 3])

    def test_snapshots_are_immutable(self):
        event = bubble_sort_events([2, 1])[0]
        with self.assertRaises(FrozenInstanceError):
            event.i = 99

    def test_shrinking_passes_sort_without_a_swapped_flag(self):
        for length in range(6):
            for source in product((-1, 0, 1), repeat=length):
                with self.subTest(source=source):
                    result, comparisons, passes = sort_without_early_exit(source)
                    self.assertEqual(result, tuple(sorted(source)))
                    self.assertEqual(result, bubble_sort_events(source)[-1].values)
                    self.assertEqual(passes, max(0, length - 1))
                    self.assertEqual(comparisons, length * (length - 1) // 2)

    def test_early_exit_saves_comparisons_on_already_sorted_inputs(self):
        for length in range(13):
            with self.subTest(length=length):
                source = list(range(length))
                result, comparisons, _ = sort_without_early_exit(source)
                events = bubble_sort_events(source)
                self.assertEqual(events[-1].values, result)
                self.assertEqual(comparisons, length * (length - 1) // 2)
                self.assertEqual(sum(e.kind == "compare" for e in events), max(0, length - 1))
                self.assertEqual(events[-1].pass_number, int(length >= 2))

    def test_a_swapped_pass_can_already_have_sorted_the_array(self):
        for source, sorted_pass in (([2, 1], 1), ([5, 1, 4, 2, 8], 2)):
            with self.subTest(source=source):
                events = bubble_sort_events(source)
                completed = next(e for e in events if e.kind == "pass_complete" and e.pass_number == sorted_pass)
                check = next(e for e in events if e.kind == "early_exit_check" and e.pass_number == sorted_pass)
                self.assertEqual(completed.values, tuple(sorted(source)))
                self.assertTrue(completed.swapped)
                self.assertFalse(check.condition)
        pair_events = bubble_sort_events([2, 1])
        self.assertEqual(pair_events[-1].pass_number, 1)
        self.assertFalse(any(e.kind == "break" for e in pair_events))
        lesson_events = bubble_sort_events([5, 1, 4, 2, 8])
        self.assertEqual([e.pass_number for e in lesson_events if e.kind == "break"], [3])

    def test_one_small_value_at_the_end_still_requires_quadratic_comparisons(self):
        for length in range(2, 17):
            with self.subTest(length=length):
                source = [*range(2, length + 1), 1]
                events = bubble_sort_events(source)
                self.assertEqual(events[-1].values, tuple(range(1, length + 1)))
                self.assertEqual(events[-1].pass_number, length - 1)
                self.assertEqual(sum(e.kind == "compare" for e in events), length * (length - 1) // 2)
                self.assertEqual(sum(e.kind == "mark_swapped" for e in events), length - 1)

    def test_strict_comparison_preserves_original_order_of_equal_keys(self):
        for length in range(6):
            for keys in product((-1, 0, 1), repeat=length):
                with self.subTest(keys=keys):
                    source = [TaggedInt(key, origin) for origin, key in enumerate(keys)]
                    actual = bubble_sort_events(source)[-1].values
                    expected = sorted(source)
                    self.assertEqual([(int(item), item.origin) for item in actual],
                                     [(int(item), item.origin) for item in expected])

    def test_small_inputs_obey_statement_effects_and_loop_bounds(self):
        for length in range(5):
            for source in product((-1, 0, 1), repeat=length):
                with self.subTest(source=source):
                    events = bubble_sort_events(source)
                    self.assertEqual(events[-1].values, tuple(sorted(source)))
                    for previous, event in zip(events, events[1:]):
                        before = list(previous.values)
                        if event.kind == "assign_left":
                            self.assertEqual(event.line_index, 5)
                            before[event.i] = before[event.i + 1]
                        elif event.kind == "assign_right":
                            self.assertEqual(event.line_index, 6)
                            before[event.i + 1] = previous.temp
                        self.assertEqual(event.values, tuple(before))
                        if event.kind == "compare":
                            self.assertLess(event.i, event.end)
                            self.assertGreaterEqual(event.i, 0)
                            self.assertLess(event.i + 1, length)
                            self.assertEqual(event.condition, event.values[event.i] > event.values[event.i + 1])
                        elif event.kind == "inner_check":
                            self.assertEqual(event.condition, event.i < event.end)
                        elif event.kind == "reset_swapped":
                            self.assertFalse(event.swapped)
                        elif event.kind == "inner_increment":
                            self.assertEqual(event.i, previous.i + 1)
                            self.assertIsNone(event.temp)
                        if event.kind not in ("reset_swapped", "mark_swapped"):
                            self.assertEqual(event.swapped, previous.swapped)
                        if event.sorted_from < length:
                            suffix = event.values[event.sorted_from:]
                            self.assertEqual(suffix, tuple(sorted(suffix)))


if __name__ == "__main__":
    unittest.main()
