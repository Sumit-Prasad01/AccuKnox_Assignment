"""
Task 3: Import users from a CSV file into SQLite.
"""

import csv
import sqlite3
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "assignment.db"
CSV_PATH = Path(__file__).resolve().parent / "users.csv"

REQUIRED_FIELDS = ("name", "email")


def read_users_from_csv(csv_path):
    """
    Read and validate user records from a CSV file.
    Trims whitespace, skips invalid rows with missing name or email,
    and supports extra optional columns such as role and department.
    Returns (valid_rows, total_rows_read, skipped_count, extra_fields).
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    valid_rows = []
    total_rows = 0
    skipped_count = 0
    extra_fields = []

    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Check required headers
        missing_headers = [field for field in REQUIRED_FIELDS if field not in headers]
        if missing_headers:
            raise ValueError(f"CSV is missing required header(s): {', '.join(missing_headers)}")

        extra_fields = [h for h in headers if h not in REQUIRED_FIELDS]

        for row_idx, row in enumerate(reader, start=2):  # row 1 is header
            total_rows += 1
            # Trim whitespace
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip()

            if not name or not email:
                print(f"Warning: Skipping row #{row_idx}: name or email is missing/empty ({row}).")
                skipped_count += 1
                continue

            cleaned_row = {
                "name": name,
                "email": email,
            }
            for field in extra_fields:
                cleaned_row[field] = (row.get(field) or "").strip()

            valid_rows.append(cleaned_row)

    return valid_rows, total_rows, skipped_count, extra_fields


def create_users_table(connection, extra_fields):
    """Create the users table if it does not exist, including optional extra fields."""
    columns_def = [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "name TEXT NOT NULL",
        "email TEXT NOT NULL UNIQUE"
    ]
    for field in extra_fields:
        columns_def.append(f"{field} TEXT")

    sql = f"CREATE TABLE IF NOT EXISTS users ({', '.join(columns_def)});"
    connection.execute(sql)

    # In case the table was created previously without optional extra columns, ensure they exist
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(users);")
    existing_cols = {col[1] for col in cursor.fetchall()}
    for field in extra_fields:
        if field not in existing_cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {field} TEXT;")


def insert_users(connection, users, extra_fields):
    """
    Insert valid users into SQLite using INSERT OR IGNORE to prevent duplicate emails.
    Returns (inserted_count, ignored_count).
    """
    fields = ["name", "email"] + extra_fields
    placeholders = ", ".join(["?"] * len(fields))
    columns_str = ", ".join(fields)
    sql = f"INSERT OR IGNORE INTO users ({columns_str}) VALUES ({placeholders});"

    cursor = connection.cursor()
    inserted_count = 0
    ignored_count = 0

    for user in users:
        values = tuple(user[f] for f in fields)
        cursor.execute(sql, values)
        if cursor.rowcount > 0:
            inserted_count += 1
        else:
            ignored_count += 1

    connection.commit()
    return inserted_count, ignored_count


def display_users(connection, extra_fields):
    """Query and print all users currently stored in the database."""
    fields = ["id", "name", "email"] + extra_fields
    columns_str = ", ".join(fields)
    cursor = connection.cursor()
    cursor.execute(f"SELECT {columns_str} FROM users ORDER BY id ASC;")
    rows = cursor.fetchall()

    print("\nUsers in database:")
    if not rows:
        print("No users found in database.")
        return

    for row in rows:
        row_id, name, email = row[0], row[1], row[2]
        extra_vals = [str(val) if val else "N/A" for val in row[3:]]
        details = " | ".join([f"{row_id}. {name}", email] + extra_vals)
        print(details)


def main():
    """Run the CSV-to-SQLite import workflow."""
    print(f"Reading user data from {CSV_PATH.name}...")

    try:
        users, total_read, skipped_count, extra_fields = read_users_from_csv(CSV_PATH)
    except (FileNotFoundError, ValueError, OSError) as err:
        print(f"Error reading CSV: {err}", file=sys.stderr)
        sys.exit(1)

    # Ensure database directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            create_users_table(conn, extra_fields)
            inserted_count, ignored_count = insert_users(conn, users, extra_fields)

            total_skipped_or_ignored = skipped_count + ignored_count
            print(f"\nRows read: {total_read}")
            print(f"Users inserted: {inserted_count}")
            print(f"Rows skipped or ignored: {total_skipped_or_ignored}")

            display_users(conn, extra_fields)
    except sqlite3.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
