#!/usr/bin/env python3
"""
Standalone script to run a specific query against the workouts table.
"""

import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text


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

    # Query: count running workouts > 3.1 miles in November
    query = """
    SELECT COUNT(*) AS num_runs_over_3_1_miles_november
    FROM workouts
    WHERE workoutActivityType = 'HKWorkoutActivityTypeRunning'
      AND startDate LIKE '%-11-%'
      AND distanceWalkingRunning IS NOT NULL
      AND CAST(
            REPLACE(REPLACE(TRIM(distanceWalkingRunning), 'mi', ''), ' ', '')
          AS REAL
      ) > 3.1;
    """

    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
        count = result[0] if result else 0

    print(f"Number of running workouts > 3.1 miles: {count}")


if __name__ == "__main__":
    main()
