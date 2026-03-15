#!/usr/bin/env python3
"""
Example script to query the Apple Health workout database.
"""

import sqlite3
from datetime import datetime

def query_workout_summary(db_path: str):
    """Get a summary of workouts by type and year."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get workout counts by type and year
    cursor.execute("""
        SELECT 
            workout_activity_type,
            substr(start_date, 1, 4) as year,
            COUNT(*) as count,
            AVG(duration) as avg_duration
        FROM workouts 
        GROUP BY workout_activity_type, substr(start_date, 1, 4)
        ORDER BY year, workout_activity_type
    """)
    
    results = cursor.fetchall()
    
    print("Workout Summary by Type and Year:")
    print("=" * 80)
    print(f"{'Type':<35} {'Year':<6} {'Count':<6} {'Avg Duration':<12}")
    print("-" * 65)
    
    for row in results:
        workout_type = row[0].replace("HKWorkoutActivityType", "")
        year = row[1]
        count = row[2]
        avg_duration = f"{row[3]:.1f} min" if row[3] else "N/A"
        
        print(f"{workout_type:<35} {year:<6} {count:<6} {avg_duration:<12}")
    
    conn.close()

def query_recent_workouts(db_path: str, limit: int = 10):
    """Get the most recent workouts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            workout_activity_type,
            start_date,
            duration,
            heart_rate_avg,
            running_distance,
            active_energy_burned
        FROM workouts 
        ORDER BY start_date DESC 
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    
    print(f"\nRecent {limit} Workouts:")
    print("=" * 70)
    print(f"{'Type':<25} {'Date':<20} {'Duration':<10} {'HR':<8} {'RunDist':<10} {'ActiveE':<10}")
    print("-" * 70)
    
    for row in results:
        workout_type = row[0].replace("HKWorkoutActivityType", "")
        date = row[1][:16]  # Just date and time
        duration = f"{row[2]:.1f} min" if row[2] else "N/A"
        heart_rate = f"{row[3]:.0f}" if row[3] else "N/A"
        run_dist = f"{row[4]:.2f}" if row[4] else "N/A"
        active_energy = f"{row[5]:.0f}" if row[5] else "N/A"
        
        print(f"{workout_type:<25} {date:<20} {duration:<10} {heart_rate:<8} {run_dist:<10} {active_energy:<10}")
    
    conn.close()

def query_running_stats(db_path: str):
    """Get running-specific statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            AVG(duration) as avg_duration,
            AVG(heart_rate_avg) as avg_heart_rate,
            AVG(running_distance) as avg_running_distance,
            AVG(active_energy_burned) as avg_active_energy
        FROM workouts 
        WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning'
    """)
    
    result = cursor.fetchone()
    
    print(f"\nRunning Statistics:")
    print("=" * 50)
    print(f"Total Runs: {result[0]}")
    print(f"Average Duration: {result[1]:.1f} minutes" if result[1] else "Average Duration: N/A")
    print(f"Average Heart Rate: {result[2]:.0f} bpm" if result[2] else "Average Heart Rate: N/A")
    print(f"Average Running Distance: {result[3]:.2f}" if result[3] else "Average Running Distance: N/A")
    print(f"Average Active Energy: {result[4]:.0f}" if result[4] else "Average Active Energy: N/A")
    
    # Show data coverage
    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            COUNT(heart_rate_avg) as with_heart_rate,
            COUNT(running_distance) as with_distance,
            COUNT(active_energy_burned) as with_energy
        FROM workouts 
        WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning'
    """)
    
    coverage = cursor.fetchone()
    print(f"\nData Coverage:")
    print(f"Runs with Heart Rate: {coverage[1]}/{coverage[0]} ({coverage[1]/coverage[0]*100:.1f}%)")
    print(f"Runs with Distance: {coverage[2]}/{coverage[0]} ({coverage[2]/coverage[0]*100:.1f}%)")
    print(f"Runs with Active Energy: {coverage[3]}/{coverage[0]} ({coverage[3]/coverage[0]*100:.1f}%)")
    
    conn.close()

def query_strength_stats(db_path: str):
    """Get strength training-specific statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_sessions,
            AVG(duration) as avg_duration,
            MAX(duration) as longest_session
        FROM workouts 
        WHERE workout_activity_type = 'HKWorkoutActivityTypeTraditionalStrengthTraining'
    """)
    
    result = cursor.fetchone()
    
    print(f"\nStrength Training Statistics:")
    print("=" * 40)
    print(f"Total Sessions: {result[0]}")
    print(f"Average Duration: {result[1]:.1f} minutes" if result[1] else "Average Duration: N/A")
    print(f"Longest Session: {result[2]:.1f} minutes" if result[2] else "Longest Session: N/A")
    
    conn.close()

def main():
    db_path = "apple_health_workouts.db"
    
    print("Apple Health Workout Database Analysis")
    print("=" * 50)
    
    query_workout_summary(db_path)
    query_recent_workouts(db_path)
    query_running_stats(db_path)
    query_strength_stats(db_path)
    
    print(f"\nDatabase: {db_path}")
    print("Total records: 747 workouts (465 strength training, 282 running)")

if __name__ == "__main__":
    main()
