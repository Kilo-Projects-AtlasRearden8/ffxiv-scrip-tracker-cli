# FFXIV Scrip Tracker CLI

A local-first Python command line tool for tracking **Final Fantasy XIV**
white and purple scrips, scrip vendor unlocks, and spending goals. Built for
gamers who want a simple, private, offline way to plan their scrip earnings
and spending.

This is a fan project. It is not affiliated with or endorsed by Square Enix.
Credit: **Asdale Dynamics, LLC**.

## Who this is for

Dylan Asdale is a registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). His book *The
Massive AI Manual* and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending.

Asdale Dynamics focuses on beginner-friendly AI education, books and guides,
and practical tools the LLC can publish or sell — from AI agent skills and
local-LLM utilities to small-business and author tools, accessible life-admin
helpers, and fun extras like gaming and chess tools. This FFXIV scrip tracker
is one of those fun extras: clear, warm, polished, tested, local-first, and
free of secrets or personal data.

## Features

- Track white and purple scrip balances with dated transactions
- Record scrips earned and spent (cannot spend more than you have)
- Set spending goals with progress bars and configurable alert thresholds
- Track scrip vendor unlocks (locked / unlocked)
- Check progress alerts for goals approaching or meeting their target
- Export all transactions to CSV
- Local JSON storage only — no accounts, no network, no personal data

## Install

No external dependencies. Python 3.8+ is all you need.

```bash
# Clone or copy this folder, then run directly
python -m ffxiv_scrip_tracker --help
```

Or install it in editable mode so the `scrip-tracker` command is available
everywhere:

```bash
pip install -e .
```

Then:

```bash
scrip-tracker --help
```

*(A minimal `pyproject.toml` is not included; run from the project folder or
add one if you want a console script entry point.)*

## Quick start

```bash
# Record some scrip earnings
python -m ffxiv_scrip_tracker earn white 1500 --note "Weekly tomestone cap"
python -m ffxiv_scrip_tracker earn purple 120 --note "Red-tailed tropic turn-in"

# Check balances
python -m ffxiv_scrip_tracker balance

# Spend scrips
python -m ffxiv_scrip_tracker spend purple 100 --note "Gathering gear"

# Set a spending goal (alerts at 80% by default)
python -m ffxiv_scrip_tracker goal-add "Crafting gear" purple 500 --alert-at 0.8
python -m ffxiv_scrip_tracker goal-spend "Crafting gear" 100

# Track a vendor
python -m ffxiv_scrip_tracker vendor-add "Rowena" "Mor Dhona"
python -m ffxiv_scrip_tracker vendor-unlock "Rowena"

# Full status with goals and alerts
python -m ffxiv_scrip_tracker status

# Export everything to CSV
python -m ffxiv_scrip_tracker export scrips.csv
```

## Storage

Data is saved to `scrip_data.json` in the current folder. Change the location
with `--data` or the `SCRIP_TRACKER_DATA` environment variable:

```bash
SCRIP_TRACKER_DATA=~/scrip-tracker.json python -m ffxiv_scrip_tracker status
```

Everything stays on your machine. Nothing is uploaded.

## Tests

```bash
python -m unittest discover -s tests
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

Credit: Asdale Dynamics, LLC.

## Fan project notice

This tool is an independent fan project and is not affiliated with, endorsed
by, or sponsored by Square Enix. Final Fantasy XIV and related trademarks are
the property of their respective owners.
