# No More Monday

Automate time tracking and reporting for Monday.com. Backfill time entries and generate detailed daily/weekly reports without manual data entry.

## Features

- **Time Entry Backfill**: Automatically populate Monday.com duration columns with time entries
- **Smart Weekend Skip**: Optionally skip weekends when backfilling
- **Interactive Prompts**: User-friendly input for dates, times, and authentication
- **Daily Reports**: View hours logged per day with day-of-week labels
- **Weekly Reports**: Aggregate hours by ISO week numbers
- **Flexible Configuration**: Parameterized via `.env` file and CLI arguments

## Setup

### Prerequisites

1. Python 3
2. curl (standard on MacOS and Linux)
3. **Monday.com Account Access**
   - JWT session token (found in browser cookies or request headers)
   - Item ID (visible in Monday.com board URL or API)
   - Column ID (can be extracted from API responses)

#### How to Get Your JWT Token

1. Open Monday.com in your browser
2. Open Developer Tools (F12 / Cmd+Shift+I)
3. Go to **Application** → **Cookies**
4. Find the `jwt_session_token` cookie and copy its value

#### How to Get CSRF Token

1. In Developer Tools, go to **Network** tab
2. Make a request to your Monday.com board
3. Look for any POST request headers
4. Find the `x-csrf-token` header value

### Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your Monday.com details:

```env
MONDAY_TENANT=gs-grupo               # Your Monday.com subdomain
COLUMN_ID=seguimiento_del_tiempo__1  # The column ID for time tracking
```

## Scripts

### Backfill Time Entries

> `monday_time_input.py`

Batch-populate time entries for a date range with interactive prompts and weekend skipping.

**Usage:**

```bash
python3 monday_time_input.py <jwt_session_token> <item_id> [--start-time HH:MM] [--end-time HH:MM]
```

**Parameters:**

- `jwt_session_token`: Your Monday.com JWT session token (from cookies)
- `item_id`: Monday.com item ID for the duration column
- `--start-time` *(optional)*: Default daily start time (HH:MM, default: `09:00`)
- `--end-time` *(optional)*: Default daily end time (HH:MM, default: `11:00`)

**Examples:**

```bash
# Use default times (09:00–11:00)
python3 monday_time_input.py "eyJhbGc..." "12345678"

# Specify custom times
python3 monday_time_input.py "eyJhbGc..." "12345678" --start-time 08:30 --end-time 10:30
```

**Interactive Prompts:**

- `x-csrf-token`: CSRF token from request headers (required for API calls)
- `Start date`: Beginning of backfill range (default: 1st of current month)
- `Skip weekends?`: Automatically skip Saturdays and Sundays
- For each day without an entry, you'll be prompted for start and end times (uses your CLI defaults)

### Generate Time Reports

> `monday_time_report.py`

Fetch time entries and display aggregated daily and weekly summaries.

**Usage:**

```bash
python3 monday_time_report.py <jwt_session_token> <item_id> [--start-time HH:MM] [--end-time HH:MM]
```

**Parameters:**

- `jwt_session_token`: Your Monday.com JWT session token
- `item_id`: Monday.com item ID for the duration column
- `--start-time` *(optional)*: Reference start time (HH:MM, default: `09:00`, for documentation)
- `--end-time` *(optional)*: Reference end time (HH:MM, default: `11:00`, for documentation)

**Examples:**

```bash
# Generate report with defaults
python3 monday_time_report.py "eyJhbGc..." "12345678"

# With custom reference times
python3 monday_time_report.py "eyJhbGc..." "12345678" --start-time 08:00 --end-time 18:00
```

**Interactive Prompts:**

- `Start date`: Report start date (default: 1st of current month)

**Output:**

```text
=== DAILY REPORT (from 2026-04-01) ===
  2026-04-01  (Wednesday) 2.00h
  2026-04-02  (Thursday  ) 2.00h
  ...

=== WEEKLY REPORT ===
  2026-W13  40.00h
  2026-W14  35.50h

  Total: 75.50h over 38 days
```

## Security Notes

⚠️ **Never commit JWT or CSRF tokens to version control.**

- Keep tokens in environment variables or a local `.env` file
- Use `.gitignore` to prevent accidental commits

## License

See [LICENSE](LICENSE) for details.
