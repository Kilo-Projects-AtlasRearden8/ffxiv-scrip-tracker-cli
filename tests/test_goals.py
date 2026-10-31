"""Tests for spending goal logic."""

from __future__ import annotations

import unittest

from ffxiv_scrip_tracker.goals import GoalBook, SpendingGoal


class SpendingGoalTests(unittest.TestCase):
    def test_progress_and_remaining(self) -> None:
        goal = SpendingGoal(name="gear", scrip_type="purple", target=500, spent=100)
        self.assertEqual(goal.spent, 100)
        self.assertEqual(goal.remaining, 400)
        self.assertEqual(goal.progress, 0.2)
        self.assertFalse(goal.met)
        self.assertFalse(goal.should_alert())

    def test_default_alert_at_is_80_percent(self) -> None:
        goal = SpendingGoal(name="g", scrip_type="white", target=100, spent=79)
        self.assertFalse(goal.should_alert())
        goal.spent = 80
        self.assertTrue(goal.should_alert())
        self.assertFalse(goal.met)

    def test_goal_met_at_target(self) -> None:
        goal = SpendingGoal(name="g", scrip_type="white", target=100, spent=100)
        self.assertTrue(goal.met)
        self.assertTrue(goal.should_alert())
        self.assertEqual(goal.remaining, 0)
        self.assertEqual(goal.progress, 1.0)

    def test_progress_clamps_at_100_percent(self) -> None:
        goal = SpendingGoal(name="g", scrip_type="white", target=100, spent=250)
        self.assertEqual(goal.progress, 1.0)
        self.assertEqual(goal.remaining, 0)

    def test_record_spend_increments(self) -> None:
        goal = SpendingGoal(name="g", scrip_type="purple", target=500)
        goal.record_spend(150)
        goal.record_spend(100)
        self.assertEqual(goal.spent, 250)
        self.assertEqual(goal.remaining, 250)

    def test_record_spend_rejects_bad_amount(self) -> None:
        goal = SpendingGoal(name="g", scrip_type="purple", target=500)
        with self.assertRaises(ValueError):
            goal.record_spend(0)
        with self.assertRaises(ValueError):
            goal.record_spend(-10)

    def test_invalid_scrip_type_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SpendingGoal(name="g", scrip_type="blue", target=100)  # type: ignore[arg-type]

    def test_invalid_target_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SpendingGoal(name="g", scrip_type="white", target=0)
        with self.assertRaises(ValueError):
            SpendingGoal(name="g", scrip_type="white", target=-5)

    def test_invalid_alert_at_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SpendingGoal(name="g", scrip_type="white", target=100, alert_at=1.5)
        with self.assertRaises(ValueError):
            SpendingGoal(name="g", scrip_type="white", target=100, alert_at=-0.1)


class GoalBookTests(unittest.TestCase):
    def test_add_and_spend(self) -> None:
        book = GoalBook()
        book.add(SpendingGoal(name="gear", scrip_type="purple", target=500))
        goal = book.spend("gear", 200)
        self.assertEqual(goal.spent, 200)

    def test_spend_unknown_goal_raises(self) -> None:
        book = GoalBook()
        with self.assertRaises(KeyError):
            book.spend("missing", 10)

    def test_alerts(self) -> None:
        book = GoalBook()
        book.add(SpendingGoal(name="safe", scrip_type="white", target=1000, spent=100))
        book.add(SpendingGoal(name="near", scrip_type="purple", target=500, spent=450))
        book.add(SpendingGoal(name="done", scrip_type="white", target=50, spent=50))
        alerts = book.alerts()
        names = {goal.name for goal in alerts}
        self.assertEqual(names, {"near", "done"})

    def test_serialization_round_trip(self) -> None:
        book = GoalBook()
        book.add(SpendingGoal(name="gear", scrip_type="purple", target=500, spent=100, alert_at=0.5))
        restored = GoalBook.from_dict(book.to_dict())
        self.assertEqual(len(restored.goals), 1)
        goal = restored.goals[0]
        self.assertEqual(goal.name, "gear")
        self.assertEqual(goal.spent, 100)
        self.assertEqual(goal.alert_at, 0.5)


if __name__ == "__main__":
    unittest.main()
