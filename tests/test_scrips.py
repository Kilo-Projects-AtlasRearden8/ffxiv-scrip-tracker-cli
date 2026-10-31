"""Tests for scrip tally logic."""

from __future__ import annotations

import unittest

from ffxiv_scrip_tracker.scrips import ScripTally, SCRIP_TYPES


class ScripTallyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tally = ScripTally()

    def test_initial_balances_are_zero(self) -> None:
        for scrip_type in SCRIP_TYPES:
            self.assertEqual(self.tally.balance(scrip_type), 0)
        self.assertEqual(self.tally.total(), 0)

    def test_earn_increases_balance(self) -> None:
        self.tally.earn("white", 1500)
        self.assertEqual(self.tally.balance("white"), 1500)
        self.assertEqual(self.tally.total(), 1500)

    def test_earn_purple(self) -> None:
        self.tally.earn("purple", 42)
        self.assertEqual(self.tally.balance("purple"), 42)
        self.assertEqual(self.tally.balance("white"), 0)

    def test_spend_decreases_balance(self) -> None:
        self.tally.earn("white", 1000)
        self.tally.spend("white", 300)
        self.assertEqual(self.tally.balance("white"), 700)

    def test_spend_insufficient_fails(self) -> None:
        self.tally.earn("purple", 10)
        with self.assertRaises(ValueError):
            self.tally.spend("purple", 20)
        self.assertEqual(self.tally.balance("purple"), 10)

    def test_earn_records_positive_transaction(self) -> None:
        self.tally.earn("white", 500, note="weekly")
        txs = self.tally.transactions_for("white")
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].amount, 500)
        self.assertEqual(txs[0].delta, 500)
        self.assertEqual(txs[0].note, "weekly")

    def test_spend_records_negative_transaction(self) -> None:
        self.tally.earn("white", 500)
        self.tally.spend("white", 200, note="gear")
        txs = self.tally.transactions_for("white")
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[1].amount, 200)
        self.assertEqual(txs[1].delta, -200)
        self.assertEqual(txs[1].note, "gear")

    def test_invalid_scrip_type_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tally.earn("blue", 10)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.tally.spend("green", 10)  # type: ignore[arg-type]

    def test_nonpositive_amount_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tally.earn("white", 0)
        with self.assertRaises(ValueError):
            self.tally.earn("white", -5)
        with self.assertRaises(ValueError):
            self.tally.spend("white", 0)

    def test_transactions_for_all_returns_both_types(self) -> None:
        self.tally.earn("white", 100)
        self.tally.earn("purple", 50)
        all_tx = self.tally.transactions_for()
        self.assertEqual(len(all_tx), 2)

    def test_serialization_round_trip(self) -> None:
        self.tally.earn("white", 1234, note="crafting")
        self.tally.earn("purple", 99, note="gathering")
        self.tally.spend("white", 34)
        restored = ScripTally.from_dict(self.tally.to_dict())
        self.assertEqual(restored.balance("white"), 1200)
        self.assertEqual(restored.balance("purple"), 99)
        self.assertEqual(len(restored.transactions_for("white")), 2)
        self.assertEqual(len(restored.transactions_for("purple")), 1)


if __name__ == "__main__":
    unittest.main()
