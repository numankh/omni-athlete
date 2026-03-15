# Apple Health Workout Parser

This project parses Apple Health data and stores workout information (Traditional Strength Training and Running) in a SQLite database using the apple-health-parser library.

## Files Created

- `parse_apple_health.py` - Main script to parse Apple Health export and store workouts
- `query_workouts.py` - Example script to query and analyze the workout database
- `apple_health_workouts.db` - SQLite database containing parsed workout data
- `export.zip` - Compressed Apple Health export file

## Database Schema

The `workouts` table contains:
- `id` - Primary key
- `workout_activity_type` - Type of workout (HKWorkoutActivityTypeTraditionalStrengthTraining or HKWorkoutActivityTypeRunning)
- `duration` - Workout duration in minutes
- `duration_unit` - Duration unit (typically "min")
- `total_distance` - Distance for running workouts (often NULL)
- `total_distance_unit` - Distance unit (typically "mi" or "km")
- `total_energy_burned` - Calories burned (often NULL)
- `total_energy_burned_unit` - Energy unit (typically "kcal")
- **`heart_rate_avg`** - Average heart rate for running workouts (NEW)
- **`heart_rate_min`** - Minimum heart rate for running workouts (NEW)
- **`heart_rate_max`** - Maximum heart rate for running workouts (NEW)
- **`running_distance`** - Detailed running distance from WorkoutStatistics (NEW)
- **`running_distance_unit`** - Unit for running distance (NEW)
- **`active_energy_burned`** - Active energy burned for running workouts (NEW)
- **`active_energy_unit`** - Unit for active energy (NEW)
- `start_date` - Workout start timestamp
- `end_date` - Workout end timestamp
- `creation_date` - Record creation timestamp
- `source_name` - Source device/app name
- `source_version` - Source version
- `device` - Device information

## Parsed Data Summary

- **Total Workouts**: 747
- **Traditional Strength Training**: 465 sessions
- **Running**: 282 sessions
- **Date Range**: September 2022 to February 2026

### Workout Statistics

**Running:**
- Total Runs: 282
- Average Duration: 29.1 minutes
- Average Heart Rate: 147 bpm (91.5% coverage)
- Average Running Distance: 2.89 units (91.8% coverage)
- Average Active Energy Burned: 327 units (99.3% coverage)

**Strength Training:**
- Total Sessions: 465
- Average Duration: 60.4 minutes
- Longest Session: 110.5 minutes
- Calorie data: Not available in this export

### Enhanced Data Extraction

The script now extracts detailed WorkoutStatistics for running workouts:
- **HKQuantityTypeIdentifierHeartRate** - Average, minimum, and maximum heart rate
- **HKQuantityTypeIdentifierDistanceWalkingRunning** - Running distance with units
- **HKQuantityTypeIdentifierActiveEnergyBurned** - Active energy burned with units

## Usage

### Parse Apple Health Data
```bash
# Activate virtual environment
source ../.venv/bin/activate

# Run the parser
python parse_apple_health.py
```

### Query the Database
```bash
# Run the analysis script
python query_workouts.py

# Or use SQLite directly
sqlite3 apple_health_workouts.db
```

### Example SQL Queries
```sql
-- Get all running workouts with heart rate data
SELECT 
    start_date, 
    duration, 
    heart_rate_avg, 
    running_distance, 
    active_energy_burned
FROM workouts 
WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning'
    AND heart_rate_avg IS NOT NULL
ORDER BY start_date DESC;

-- Get running workouts with distance > 3.0
SELECT 
    start_date, 
    running_distance, 
    heart_rate_avg, 
    active_energy_burned
FROM workouts 
WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning'
    AND running_distance > 3.0
ORDER BY running_distance DESC;

-- Get heart rate statistics by year
SELECT 
    substr(start_date, 1, 4) as year,
    COUNT(*) as run_count,
    AVG(heart_rate_avg) as avg_heart_rate,
    AVG(running_distance) as avg_distance
FROM workouts 
WHERE workout_activity_type = 'HKWorkoutActivityTypeRunning'
    AND heart_rate_avg IS NOT NULL
GROUP BY year
ORDER BY year;
```

## Requirements

- Python 3.11+
- apple-health-parser library
- SQLite3

## Notes

- The apple-health-parser library expects a ZIP file containing the Apple Health export
- Workouts are parsed directly from the XML since they're stored as XML elements rather than as separate data types
- **Enhanced data extraction**: Running workouts now include detailed WorkoutStatistics for heart rate, distance, and active energy burned
- The script handles large XML files efficiently using streaming XML parsing
- **Data coverage**: Running workouts have excellent data coverage (91.5%+ for heart rate and distance, 99.3% for active energy)
- Distance and calorie data may not be available for strength training sessions depending on the Apple Health export configuration
