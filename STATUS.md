# STATUS

## What was built

A local-first Python CLI for tracking Final Fantasy XIV white and purple scrips,
scrip vendor unlocks, and spending goals.

Package `ffxiv_scrip_tracker`:
- `scrips.py` — `ScripTally` tracking earned/spent scrips per type with dated
  transactions, serialization round-trip, and balance guards.
- `goals.py` — `SpendingGoal` and `GoalBook`: targets, spend tracking, progress
  bars, configurable alert thresholds, met/remaining logic.
- `vendors.py` — `VendorUnlock` and `VendorBook` for locked/unlocked vendors.
- `storage.py` — `Storage` reading/writing all state to one local JSON file.
- `alerts.py` — `AlertChecker` producing human-readable goal alert messages.
- `cli.py` — argparse CLI: earn, spend, balance, goal-add, goal-spend,
  goal-list, vendor-add, vendor-unlock, vendor-list, export, status, alert.
- `__main__.py` — `python -m ffxiv_scrip_tracker` entry point.

Tests:
- `tests/test_scrips.py` — tally earn/spend/balance/serialization/validation.
- `tests/test_goals.py` — goal progress, remaining, alerts, spend, book logic.

Other files:
- `LICENSE` — MIT, copyright line exactly "Copyright (c) 2026 Asdale Dynamics, LLC".
- `README.md` — usage, quick start, storage, tests, license, fan-project notice,
  credit to Asdale Dynamics, LLC.
- `STATUS.md` — this file.

## How to run it

Requires Python 3.8+ (tested on Python 3.13.5). No external dependencies.

```bash
cd /workspace/kilo-lab/ffxiv-scrip-tracker-cli
python3 -m ffxiv_scrip_tracker --help
```

Example session:

```bash
python3 -m ffxiv_scrip_tracker earn white 1500 --note "weekly cap"
python3 -m ffxiv_scrip_tracker earn purple 120 --note "turn-ins"
python3 -m ffxiv_scrip_tracker spend purple 100 --note "gear"
python3 -m ffxiv_scrip_tracker goal-add "Crafting gear" purple 500 --alert-at 0.8
python3 -m ffxiv_scrip_tracker goal-spend "Crafting gear" 400
python3 -m ffxiv_scrip_tracker vendor-add "Rowena" "Mor Dhona"
python3 -m ffxiv_scrip_tracker vendor-unlock "Rowena"
python3 -m ffxiv_scrip_tracker status
python3 -m ffxiv_scrip_tracker export scrips.csv
```

Data is saved to `scrip_data.json` in the current folder. Override with
`--data <path>` or the `SCRIP_TRACKER_DATA` environment variable.

## Verification results

- `python3 -m unittest discover -s tests -v`: 24 tests, OK (0 failures).
- `python3 -m ffxiv_scrip_tracker --help`: prints usage and all subcommands.
- End-to-end smoke test using a temp data file: earn, spend, goal-add,
  goal-spend, vendor-add, vendor-unlock, status, and CSV export all ran
  successfully; balances, progress bars, alert messages, vendor status, and
  CSV contents all correct.

## Known gaps

- No console-script entry point / `pyproject.toml`; run via `python3 -m`
  from the project folder or add packaging manually.
- No input validation beyond positive-integer amounts and non-negative balances
  (spending cannot drop below zero, which is enforced).
- No purge/reset command; delete the JSON file to start over.
- Goals track spend toward a target independent of actual scrip balance; they
  are not auto-linked to `tally.spend`.
- Single JSON file storage with last-write-wins; no file locking or concurrency
  safety.
- Fan project, not affiliated with or endorsed by Square Enix.
