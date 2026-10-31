"""Command line interface for the FFXIV scrip tracker."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Optional

from .alerts import AlertChecker
from .goals import GoalBook, SpendingGoal
from .scrips import ScripTally, ScripType, SCRIP_TYPES
from .storage import Storage
from .vendors import VendorBook, VendorUnlock

DEFAULT_DATA_FILE = "scrip_data.json"


def _data_path(override: Optional[str]) -> str:
    if override:
        return override
    return os.environ.get("SCRIP_TRACKER_DATA", DEFAULT_DATA_FILE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrip-tracker",
        description=(
            "Track FFXIV white and purple scrips, vendor unlocks, and "
            "spending goals. Local-first JSON storage with CSV export."
        ),
    )
    parser.add_argument(
        "--data",
        default=None,
        help="Path to JSON storage file (default: scrip_data.json, or "
        "$SCRIP_TRACKER_DATA)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    def add_scrip_subcommand(name: str, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("scrip_type", choices=list(SCRIP_TYPES))
        p.add_argument("amount", type=int, help="Positive whole number of scrips")
        p.add_argument("--note", default="", help="Optional note for the transaction")
        return p

    add_scrip_subcommand("earn", "Record scrips earned")
    add_scrip_subcommand("spend", "Record scrips spent")

    p_balance = sub.add_parser("balance", help="Show current scrip balances")
    p_balance.add_argument(
        "--white", action="store_true", help="Show only white scrips"
    )
    p_balance.add_argument(
        "--purple", action="store_true", help="Show only purple scrips"
    )

    p_goal_add = sub.add_parser("goal-add", help="Add a spending goal")
    p_goal_add.add_argument("name", help="Goal name")
    p_goal_add.add_argument("scrip_type", choices=list(SCRIP_TYPES))
    p_goal_add.add_argument("target", type=int, help="Target scrip budget")
    p_goal_add.add_argument(
        "--alert-at",
        type=float,
        default=0.8,
        help="Fraction of target at which to alert (0-1, default 0.8)",
    )

    p_goal_spend = sub.add_parser("goal-spend", help="Record spend toward a goal")
    p_goal_spend.add_argument("name", help="Goal name")
    p_goal_spend.add_argument("amount", type=int)

    sub.add_parser("goal-list", help="List spending goals and progress")

    p_vendor_add = sub.add_parser("vendor-add", help="Track a scrip vendor")
    p_vendor_add.add_argument("name", help="Vendor name")
    p_vendor_add.add_argument("location", help="Vendor location")
    p_vendor_add.add_argument(
        "--unlocked",
        action="store_true",
        help="Mark the vendor as unlocked right away",
    )
    p_vendor_unlock = sub.add_parser("vendor-unlock", help="Mark a vendor unlocked")
    p_vendor_unlock.add_argument("name", help="Vendor name")
    sub.add_parser("vendor-list", help="List tracked vendors and unlock status")

    p_export = sub.add_parser("export", help="Export transactions to CSV")
    p_export.add_argument("file", help="Output CSV path")

    sub.add_parser("status", help="Show balances, goals, vendors, and alerts")
    sub.add_parser("alert", help="Check and print spending goal alerts")

    return parser


def _load_state(args: argparse.Namespace) -> tuple[Storage, ScripTally, GoalBook, VendorBook]:
    storage = Storage(_data_path(args.data))
    tally = storage.load_tally()
    goals = storage.load_goals()
    vendors = storage.load_vendors()
    return storage, tally, goals, vendors


def _save_state(storage: Storage, tally: ScripTally, goals: GoalBook, vendors: VendorBook) -> None:
    storage.save_all({"tally": tally, "goals": goals, "vendors": vendors})


def cmd_earn(args: argparse.Namespace, tally: ScripTally) -> int:
    tally.earn(args.scrip_type, args.amount, args.note)
    print(f"Earned {args.amount} {args.scrip_type} scrips{f' ({args.note})' if args.note else ''}.")
    print(f"New {args.scrip_type} balance: {tally.balance(args.scrip_type)}")
    return 0


def cmd_spend(args: argparse.Namespace, tally: ScripTally) -> int:
    try:
        tally.spend(args.scrip_type, args.amount, args.note)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Spent {args.amount} {args.scrip_type} scrips{f' ({args.note})' if args.note else ''}.")
    print(f"New {args.scrip_type} balance: {tally.balance(args.scrip_type)}")
    return 0


def cmd_balance(args: argparse.Namespace, tally: ScripTally) -> int:
    types_to_show = list(SCRIP_TYPES)
    if args.white and not args.purple:
        types_to_show = ["white"]
    if args.purple and not args.white:
        types_to_show = ["purple"]
    for scrip_type in types_to_show:
        print(f"{scrip_type.capitalize()} scrips: {tally.balance(scrip_type)}")
    print(f"Total: {tally.total()}")
    return 0


def cmd_goal_add(args: argparse.Namespace, goals: GoalBook) -> int:
    try:
        goal = SpendingGoal(
            name=args.name,
            scrip_type=args.scrip_type,
            target=args.target,
            alert_at=args.alert_at,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    goals.add(goal)
    print(f"Added goal: {goal.status_line()}")
    return 0


def cmd_goal_spend(args: argparse.Namespace, goals: GoalBook) -> int:
    try:
        goal = goals.spend(args.name, args.amount)
    except KeyError as exc:
        print(f"Error: {exc}")
        return 1
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Recorded {args.amount} spent toward '{args.name}'.")
    print(goal.status_line())
    if goal.met:
        print("Goal met!")
    return 0


def cmd_goal_list(args: argparse.Namespace, goals: GoalBook) -> int:
    if not goals.goals:
        print("No spending goals yet. Add one with: scrip-tracker goal-add ...")
        return 0
    for goal in goals.goals:
        alert = "  <-- ALERT" if goal.should_alert() else ""
        print(f"{goal.status_line()}{alert}")
    return 0


def cmd_vendor_add(args: argparse.Namespace, vendors: VendorBook) -> int:
    try:
        vendors.add(
            VendorUnlock(name=args.name, location=args.location, unlocked=args.unlocked)
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    status = "unlocked" if args.unlocked else "locked"
    print(f"Tracked vendor '{args.name}' at {args.location} ({status}).")
    return 0


def cmd_vendor_unlock(args: argparse.Namespace, vendors: VendorBook) -> int:
    try:
        vendors.unlock(args.name)
    except KeyError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Vendor '{args.name}' is now unlocked.")
    return 0


def cmd_vendor_list(args: argparse.Namespace, vendors: VendorBook) -> int:
    if not vendors.vendors:
        print("No vendors tracked yet. Add one with: scrip-tracker vendor-add ...")
        return 0
    for vendor in vendors.vendors:
        mark = "[X]" if vendor.unlocked else "[ ]"
        print(f"{mark} {vendor.name} - {vendor.location}" + (f" ({vendor.notes})" if vendor.notes else ""))
    return 0


def cmd_export(args: argparse.Namespace, tally: ScripTally) -> int:
    transactions = tally.transactions_for()
    with open(args.file, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "scrip_type", "amount", "delta", "note"])
        for tx in transactions:
            writer.writerow([tx.timestamp, tx.scrip_type, tx.amount, tx.delta, tx.note])
    print(f"Exported {len(transactions)} transactions to {args.file}")
    return 0


def cmd_status(args: argparse.Namespace, tally: ScripTally, goals: GoalBook, vendors: VendorBook) -> int:
    print("=== FFXIV Scrip Tracker ===")
    print()
    print("Balances:")
    for scrip_type in SCRIP_TYPES:
        print(f"  {scrip_type.capitalize()}: {tally.balance(scrip_type)}")
    print(f"  Total: {tally.total()}")
    print()
    print("Spending goals:")
    if not goals.goals:
        print("  (none)")
    else:
        for goal in goals.goals:
            print(f"  {goal.status_line()}")
    print()
    print("Vendor unlocks:")
    if not vendors.vendors:
        print("  (none)")
    else:
        for vendor in vendors.vendors:
            mark = "[X]" if vendor.unlocked else "[ ]"
            print(f"  {mark} {vendor.name} - {vendor.location}")
    print()
    checker = AlertChecker(goals)
    print(checker.format())
    return 0


def cmd_alert(args: argparse.Namespace, goals: GoalBook) -> int:
    checker = AlertChecker(goals)
    print(checker.format())
    return 0


COMMAND_HANDLERS = {
    "earn": lambda args, state: cmd_earn(args, state[1]),
    "spend": lambda args, state: cmd_spend(args, state[1]),
    "balance": lambda args, state: cmd_balance(args, state[1]),
    "goal-add": lambda args, state: cmd_goal_add(args, state[2]),
    "goal-spend": lambda args, state: cmd_goal_spend(args, state[2]),
    "goal-list": lambda args, state: cmd_goal_list(args, state[2]),
    "vendor-add": lambda args, state: cmd_vendor_add(args, state[3]),
    "vendor-unlock": lambda args, state: cmd_vendor_unlock(args, state[3]),
    "vendor-list": lambda args, state: cmd_vendor_list(args, state[3]),
    "export": lambda args, state: cmd_export(args, state[1]),
    "status": lambda args, state: cmd_status(args, state[1], state[2], state[3]),
    "alert": lambda args, state: cmd_alert(args, state[2]),
}


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    state = _load_state(args)
    try:
        handler = COMMAND_HANDLERS[args.command]
    except KeyError:
        parser.print_help()
        return 2
    try:
        return handler(args, state)
    finally:
        _save_state(*state)


if __name__ == "__main__":
    sys.exit(main())
