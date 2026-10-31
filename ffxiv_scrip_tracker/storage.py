"""Local JSON storage for the FFXIV scrip tracker."""

from __future__ import annotations

import json
import os
from typing import Any

from .scrips import ScripTally
from .goals import GoalBook
from .vendors import VendorBook


class Storage:
    """Reads and writes tracker state to a single JSON file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> dict[str, Any]:
        if not self.exists():
            return {}
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return {}
        return data

    def save(self, data: dict[str, Any]) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")

    # --- high-level helpers -------------------------------------------

    def load_tally(self) -> ScripTally:
        return ScripTally.from_dict(self.load().get("scrips", {}))

    def save_tally(self, tally: ScripTally) -> None:
        data = self.load()
        data["scrips"] = tally.to_dict()
        self.save(data)

    def load_goals(self) -> GoalBook:
        return GoalBook.from_dict(self.load().get("goals", []))

    def save_goals(self, goals: GoalBook) -> None:
        data = self.load()
        data["goals"] = goals.to_dict()
        self.save(data)

    def load_vendors(self) -> VendorBook:
        return VendorBook.from_dict(self.load().get("vendors", []))

    def save_vendors(self, vendors: VendorBook) -> None:
        data = self.load()
        data["vendors"] = vendors.to_dict()
        self.save(data)

    def load_all(self) -> dict[str, Any]:
        return {
            "tally": self.load_tally(),
            "goals": self.load_goals(),
            "vendors": self.load_vendors(),
        }

    def save_all(self, state: dict[str, Any]) -> None:
        merged: dict[str, Any] = {}
        if "tally" in state:
            merged["scrips"] = state["tally"].to_dict()
        if "goals" in state:
            merged["goals"] = state["goals"].to_dict()
        if "vendors" in state:
            merged["vendors"] = state["vendors"].to_dict()
        self.save(merged)
