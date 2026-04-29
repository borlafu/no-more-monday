# No More Monday

Automate time tracking and reporting for Monday.com. Backfill time entries and generate detailed daily/weekly reports without manual data entry.

## Features

- **Time Entry Backfill**: Automatically populate Monday.com duration columns with time entries
- **Smart Weekend Skip**: Optionally skip weekends when backfilling
- **Interactive Prompts**: User-friendly input for dates, times, and authentication
- **Daily Reports**: View hours logged per day with day-of-week labels
- **Weekly Reports**: Aggregate hours by ISO week numbers
- **Flexible Configuration**: Support for custom Monday.com boards and columns

## Scripts

### `monday_time_input.py` — Backfill Time Entries

Batch-populate time entries for a date range with interactive prompts and weekend skipping.

**Usage:**

```bash
python3 monday_time_input.py <jwt_session_token> <item_id> [column_id]
```

**Parameters:**

- `jwt_session_token`: Your Monday.com JWT session token (from cookies)
- `item_id`: Monday.com item ID for the duration column
- `column_id` *(optional)*: Column ID (default: `seguimiento_del_tiempo__1`)

**Example:**

```bash
python3 monday_time_input.py "eyJhbGc..." "12345678" "seguimiento_del_tiempo__1"
```

**Interactive Prompts:**

- `x-csrf-token`: CSRF token from request headers (required for API calls)
- `Start date`: Beginning of backfill range (default: 1st of current month)
- `Skip weekends?`: Automatically skip Saturdays and Sundays

**Defaults:**

- Start time: `17:00`
- End time: `19:00`

### `monday_time_report.py` — Generate Time Reports

Fetch time entries and display aggregated daily and weekly summaries.

**Usage:**

```bash
python3 monday_time_report.py <jwt_session_token> <item_id> [column_id]
```

**Parameters:**

- `jwt_session_token`: Your Monday.com JWT session token
- `item_id`: Monday.com item ID for the duration column
- `column_id` *(optional)*: Column ID (default: `seguimiento_del_tiempo__1`)

**Example:**

```bash
python3 monday_time_report.py "eyJhbGc..." "12345678"
```

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

## Prerequisites

1. **Python 3+**
2. **curl** (for HTTP requests)
3. **Monday.com Account Access**
   - JWT session token (found in browser cookies or request headers)
   - Item ID (visible in Monday.com board URL or API)
   - Column ID (can be extracted from API responses)

### How to Get Your JWT Token

1. Open Monday.com in your browser
2. Open Developer Tools (F12 / Cmd+Shift+I)
3. Go to **Application** → **Cookies**
4. Find the `jwt_session_token` cookie and copy its value

### How to Get CSRF Token

1. In Developer Tools, go to **Network** tab
2. Make a request to your Monday.com board
3. Look for any POST request headers
4. Find the `x-csrf-token` header value

## Installation

No external dependencies required beyond Python 3 and curl (both standard on macOS and Linux).

```bash
git clone <repo-url>
cd no-more-monday
chmod +x monday_time_*.py
```

## Security Notes

⚠️ **Never commit JWT or CSRF tokens to version control.**

- Keep tokens in environment variables or a local `.env` file
- Use `.gitignore` to prevent accidental commits

## Workflow Example

1. **Backfill entries:**

   ```bash
   python3 monday_time_input.py $JWT_TOKEN 12345678
   ```

   - Set start date to 1st of month
   - Skip weekends: `Y`
   - CSRF token when prompted

2. **Generate report:**

   ```bash
   python3 monday_time_report.py $JWT_TOKEN 12345678
   ```

   - View daily and weekly summaries
   - Verify all entries were logged correctly

## License

See [LICENSE](LICENSE) for details.
