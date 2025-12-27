#!/usr/bin/env python3
"""
Show total running miles per month for 2025 only with a chart and trendline.
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import numpy as np


def main():
    repo_root = Path(__file__).resolve().parents[1]
    export_dir = repo_root / "data" / "apple_health_export_unzipped" / "apple_health_export"
    csv_path = export_dir / "export_workouts.csv"
    db_path = "sqlite:///workouts.db"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Load CSV into SQLite
    engine = create_engine(db_path)
    df = pd.read_csv(csv_path)
    df.to_sql("workouts", engine, index=False, if_exists="replace")
    print("Loaded workouts CSV into SQLite.")

    # Query: total running miles per month for 2025
    query = """
    SELECT
        SUBSTR(startDate, 1, 7) AS month,
        SUM(
            CAST(
                REPLACE(REPLACE(TRIM(distanceWalkingRunning), 'mi', ''), ' ', '')
              AS REAL
            )
        ) AS total_miles
    FROM workouts
    WHERE workoutActivityType = 'HKWorkoutActivityTypeRunning'
      AND distanceWalkingRunning IS NOT NULL
      AND startDate LIKE '2025-%'
    GROUP BY month
    ORDER BY month;
    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()

    if not rows:
        print("No running workouts found for 2025.")
        return

    months = [row[0] for row in rows]
    miles = [float(row[1]) for row in rows]

    # Convert month strings to numeric indices for fitting
    x_vals = np.arange(len(months))
    y_vals = np.array(miles)

    # Linear fit
    coeffs = np.polyfit(x_vals, y_vals, 1)
    trendline = np.poly1d(coeffs)
    y_fit = trendline(x_vals)

    plt.figure(figsize=(12, 5))
    plt.plot(months, miles, marker='o', label='Monthly Miles (2025)')
    plt.plot(months, y_fit, '--', color='red', label='Trendline')
    plt.title('Running Miles Per Month (2025)')
    plt.xlabel('Month')
    plt.ylabel('Total Miles')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()


if __name__ == "__main__":
    main()
