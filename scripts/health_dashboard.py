#!/usr/bin/env python3
"""
Apple Health Dashboard
Loads CSVs directly and plots:
  - Running miles per month (all time)
  - Running miles per month (2025 only)
  - Average sleep hours per night (filtered 2–12 hours)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_with_trendline(df, x_col, y_col, title, xlabel, ylabel):
    x_vals = np.arange(len(df))
    y_vals = df[y_col].values
    coeffs = np.polyfit(x_vals, y_vals, 1)
    trendline = np.poly1d(coeffs)
    y_fit = trendline(x_vals)

    plt.figure(figsize=(12, 5))
    plt.plot(df[x_col], y_vals, marker='o', label=ylabel)
    plt.plot(df[x_col], y_fit, '--', color='red', label='Trendline')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()


def main():
    repo_root = Path(__file__).resolve().parents[1]
    export_dir = repo_root / "data" / "apple_health_export_unzipped" / "apple_health_export"
    workouts_csv = export_dir / "export_workouts.csv"
    sleep_csv = export_dir / "export_sleep.csv"

    if not workouts_csv.exists() or not sleep_csv.exists():
        print("CSV files not found. Make sure export_workouts.csv and export_sleep.csv exist under:")
        print(export_dir)
        sys.exit(1)

    # Load data
    workouts_df = pd.read_csv(workouts_csv)
    sleep_df = pd.read_csv(sleep_csv)
    print(f"Loaded {len(workouts_df)} workout rows and {len(sleep_df)} sleep rows.")

    # --- Running miles per month (all time) ---
    running = workouts_df[
        (workouts_df["workoutActivityType"] == "HKWorkoutActivityTypeRunning") &
        workouts_df["distanceWalkingRunning"].notna()
    ].copy()
    running["distance_miles"] = running["distanceWalkingRunning"].astype(str).str.replace("mi", "").str.replace(" ", "").astype(float)
    running["month"] = running["startDate"].str[:7]
    monthly_miles = running.groupby("month")["distance_miles"].sum().reset_index().sort_values("month")
    plot_with_trendline(monthly_miles, "month", "distance_miles",
                        "Running Miles Per Month (All Time)", "Month", "Total Miles")

    # --- Running miles per month (2025 only) ---
    running_2025 = running[running["month"].str.startswith("2025")].copy()
    monthly_miles_2025 = running_2025.groupby("month")["distance_miles"].sum().reset_index().sort_values("month")
    plot_with_trendline(monthly_miles_2025, "month", "distance_miles",
                        "Running Miles Per Month (2025)", "Month", "Total Miles")

    # --- Average sleep hours per night (filtered 2–12 hours) ---
    sleep_filtered = sleep_df[sleep_df["value"].str.contains("SleepAnalysis", na=False)].copy()
    sleep_filtered["startDate"] = pd.to_datetime(sleep_filtered["startDate"])
    sleep_filtered["endDate"] = pd.to_datetime(sleep_filtered["endDate"])
    sleep_filtered["duration_hours"] = (sleep_filtered["endDate"] - sleep_filtered["startDate"]).dt.total_seconds() / 3600
    sleep_clean = sleep_filtered[(sleep_filtered["duration_hours"] >= 2) & (sleep_filtered["duration_hours"] <= 12)].copy()
    sleep_clean["month"] = sleep_clean["startDate"].dt.strftime("%Y-%m")
    monthly_sleep = sleep_clean.groupby("month")["duration_hours"].mean().reset_index().sort_values("month")
    plot_with_trendline(monthly_sleep, "month", "duration_hours",
                        "Average Sleep Hours Per Night (Monthly)", "Month", "Average Hours")

    # --- Average sleep hours per night (2025 only) ---
    sleep_2025 = sleep_clean[sleep_clean["month"].str.startswith("2025")].copy()
    monthly_sleep_2025 = sleep_2025.groupby("month")["duration_hours"].mean().reset_index().sort_values("month")
    plot_with_trendline(monthly_sleep_2025, "month", "duration_hours",
                        "Average Sleep Hours Per Night (2025)", "Month", "Average Hours")


if __name__ == "__main__":
    main()
