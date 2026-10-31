"""Spending goal logic for FFXIV scrips."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal

from .scrips import ScripType, SCRIP_TYPES


@dataclass
class SpendingGoal:
    """A spending goal tracked against one scrip type.

    ``spent`` counts scrips spent toward the goal. ``target`` is the
    scrip budget. Progress is spent / target.
    """

    name: str
    scrip_type: ScripType
    target: int
    spent: int = 0
    alert_at: float = 0.8

    def __post_init__(self) -> None:
        if self.scrip_type not in SCRIP_TYPES:
            raise ValueError(
                f"Unknown scrip type: {self.scrip_type!r}. Use 'white' or 'purple'."
            )
        if not isinstance(self.target, int) or isinstance(self.target, bool) or self.target <= 0:
            raise ValueError("Target must be a positive integer.")
        if not isinstance(self.spent, int) or isinstance(self.spent, bool) or self.spent < 0:
            raise ValueError("Spent must be a non-negative integer.")
        if not (0.0 <= self.alert_at <= 1.0):
            raise ValueError("alert_at must be between 0 and 1.")

    @property
    def remaining(self) -> int:
        return max(self.target - self.spent, 0)

    @property
    def progress(self) -> float:
        if self.target <= 0:
            return 0.0
        return min(self.spent / self.target, 1.0)

    @property
    def met(self) -> bool:
        return self.spent >= self.target

    def record_spend(self, amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError(f"Amount must be a positive integer, got {amount!r}.")
        self.spent += amount

    def should_alert(self) -> bool:
        """True when the goal has been met or the alert threshold is reached."""
        if self.met:
            return True
        return self.progress >= self.alert_at

    def status_line(self) -> str:
        bar_width = 20
        filled = int(self.progress * bar_width)
        bar = "#" * filled + "-" * (bar_width - filled)
        pct = self.progress * 100
        return (
            f"[{bar}] {pct:5.1f}%  {self.name} "
            f"({self.scrip_type}): {self.spent}/{self.target} spent, "
            f"{self.remaining} remaining"
        )

    # --- serialization -------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SpendingGoal":
        return cls(**data)


@dataclass
class GoalBook:
    """Collection of spending goals."""

    goals: list[SpendingGoal] = field(default_factory=list)

    def add(self, goal: SpendingGoal) -> None:
        self.goals.append(goal)

    def spend(self, name: str, amount: int) -> SpendingGoal:
        for goal in self.goals:
            if goal.name == name:
                goal.record_spend(amount)
                return goal
        raise KeyError(f"No goal named {name!r}.")

    def alerts(self) -> list[SpendingGoal]:
        return [goal for goal in self.goals if goal.should_alert()]

    def to_dict(self) -> dict:
        return [goal.to_dict() for goal in self.goals]

    @classmethod
    def from_dict(cls, data: list) -> "GoalBook":
        return cls(goals=[SpendingGoal.from_dict(item) for item in data])
