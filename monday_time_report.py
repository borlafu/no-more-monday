#!/usr/bin/env python3
"""Usage: monday_time_report.py <jwt_session_token> <item_id> [column_id]"""

import json, sys, subprocess
from datetime import datetime, date
from collections import defaultdict


def prompt_start_date() -> date:
    today = date.today()
    default = date(today.year, today.month, 1)
    raw = input(f"Start date [YYYY-MM-DD] (default: {default}): ").strip()
    if not raw:
        return default
    try:
        return date.fromisoformat(raw)
    except ValueError:
        print(f"  Invalid date '{raw}', using default: {default}")
        return default


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    jwt = sys.argv[1]
    item_id = sys.argv[2]
    column_id = sys.argv[3] if len(sys.argv) > 3 else "seguimiento_del_tiempo__1"
    cookies = f"jwt_session_token={jwt}"

    start_date = prompt_start_date()

    result = subprocess.run(
        [
            "curl",
            "-s",
            f"https://gs-grupo.monday.com/duration_column_history/{item_id}/{column_id}",
            "-H",
            "accept: application/json",
            "-H",
            "x-requested-with: XMLHttpRequest",
            "-H",
            "origin: https://gs-grupo.monday.com",
            "-b",
            cookies,
        ],
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    daily, weekly = defaultdict(float), defaultdict(float)
    skipped = 0
    for entry in data:
        start = datetime.fromisoformat(entry["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(entry["ended_at"].replace("Z", "+00:00"))
        day = start.date()
        if day < start_date:
            skipped += 1
            continue
        hours = (end - start).total_seconds() / 3600
        year, week, _ = start.isocalendar()
        daily[day] += hours
        weekly[f"{year}-W{week:02d}"] += hours

    print(f"\n=== DAILY REPORT (from {start_date}) ===")
    for day in sorted(daily):
        print(f"  {day}  ({day.strftime('%A'):<9})  {daily[day]:.2f}h")

    print("\n=== WEEKLY REPORT ===")
    for week in sorted(weekly):
        print(f"  {week}  {weekly[week]:.2f}h")

    total_days = len(daily)
    total_hours = sum(daily.values())
    print(f"\n  Total: {total_hours:.2f}h over {total_days} day{'s' if total_days != 1 else ''}")
    if skipped:
        print(f"  ({skipped} entr{'ies' if skipped != 1 else 'y'} before {start_date} excluded)")


if __name__ == "__main__":
    main()
