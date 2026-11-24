# Python Data Retrieval, Processing, Visualization, and CSV Import

A clean, modular, and beginner-friendly Python project implementing three core data engineering and visualization tasks using Python standard libraries alongside `requests` and `matplotlib`.

---

## Project Structure

```text
AccuKnox_Assignment/
├── task1_books/
│   └── books_api_to_sqlite.py    # Task 1: Fetch books from REST API & save to SQLite
├── task2_scores/
│   ├── student_scores.py         # Task 2: Fetch student scores, calculate avg & plot chart
│   └── sample_scores.json        # Fallback sample dataset for student scores
├── task3_csv_import/
│   ├── csv_to_sqlite.py          # Task 3: Import users from CSV to SQLite
│   └── users.csv                 # Sample users CSV data (supports extra columns & edge cases)
├── data/
│   └── assignment.db             # Local SQLite database (created automatically)
├── output/
│   └── student_scores.png        # Generated bar chart output (created automatically)
├── requirements.txt              # Project third-party dependencies
├── README.md                     # Documentation and run instructions
└── Implementation_Plan.md        # Assignment specification
```

---

## Prerequisites

- **Python**: Version 3.10 or higher
- **Virtual Environment** (recommended): `.venv`

---

## Installation

1. Open a terminal at the project root directory.
2. Activate your virtual environment:

   **PowerShell:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Command Prompt:**
   ```cmd
   .\.venv\Scripts\activate.bat
   ```

   **macOS / Linux:**
   ```bash
   source .venv/bin/activate
   ```

3. Install required third-party packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Tasks

All scripts should be executed from the project root.

### Task 1: Fetch Books from REST API and Store in SQLite
Fetches 20 fiction books from the Open Library Subjects API, saves title, first author, and first publication year into `data/assignment.db` (`books` table), and displays the saved records.

```bash
python task1_books/books_api_to_sqlite.py
```

- **API Endpoint**: `https://openlibrary.org/subjects/fiction.json?limit=20`
- **Duplicate Handling**: Clears existing book rows prior to inserting newly fetched records if the API call succeeds. If the API fails, existing records are safely preserved.
- **Database Table**: `books (id, title, author, publication_year)`

### Task 2: Student Scores, Average Calculation & Bar Chart
Fetches student scores, calculates their arithmetic mean (formatted to 2 decimal places), and saves a styled bar chart with an average reference line to `output/student_scores.png`.

```bash
python task2_scores/student_scores.py
```

- **Configuring Custom API URL**:
  - The script checks the environment variable `STUDENT_SCORES_API_URL`.
  - **PowerShell:**
    ```powershell
    $env:STUDENT_SCORES_API_URL="https://your-api.example.com/students/scores"
    python task2_scores/student_scores.py
    ```
  - **Command Prompt:**
    ```cmd
    set STUDENT_SCORES_API_URL=https://your-api.example.com/students/scores
    python task2_scores/student_scores.py
    ```
- **Fallback Mechanism**:
  If `STUDENT_SCORES_API_URL` is not set, or if the API endpoint cannot be reached or returns invalid data, the script automatically falls back to `task2_scores/sample_scores.json` and clearly displays that sample data is in use.
- **Output Chart**: `output/student_scores.png`

### Task 3: Import Users from CSV into SQLite
Reads user records from `task3_csv_import/users.csv`, validates required fields (`name` and `email`), trims whitespace, gracefully skips incomplete records, dynamically handles optional columns (e.g., `role`, `department`), and inserts records into `data/assignment.db` (`users` table).

```bash
python task3_csv_import/csv_to_sqlite.py
```

- **Duplicate Prevention**: Uses a `UNIQUE` constraint on `email` and `INSERT OR IGNORE` to prevent duplicate emails across multiple executions.
- **Database Table**: `users (id, name, email, role, department)`
- **Summary**: Prints total rows read, users successfully inserted, and rows skipped or ignored.

---

## Database Details

- **Database Location**: `data/assignment.db`
- **Tables**:
  - `books`:
    - `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
    - `title` (TEXT NOT NULL)
    - `author` (TEXT)
    - `publication_year` (INTEGER)
  - `users`:
    - `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
    - `name` (TEXT NOT NULL)
    - `email` (TEXT NOT NULL UNIQUE)
    - `role` (TEXT)
    - `department` (TEXT)

---

## Example Console Output

### Task 1
```text
Fetching books from Open Library API...
Fetched 20 books.
Saved 20 books to SQLite (assignment.db).

Books stored in database:
1. The Hobbit | J.R.R. Tolkien | 1937
2. Pride and Prejudice | Jane Austen | 1813
...
```

### Task 2
```text
Note: No live API URL configured via STUDENT_SCORES_API_URL. Using sample JSON fallback.
Using student score data from: sample data
Number of students: 5
Average score: 86.40
Chart saved to output/student_scores.png
```

### Task 3
```text
Reading user data from users.csv...
Warning: Skipping row #11: name or email is missing/empty ({'name': 'Missing Email User', 'email': '', 'role': 'Intern', 'department': 'Engineering'}).
Warning: Skipping row #12: name or email is missing/empty ({'name': '', 'email': 'missing_name@example.com', 'role': 'Intern', 'department': 'Product'}).

Rows read: 11
Users inserted: 9
Rows skipped or ignored: 3

Users in database:
1. Aarav Sharma | aarav@example.com | Backend Developer | Engineering
2. Diya Patel | diya@example.com | Frontend Developer | Engineering
3. Kabir Das | kabir@example.com | Data Scientist | Analytics
...
```
