"""Progress alerts for spending goals."""

from __future__ import annotations

from .goals import GoalBook, SpendingGoal


class AlertChecker:
    """Produces human-readable alert messages for goals that need attention."""

    def __init__(self, goals: GoalBook) -> None:
        self.goals = goals

    def check(self) -> list[str]:
        messages: list[str] = []
        for goal in self.goals.alerts():
            if goal.met:
                messages.append(
                    f"GOAL MET: {goal.name} ({goal.scrip_type}) - "
                    f"{goal.spent}/{goal.spent} spent"
                )
            else:
                pct = goal.progress * 100
                messages.append(
                    f"APPROACHING GOAL: {goal.name} ({goal.scrip_type}) - "
                    f"{goal.spent}/{goal.target} spent ({pct:.0f}%), "
                    f"{goal.remaining} remaining"
                )
        return messages

    def format(self) -> str:
        messages = self.check()
        if not messages:
            return "No spending goal alerts at this time."
        lines = ["Spending goal alerts:"]
        lines.extend(f"  - {message}" for message in messages)
        return "\n".join(lines)
