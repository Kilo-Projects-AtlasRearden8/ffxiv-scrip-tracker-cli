"""Tally logic for FFXIV white and purple scrips."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Literal

ScripType = Literal["white", "purple"]
SCRIP_TYPES: tuple[ScripType, ...] = ("white", "purple")


@dataclass
class Transaction:
    """A single scrip earn or spend event."""

    scrip_type: ScripType
    amount: int
    delta: int
    timestamp: str
    note: str = ""


@dataclass
class ScripAccount:
    """Running tally for one scrip type."""

    balance: int = 0
    transactions: list[Transaction] = field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ScripTally:
    """Tracks earned and spent white and purple scrips."""

    def __init__(self) -> None:
        self.accounts: dict[ScripType, ScripAccount] = {
            scrip_type: ScripAccount() for scrip_type in SCRIP_TYPES
        }

    def earn(self, scrip_type: ScripType, amount: int, note: str = "") -> None:
        """Record scrips earned."""
        self._validate_type(scrip_type)
        self._validate_amount(amount)
        account = self.accounts[scrip_type]
        account.balance += amount
        account.transactions.append(
            Transaction(scrip_type, amount, amount, _now(), note)
        )

    def spend(self, scrip_type: ScripType, amount: int, note: str = "") -> None:
        """Record scrips spent. Cannot drop a balance below zero."""
        self._validate_type(scrip_type)
        self._validate_amount(amount)
        account = self.accounts[scrip_type]
        if account.balance - amount < 0:
            raise ValueError(
                f"Insufficient {scrip_type} scrips: have {account.balance}, "
                f"trying to spend {amount}"
            )
        account.balance -= amount
        account.transactions.append(
            Transaction(scrip_type, amount, -amount, _now(), note)
        )

    def balance(self, scrip_type: ScripType) -> int:
        self._validate_type(scrip_type)
        return self.accounts[scrip_type].balance

    def total(self) -> int:
        return sum(account.balance for account in self.accounts.values())

    def transactions_for(self, scrip_type: ScripType | None = None) -> list[Transaction]:
        self._validate_type(scrip_type) if scrip_type is not None else None
        if scrip_type is None:
            result: list[Transaction] = []
            for account in self.accounts.values():
                result.extend(account.transactions)
            return result
        return list(self.accounts[scrip_type].transactions)

    @staticmethod
    def _validate_type(scrip_type: ScripType) -> None:
        if scrip_type not in SCRIP_TYPES:
            raise ValueError(
                f"Unknown scrip type: {scrip_type!r}. Use 'white' or 'purple'."
            )

    @staticmethod
    def _validate_amount(amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise ValueError(f"Amount must be a positive integer, got {amount!r}.")

    # --- serialization -------------------------------------------------

    def to_dict(self) -> dict:
        return {
            scrip_type: {
                "balance": account.balance,
                "transactions": [asdict(tx) for tx in account.transactions],
            }
            for scrip_type, account in self.accounts.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScripTally":
        tally = cls()
        for scrip_type in SCRIP_TYPES:
            section = data.get(scrip_type, {})
            account = ScripAccount(balance=int(section.get("balance", 0)))
            for tx in section.get("transactions", []):
                account.transactions.append(
                    Transaction(
                        scrip_type=tx["scrip_type"],
                        amount=int(tx["amount"]),
                        delta=int(tx["delta"]),
                        timestamp=str(tx["timestamp"]),
                        note=str(tx.get("note", "")),
                    )
                )
            tally.accounts[scrip_type] = account
        return tally
