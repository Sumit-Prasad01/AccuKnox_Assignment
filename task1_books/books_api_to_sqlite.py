"""
Task 1: Fetch books from Open Library REST API and store them in SQLite.
"""

import sqlite3
import sys
from pathlib import Path
import requests

# Base directory and database path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "assignment.db"

API_URL = "https://openlibrary.org/subjects/fiction.json?limit=20"
REQUEST_TIMEOUT_SECONDS = 15


def fetch_books():
    """
    Fetch book records from the Open Library Subjects API.
    Returns a list of tuples: (title, author, publication_year).
    """
    try:
        response = requests.get(API_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {REQUEST_TIMEOUT_SECONDS}s while fetching books.", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error: Network or HTTP failure fetching books: {err}", file=sys.stderr)
        return None
    except ValueError as err:
        print(f"Error: Failed to parse JSON response: {err}", file=sys.stderr)
        return None

    works = data.get("works")
    if not isinstance(works, list):
        print("Error: Unexpected response format: 'works' field missing or not a list.", file=sys.stderr)
        return None

    books = []
    for work in works:
        title = work.get("title") or "Unknown Title"
        authors = work.get("authors", [])
        author = authors[0].get("name") if authors and isinstance(authors, list) and isinstance(authors[0], dict) else "Unknown author"
        pub_year = work.get("first_publish_year")
        books.append((title, author, pub_year))

    return books


def create_books_table(connection):
    """Create the books table if it does not exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        publication_year INTEGER
    );
    """
    connection.execute(create_table_sql)


def save_books(connection, books):
    """
    Save fetched book records into SQLite.
    Replaces existing rows with the newly fetched records to avoid duplicates.
    """
    cursor = connection.cursor()
    # Clear existing records before inserting fresh records
    cursor.execute("DELETE FROM books;")
    insert_sql = """
    INSERT INTO books (title, author, publication_year)
    VALUES (?, ?, ?);
    """
    cursor.executemany(insert_sql, books)
    connection.commit()
    return len(books)


def display_books(connection):
    """Read and print saved books from the database."""
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, author, publication_year FROM books ORDER BY id ASC;")
    rows = cursor.fetchall()

    print("\nBooks stored in database:")
    if not rows:
        print("No books found in the database.")
        return

    for row_id, title, author, year in rows:
        author_display = author if author else "Unknown author"
        year_display = year if year is not None else "Unknown year"
        print(f"{row_id}. {title} | {author_display} | {year_display}")


def main():
    """Run the complete book fetching and storage workflow."""
    print("Fetching books from Open Library API...")
    books = fetch_books()
    if books is None:
        print("Aborting database update to protect existing records.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(books)} books.")

    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            create_books_table(conn)
            saved_count = save_books(conn, books)
            print(f"Saved {saved_count} books to SQLite ({DB_PATH.name}).")
            display_books(conn)
    except sqlite3.Error as err:
        print(f"Database error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
