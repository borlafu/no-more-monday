#!/usr/bin/env python3
"""Usage: monday_time_input.py <jwt_session_token> <item_id> [--start-time HH:MM] [--end-time HH:MM]"""

import json, sys, subprocess, calendar, argparse, os
from datetime import datetime, date, timedelta, timezone


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


load_env()

MONDAY_TENANT = os.getenv("MONDAY_TENANT", "gs-grupo")
COLUMN_ID = os.getenv("COLUMN_ID", "seguimiento_del_tiempo__1")
DEFAULT_START_TIME = "09:00"
DEFAULT_END_TIME = "11:00"

# ── Helpers ───────────────────────────────────────────────────────────────────


def prompt_date(label: str, default: date) -> date:
    raw = input(f"{label} [YYYY-MM-DD] (default: {default}): ").strip()
    if not raw:
        return default
    try:
        return date.fromisoformat(raw)
    except ValueError:
        print(f"  Invalid date '{raw}', using default: {default}")
        return default


def prompt_time(label: str, default: str) -> str:
    raw = input(f"  {label} [HH:MM] (default: {default}): ").strip()
    if not raw:
        return default
    try:
        datetime.strptime(raw, "%H:%M")
        return raw
    except ValueError:
        print(f"  Invalid time '{raw}', using default: {default}")
        return default


def prompt_str(label: str, default: str = "") -> str:
    display = f" (default: {default})" if default else ""
    raw = input(f"{label}{display}: ").strip()
    return raw if raw else default


def make_iso(day: date, time_str: str) -> str:
    dt = datetime.strptime(f"{day} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── API calls ─────────────────────────────────────────────────────────────────


def fetch_entries(base_url: str, cookies: str, csrf: str) -> list:
    result = subprocess.run(
        [
            "curl",
            "-s",
            base_url,
            "-H",
            "accept: application/json",
            "-H",
            "x-requested-with: XMLHttpRequest",
            "-H",
            f"origin: https://{MONDAY_TENANT}.monday.com",
            "-H",
            f"x-csrf-token: {csrf}",
            "-b",
            cookies,
        ],
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def post_entry(base_url: str, cookies: str, csrf: str, started_at: str, ended_at: str) -> dict:
    payload = json.dumps({"started_at": started_at, "ended_at": ended_at})
    result = subprocess.run(
        [
            "curl",
            "-s",
            base_url,
            "-X",
            "POST",
            "-H",
            "accept: application/json, text/javascript, */*; q=0.01",
            "-H",
            "content-type: application/json",
            "-H",
            "x-requested-with: XMLHttpRequest",
            "-H",
            f"origin: https://{MONDAY_TENANT}.monday.com",
            "-H",
            f"x-csrf-token: {csrf}",
            "-b",
            cookies,
            "--data-raw",
            payload,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Monday.com Time Backfill")
    parser.add_argument("jwt", help="JWT session token")
    parser.add_argument("item_id", help="Item ID")
    parser.add_argument(
        "--start-time",
        default=DEFAULT_START_TIME,
        help=f"Default daily start time (HH:MM, default: {DEFAULT_START_TIME})",
    )
    parser.add_argument(
        "--end-time",
        default=DEFAULT_END_TIME,
        help=f"Default daily end time (HH:MM, default: {DEFAULT_END_TIME})",
    )
    args = parser.parse_args()

    jwt = args.jwt
    item_id = args.item_id
    column_id = COLUMN_ID
    start_t = args.start_time
    end_t = args.end_time

    print("=== Monday.com Time Backfill ===\n")

    # Credentials & CORS tokens
    csrf = prompt_str("x-csrf-token")

    # Date range
    today = date.today()
    default_start = date(today.year, today.month, 1)
    start_date = prompt_date("\nStart date", default_start)
    _, last_day = calendar.monthrange(today.year, today.month)
    end_date = date(today.year, today.month, last_day)

    # Weekend behaviour
    skip_weekends_ans = input("Skip weekends automatically? [Y/n]: ").strip().lower()
    skip_weekends = skip_weekends_ans != "n"

    cookies = f"jwt_session_token={jwt}"
    base_url = f"https://{MONDAY_TENANT}.monday.com/duration_column_history/{item_id}/{column_id}"

    # Fetch all existing entries once
    print("\nFetching existing entries…")
    entries = fetch_entries(base_url, cookies, csrf)
    if not isinstance(entries, list):
        print(f"  Unexpected response: {entries}")
        sys.exit(1)

    existing_days: set[date] = set()
    for entry in entries:
        d = datetime.fromisoformat(entry["started_at"].replace("Z", "+00:00")).date()
        existing_days.add(d)

    print(f"  Found {len(entries)} entries across {len(existing_days)} days.")
    print(f"  Backfilling from {start_date} to {end_date}.\n")

    # Iterate day by day
    added = skipped = 0
    current = start_date
    while current <= end_date:
        weekday = current.strftime("%A")
        is_future = current > today
        is_weekend = current.weekday() >= 5  # 5=Saturday, 6=Sunday

        if current in existing_days:
            print(f"  {current} ({weekday:<9}) — already has an entry, skipping.")
            current += timedelta(days=1)
            continue

        if skip_weekends and is_weekend:
            print(f"  {current} ({weekday:<9}) — weekend, skipping.")
            skipped += 1
            current += timedelta(days=1)
            continue

        future_tag = " [future]" if is_future else ""
        ans = input(f"  {current} ({weekday:<9}){future_tag} — no entry. Add one? [Y/n]: ").strip().lower()
        if ans == "n":
            print("    Skipped.")
            skipped += 1
            current += timedelta(days=1)
            continue

        start_t = prompt_time("    Start time", start_t)
        end_t = prompt_time("    End time  ", end_t)

        started_at = make_iso(current, start_t)
        ended_at = make_iso(current, end_t)

        resp = post_entry(base_url, cookies, csrf, started_at, ended_at)

        if "id" in resp or "started_at" in resp:
            hours = (
                datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                - datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            ).total_seconds() / 3600
            print(f"    ✓ Added {hours:.2f}h  ({started_at} → {ended_at})")
            added += 1
        else:
            print(f"    ✗ Unexpected response: {resp}")

        current += timedelta(days=1)

    print(f"\nDone. {added} entr{'ies' if added != 1 else 'y'} added, {skipped} skipped.")


if __name__ == "__main__":
    main()
