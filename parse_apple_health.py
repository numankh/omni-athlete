#!/usr/bin/env python3
"""
Parse Apple Health data using apple-health-parser library and store 
workout data (TraditionalStrengthTraining and Running) in SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from apple_health_parser.utils.parser import Parser

def safe_float(s: Optional[str]) -> Optional[float]:
    """Safely convert string to float, returning None if conversion fails."""
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def create_database_schema(db_path: str) -> None:
    """Create SQLite database schema for workouts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create workouts table with additional fields for running data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_activity_type TEXT NOT NULL,
            duration REAL,
            duration_unit TEXT,
            -- Additional fields for running workouts
            heart_rate_avg REAL,
            heart_rate_min REAL,
            heart_rate_max REAL,
            running_distance REAL,
            running_distance_unit TEXT,
            active_energy_burned REAL,
            active_energy_unit TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            creation_date TEXT,
            source_name TEXT,
            source_version TEXT,
            device TEXT
        )
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_workouts_type_start 
        ON workouts(workout_activity_type, start_date)
    """)
    
    conn.commit()
    conn.close()

def parse_and_store_workouts(xml_path: str, db_path: str) -> None:
    """Parse Apple Health XML and store specified workout types in SQLite."""
    
    # Target workout types
    target_workouts = {
        "HKWorkoutActivityTypeTraditionalStrengthTraining",
        "HKWorkoutActivityTypeRunning"
    }
    
    print(f"Parsing Apple Health data from: {xml_path}")
    
    # Parse the Apple Health export using Parser
    parser = Parser(export_file=xml_path, verbose=True)
    
    # Since workouts are stored as XML elements, we need to parse them directly
    # from the XML file using the parser's internal methods
    from xml.etree.ElementTree import iterparse
    
    print("Parsing workouts directly from XML...")
    
    workout_records = []
    processed_count = 0
    
    # Parse XML directly for workout elements
    context = iterparse(parser.xml_file, events=("end",))
    for _, elem in context:
        if elem.tag == "Workout":
            workout_type = elem.attrib.get("workoutActivityType")
            if workout_type in target_workouts:
                workout_data = elem.attrib.copy()
                
                # Extract WorkoutStatistics for running workouts
                if workout_type == "HKWorkoutActivityTypeRunning":
                    # Initialize running-specific fields
                    heart_rate_avg = None
                    heart_rate_min = None
                    heart_rate_max = None
                    running_distance = None
                    running_distance_unit = None
                    active_energy_burned = None
                    active_energy_unit = None
                    
                    # Parse WorkoutStatistics children
                    for child in elem:
                        if child.tag == "WorkoutStatistics":
                            stats_type = child.attrib.get("type")
                            
                            # Handle heart rate data
                            if stats_type == "HKQuantityTypeIdentifierHeartRate":
                                heart_rate_avg = safe_float(child.attrib.get("average"))
                                heart_rate_min = safe_float(child.attrib.get("minimum"))
                                heart_rate_max = safe_float(child.attrib.get("maximum"))
                            
                            # Handle running distance
                            elif stats_type == "HKQuantityTypeIdentifierDistanceWalkingRunning":
                                running_distance = safe_float(child.attrib.get("sum"))
                                running_distance_unit = child.attrib.get("unit")
                            
                            # Handle active energy burned
                            elif stats_type == "HKQuantityTypeIdentifierActiveEnergyBurned":
                                active_energy_burned = safe_float(child.attrib.get("sum"))
                                active_energy_unit = child.attrib.get("unit")
                    
                    # Add extracted data to workout_data
                    workout_data.update({
                        'heart_rate_avg': heart_rate_avg,
                        'heart_rate_min': heart_rate_min,
                        'heart_rate_max': heart_rate_max,
                        'running_distance': running_distance,
                        'running_distance_unit': running_distance_unit,
                        'active_energy_burned': active_energy_burned,
                        'active_energy_unit': active_energy_unit
                    })
                
                workout_records.append(workout_data)
                processed_count += 1
                
                if processed_count <= 10:  # Show first 10 for debugging
                    print(f"Found workout: {workout_type} on {elem.attrib.get('startDate')}")
                    if workout_type == "HKWorkoutActivityTypeRunning":
                        print(f"  - Heart Rate: {workout_data.get('heart_rate_avg')} bpm")
                        print(f"  - Distance: {workout_data.get('running_distance')} {workout_data.get('running_distance_unit')}")
                        print(f"  - Active Energy: {workout_data.get('active_energy_burned')} {workout_data.get('active_energy_unit')}")
            
            elem.clear()
    
    print(f"Total target workout records found: {len(workout_records)}")
    
    # Count by type
    strength_count = sum(1 for w in workout_records 
                         if w.get('workoutActivityType') == "HKWorkoutActivityTypeTraditionalStrengthTraining")
    running_count = sum(1 for w in workout_records 
                       if w.get('workoutActivityType') == "HKWorkoutActivityTypeRunning")
    
    print(f"  - Traditional Strength Training: {strength_count}")
    print(f"  - Running: {running_count}")
    
    if not workout_records:
        print("No target workout records found!")
        return
    
    # Store in database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    workout_insert_sql = """
        INSERT INTO workouts (
            workout_activity_type,
            duration, duration_unit,
            heart_rate_avg, heart_rate_min, heart_rate_max,
            running_distance, running_distance_unit,
            active_energy_burned, active_energy_unit,
            start_date, end_date, creation_date,
            source_name, source_version, device
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    inserted_count = 0
    
    for workout in workout_records:
        # Convert workout dict to database format
        row = (
            workout.get('workoutActivityType'),
            safe_float(workout.get('duration')),
            workout.get('durationUnit'),
            workout.get('heart_rate_avg'),
            workout.get('heart_rate_min'),
            workout.get('heart_rate_max'),
            workout.get('running_distance'),
            workout.get('running_distance_unit'),
            workout.get('active_energy_burned'),
            workout.get('active_energy_unit'),
            workout.get('startDate'),
            workout.get('endDate'),
            workout.get('creationDate'),
            workout.get('sourceName'),
            workout.get('sourceVersion'),
            workout.get('device')
        )
        
        cursor.execute(workout_insert_sql, row)
        inserted_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"Successfully inserted {inserted_count} workouts into database: {db_path}")

def main():
    """Main function to parse Apple Health data."""
    
    # Paths
    zip_path = "/Users/numankhan/Documents/helloworld/apple-health/export.zip"
    db_path = "/Users/numankhan/Documents/helloworld/apple-health/apple_health_workouts.db"
    
    # Verify zip file exists
    if not Path(zip_path).exists():
        print(f"Error: ZIP file not found at {zip_path}")
        return
    
    # Create database schema
    print("Creating database schema...")
    create_database_schema(db_path)
    
    # Parse and store workouts
    parse_and_store_workouts(zip_path, db_path)
    
    print("\nParsing complete!")
    print(f"Database created at: {db_path}")
    print("\nYou can query the data with:")
    print(f"sqlite3 {db_path}")
    print("SELECT * FROM workouts WHERE workout_activity_type = 'HKWorkoutActivityTypeTraditionalStrengthTraining';")
    print("SELECT * FROM workouts WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning';")

if __name__ == "__main__":
    main()
