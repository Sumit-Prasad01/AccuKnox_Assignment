"""
Task 2: Fetch student scores, calculate the average, and create a bar chart.
"""

import json
import os
import statistics
import sys
from pathlib import Path

# Use non-interactive backend for matplotlib before importing pyplot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_IMAGE_PATH = OUTPUT_DIR / "student_scores.png"
SAMPLE_SCORES_PATH = Path(__file__).resolve().parent / "sample_scores.json"

DEFAULT_API_URL = "https://your-api.example.com/students/scores"
REQUEST_TIMEOUT_SECONDS = 10


def load_sample_scores(sample_path):
    """Load fallback student score data from local JSON file."""
    if not sample_path.exists():
        print(f"Error: Sample data file not found at {sample_path}", file=sys.stderr)
        return []

    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("students", [])
    except (json.JSONDecodeError, OSError) as err:
        print(f"Error: Failed to read sample scores file: {err}", file=sys.stderr)
        return []


def fetch_scores():
    """
    Fetch student scores from configured API endpoint, or fall back to sample JSON file.
    Returns tuple of (students_data, source_description).
    """
    api_url = os.getenv("STUDENT_SCORES_API_URL", "").strip()

    # If an actual API URL is provided and not the default placeholder
    if api_url and api_url != DEFAULT_API_URL:
        try:
            print(f"Attempting to fetch scores from configured API: {api_url}")
            response = requests.get(api_url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()
            students = data.get("students")
            if isinstance(students, list) and students:
                return students, "API"
            print("Warning: API response did not contain a valid 'students' list. Falling back to sample data.")
        except requests.exceptions.RequestException as err:
            print(f"Warning: Failed to reach API ({err}). Falling back to sample data.")
        except ValueError as err:
            print(f"Warning: Failed to parse API response as JSON ({err}). Falling back to sample data.")
    else:
        print("Note: No live API URL configured via STUDENT_SCORES_API_URL. Using sample JSON fallback.")

    students = load_sample_scores(SAMPLE_SCORES_PATH)
    return students, "sample data"


def validate_students(students_raw):
    """
    Validate and clean student records.
    Filters out records with missing names or non-numeric scores.
    Returns list of tuples: (name, float_score).
    """
    valid_students = []
    for idx, item in enumerate(students_raw, start=1):
        if not isinstance(item, dict):
            print(f"Warning: Skipping record #{idx}: expected JSON object, got {type(item).__name__}.")
            continue

        name = item.get("name")
        score_val = item.get("score")

        if not name or not str(name).strip():
            print(f"Warning: Skipping record #{idx}: student name is missing or empty.")
            continue

        try:
            numeric_score = float(score_val)
        except (ValueError, TypeError):
            print(f"Warning: Skipping record #{idx} ('{name}'): invalid non-numeric score '{score_val}'.")
            continue

        valid_students.append((str(name).strip(), numeric_score))

    return valid_students


def calculate_average(students):
    """Calculate the arithmetic mean of student scores."""
    if not students:
        raise ValueError("Cannot calculate average: student list is empty.")
    scores = [score for _, score in students]
    return statistics.mean(scores)


def create_chart(students, average, output_path):
    """
    Generate and save a bar chart showing student scores and average reference line.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    names = [name for name, _ in students]
    scores = [score for _, score in students]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, scores, color="#2563EB", edgecolor="#1D4ED8", alpha=0.85, width=0.55)

    # Reference line for average score
    ax.axhline(
        y=average,
        color="#DC2626",
        linestyle="--",
        linewidth=1.8,
        label=f"Average Score ({average:.2f})"
    )

    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_title("Student Test Scores", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Student Name", fontsize=11, labelpad=10)
    ax.set_ylabel("Test Score", fontsize=11, labelpad=10)
    ax.set_ylim(0, max(max(scores) * 1.15, 100))
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    # Adjust layout and rotate labels if needed
    plt.xticks(rotation=20 if len(names) > 5 else 0, ha="right" if len(names) > 5 else "center")
    plt.tight_layout()

    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    """Run the complete score fetching, calculation, and visualization workflow."""
    raw_students, source = fetch_scores()
    valid_students = validate_students(raw_students)

    if not valid_students:
        print("Error: No valid student score records available.", file=sys.stderr)
        sys.exit(1)

    average = calculate_average(valid_students)

    print(f"Using student score data from: {source}")
    print(f"Number of students: {len(valid_students)}")
    print(f"Average score: {average:.2f}")

    create_chart(valid_students, average, OUTPUT_IMAGE_PATH)
    print(f"Chart saved to {OUTPUT_IMAGE_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
