#!/usr/bin/env python3
"""
Show total sleep hours per month over time with a chart and trendline.
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
    csv_path = export_dir / "export_sleep.csv"
    db_path = "sqlite:///sleep.db"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Load CSV into SQLite
    engine = create_engine(db_path)
    df = pd.read_csv(csv_path)
    df.to_sql("sleep", engine, index=False, if_exists="replace")
    print("Loaded sleep CSV into SQLite.")

    # Query: average sleep hours per night per month (filtered for 2–12 hours)
    query = """
    SELECT
        SUBSTR(startDate, 1, 7) AS month,
        AVG(
            (julianday(endDate) - julianday(startDate)) * 24
        ) AS avg_hours_per_night
    FROM sleep
    WHERE value LIKE '%SleepAnalysis%'
      AND (julianday(endDate) - julianday(startDate)) * 24 BETWEEN 2 AND 12
    GROUP BY month
    ORDER BY month;
    """

    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()

    if not rows:
        print("No sleep records found.")
        return

    months = [row[0] for row in rows]
    hours = [float(row[1]) for row in rows]

    # Convert month strings to numeric indices for fitting
    x_vals = np.arange(len(months))
    y_vals = np.array(hours)

    # Linear fit
    coeffs = np.polyfit(x_vals, y_vals, 1)
    trendline = np.poly1d(coeffs)
    y_fit = trendline(x_vals)

    plt.figure(figsize=(12, 5))
    plt.plot(months, hours, marker='o', label='Avg Hours/Night')
    plt.plot(months, y_fit, '--', color='red', label='Trendline')
    plt.title('Average Sleep Hours Per Night (Monthly)')
    plt.xlabel('Month')
    plt.ylabel('Average Hours')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()


if __name__ == "__main__":
    main()
