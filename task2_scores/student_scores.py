import matplotlib.pyplot as plt
import requests
from pathlib import Path


# Base directory and database path
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def fetch_student_scores(api_url: str) -> list[dict]:
    """Fetch user records from a public REST API and transform them into student scores."""
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    payload = response.json()

    users = payload.get("users", [])
    if not users:
        raise ValueError("No user records returned from the public API.")

    # Extract student names and derive a 0–100 test score from existing numeric fields
    records = []
    for user in users:
        full_name = f"{user['firstName']} {user['lastName'][0]}."
        # Deterministic score calculation from API numeric attributes (height/weight)
        raw_score = (float(user["height"]) * 0.4) + (float(user["weight"]) * 0.2)
        normalized_score = round(min(100.0, max(40.0, raw_score)), 1)
        records.append({"name": full_name, "score": normalized_score})

    return records


def calculate_average_and_plot(
    records: list[dict], output_path: str = f"{OUTPUT_DIR}/student_scores.png"
) -> float:
    """Compute the mean test score and generate an annotated bar chart."""
    names = [r["name"] for r in records]
    scores = [r["score"] for r in records]
    avg_score = sum(scores) / len(scores)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(names, scores, color="#2563eb", edgecolor="#1e40af", width=0.55)

    # Plot average reference line
    ax.axhline(
        avg_score,
        color="#dc2626",
        linestyle="--",
        linewidth=1.5,
        label=f"Average Score: {avg_score:.2f}",
    )

    # Label each bar with its exact score
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("Student Test Scores Overview", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Student", fontsize=11)
    ax.set_ylabel("Score (0–100)", fontsize=11)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.show()

    return avg_score


if __name__ == "__main__":
    # Public, zero-authentication REST API endpoint
    PUBLIC_API_URL = "https://dummyjson.com/users?limit=10"

    student_records = fetch_student_scores(PUBLIC_API_URL)
    average = calculate_average_and_plot(student_records)
    print(f"Fetched {len(student_records)} students | Average Score: {average:.2f}")