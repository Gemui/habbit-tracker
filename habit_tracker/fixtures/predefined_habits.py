"""
Predefined habits fixtures for the Habit Tracker application.

This module contains exactly 5 predefined habits (≥1 daily, ≥1 weekly) 
and 4 weeks of sample completion events as requested in the feedback.

These fixtures are committed and will be reused for testing and demos.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Import Periodicity directly from enums
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from habit_tracker.core.models.enums import Periodicity


# Habit name constants to avoid duplication
HABIT_DRINK_WATER = 'Drink Water'
HABIT_READ_BOOKS = 'Read Books'
HABIT_EXERCISE = 'Exercise'
HABIT_WEEKLY_PLANNING = 'Weekly Planning'
HABIT_DEEP_CLEAN = 'Deep Clean'

# Exactly 5 predefined habits as requested
PREDEFINED_HABITS = [
    # Daily habits (3 habits - more than the minimum of 1)
    {
        'name': HABIT_DRINK_WATER,
        'description': 'Drink at least 8 glasses of water daily for proper hydration',
        'periodicity': Periodicity.DAILY
    },
    {
        'name': HABIT_READ_BOOKS,
        'description': 'Read for at least 30 minutes to expand knowledge and vocabulary',
        'periodicity': Periodicity.DAILY
    },
    {
        'name': HABIT_EXERCISE,
        'description': 'Do 30 minutes of physical exercise to maintain fitness',
        'periodicity': Periodicity.DAILY
    },
    
    # Weekly habits (2 habits - more than the minimum of 1)
    {
        'name': HABIT_WEEKLY_PLANNING,
        'description': 'Review and plan goals for the upcoming week',
        'periodicity': Periodicity.WEEKLY
    },
    {
        'name': HABIT_DEEP_CLEAN,
        'description': 'Thoroughly clean and organize living space',
        'periodicity': Periodicity.WEEKLY
    }
]


def generate_four_weeks_sample_events() -> Dict[str, List[datetime]]:
    """
    Generate exactly 4 weeks of sample completion events for all predefined habits.
    
    This creates realistic completion patterns that will be reused for testing and demos.
    The patterns are designed to show various streak lengths and completion rates.
    
    Returns:
        Dictionary mapping habit names to lists of completion datetimes
    """
    # Calculate the date range for exactly 4 weeks (28 days)
    end_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=27)  # 28 days total (0-27)
    
    # Define realistic completion patterns for each habit
    completion_events = {}
    
    # HABIT_DRINK_WATER - Very consistent daily habit (90% completion rate)
    # Pattern: Only misses 2-3 days over 4 weeks
    water_completions = []
    missed_days = {5, 13, 22}  # Miss days 5, 13, and 22
    
    for day in range(28):
        if day not in missed_days:
            completion_time = start_date + timedelta(days=day)
            # Vary the time of completion (morning routine)
            completion_time = completion_time.replace(
                hour=8, 
                minute=30 + (day % 30),  # Slight time variation
                second=0
            )
            water_completions.append(completion_time)
    
    completion_events[HABIT_DRINK_WATER] = water_completions
    
    # HABIT_READ_BOOKS - Good daily habit with some breaks (75% completion rate)
    # Pattern: Takes weekends off occasionally, misses 7 days total
    reading_completions = []
    missed_days = {6, 7, 12, 15, 19, 20, 21}  # Miss 7 days
    
    for day in range(28):
        if day not in missed_days:
            completion_time = start_date + timedelta(days=day)
            # Evening reading time
            completion_time = completion_time.replace(
                hour=20,
                minute=15 + (day % 45),
                second=0
            )
            reading_completions.append(completion_time)
    
    completion_events[HABIT_READ_BOOKS] = reading_completions
    
    # HABIT_EXERCISE - Moderate daily habit (65% completion rate)
    # Pattern: More inconsistent, misses about 1/3 of days
    exercise_completions = []
    missed_days = {1, 3, 6, 8, 11, 14, 16, 18, 20, 24, 26}  # Miss 11 days
    
    for day in range(28):
        if day not in missed_days:
            completion_time = start_date + timedelta(days=day)
            # Morning or evening exercise
            hour = 7 if day % 2 == 0 else 18  # Alternate morning/evening
            completion_time = completion_time.replace(
                hour=hour,
                minute=0 + (day % 20),
                second=0
            )
            exercise_completions.append(completion_time)
    
    completion_events[HABIT_EXERCISE] = exercise_completions
    
    # HABIT_WEEKLY_PLANNING - Very consistent weekly habit
    # Pattern: Completes 3 out of 4 weeks (75% completion rate)
    planning_completions = []
    
    # Complete in weeks 1, 2, and 4 (miss week 3)
    completed_weeks = [0, 1, 3]  # Week indices
    
    for week in completed_weeks:
        # Complete on Sunday of each week (day 6 of the week)
        week_start = start_date + timedelta(weeks=week)
        # Find the Sunday of this week (adjust for start_date's day of week)
        days_to_sunday = (6 - week_start.weekday()) % 7
        completion_time = week_start + timedelta(days=days_to_sunday)
        completion_time = completion_time.replace(
            hour=10,
            minute=0,
            second=0
        )
        planning_completions.append(completion_time)
    
    completion_events[HABIT_WEEKLY_PLANNING] = planning_completions
    
    # HABIT_DEEP_CLEAN - Consistent weekly habit
    # Pattern: Completes all 4 weeks (100% completion rate)
    cleaning_completions = []
    
    for week in range(4):
        # Complete on Saturday of each week
        week_start = start_date + timedelta(weeks=week)
        # Find the Saturday of this week
        days_to_saturday = (5 - week_start.weekday()) % 7
        completion_time = week_start + timedelta(days=days_to_saturday)
        completion_time = completion_time.replace(
            hour=14,  # Afternoon cleaning
            minute=30,
            second=0
        )
        cleaning_completions.append(completion_time)
    
    completion_events[HABIT_DEEP_CLEAN] = cleaning_completions
    
    return completion_events


def get_expected_statistics() -> Dict[str, Dict[str, any]]:
    """
    Get the expected statistics for the predefined habits with 4 weeks of data.
    
    This is useful for validation and testing to ensure the fixtures are correct.
    
    Returns:
        Dictionary with expected statistics for each habit
    """
    return {
        HABIT_DRINK_WATER: {
            'total_completions': 25,  # 28 - 3 missed days
            'completion_rate': 89.3,  # 25/28 * 100
            'expected_longest_streak': 12,  # Days 0-4, 6-12 (longest consecutive)
            'periodicity': 'daily'
        },
        HABIT_READ_BOOKS: {
            'total_completions': 21,  # 28 - 7 missed days
            'completion_rate': 75.0,  # 21/28 * 100
            'expected_longest_streak': 5,   # Longest consecutive period
            'periodicity': 'daily'
        },
        HABIT_EXERCISE: {
            'total_completions': 17,  # 28 - 11 missed days
            'completion_rate': 60.7,  # 17/28 * 100
            'expected_longest_streak': 3,   # Shorter streaks due to inconsistency
            'periodicity': 'daily'
        },
        HABIT_WEEKLY_PLANNING: {
            'total_completions': 3,   # 3 out of 4 weeks
            'completion_rate': 75.0,  # 3/4 * 100
            'expected_longest_streak': 2,   # Weeks 1-2 consecutive
            'periodicity': 'weekly'
        },
        HABIT_DEEP_CLEAN: {
            'total_completions': 4,   # All 4 weeks
            'completion_rate': 100.0, # 4/4 * 100
            'expected_longest_streak': 4,   # All weeks consecutive
            'periodicity': 'weekly'
        }
    }


def validate_fixture_data() -> bool:
    """
    Validate that the fixture data meets the requirements.
    
    Returns:
        True if all requirements are met
        
    Raises:
        AssertionError: If any requirement is not met
    """
    # Check exactly 5 habits
    assert len(PREDEFINED_HABITS) == 5, f"Expected 5 habits, got {len(PREDEFINED_HABITS)}"
    
    # Check at least 1 daily and 1 weekly
    daily_count = sum(1 for h in PREDEFINED_HABITS if h['periodicity'] == Periodicity.DAILY)
    weekly_count = sum(1 for h in PREDEFINED_HABITS if h['periodicity'] == Periodicity.WEEKLY)
    
    assert daily_count >= 1, f"Expected at least 1 daily habit, got {daily_count}"
    assert weekly_count >= 1, f"Expected at least 1 weekly habit, got {weekly_count}"
    
    # Check all habits have required fields
    required_fields = ['name', 'description', 'periodicity']
    for habit in PREDEFINED_HABITS:
        for field in required_fields:
            assert field in habit, f"Habit missing required field: {field}"
        assert isinstance(habit['name'], str) and habit['name'], "Habit name must be non-empty string"
        assert isinstance(habit['description'], str) and habit['description'], "Habit description must be non-empty string"
        assert habit['periodicity'] in [Periodicity.DAILY, Periodicity.WEEKLY], "Invalid periodicity"
    
    # Check 4 weeks of sample events
    events = generate_four_weeks_sample_events()
    
    # Check events exist for all habits
    habit_names = [h['name'] for h in PREDEFINED_HABITS]
    for name in habit_names:
        assert name in events, f"Missing events for habit: {name}"
    
    # Check date ranges (4 weeks = 28 days)
    # Use the same end_date as in the fixture generation
    end_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=27)
    
    # Make the start_date more lenient (start of the start day)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    # Make the end_date more lenient (end of the end day)
    extended_end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    for habit_name, completions in events.items():
        for completion in completions:
            assert start_date <= completion <= extended_end_date, f"Completion outside 4-week range for {habit_name}: {completion} not between {start_date} and {extended_end_date}"
    
    print("✅ All fixture requirements validated successfully")
    return True


# Example usage and testing
if __name__ == "__main__":
    # Validate the fixtures
    validate_fixture_data()
    
    # Print summary
    print("\n📊 PREDEFINED HABITS SUMMARY")
    print("=" * 50)
    print(f"Total habits: {len(PREDEFINED_HABITS)}")
    
    daily_habits = [h for h in PREDEFINED_HABITS if h['periodicity'] == Periodicity.DAILY]
    weekly_habits = [h for h in PREDEFINED_HABITS if h['periodicity'] == Periodicity.WEEKLY]
    
    print(f"Daily habits: {len(daily_habits)}")
    for habit in daily_habits:
        print(f"  - {habit['name']}")
    
    print(f"Weekly habits: {len(weekly_habits)}")
    for habit in weekly_habits:
        print(f"  - {habit['name']}")
    
    print("\n📅 SAMPLE EVENTS SUMMARY (4 weeks)")
    events = generate_four_weeks_sample_events()
    expected_stats = get_expected_statistics()
    
    for habit_name, completions in events.items():
        stats = expected_stats[habit_name]
        print(f"\n{habit_name} ({stats['periodicity']}):")
        print(f"  Completions: {len(completions)}")
        print(f"  Expected completion rate: {stats['completion_rate']:.1f}%")
        print(f"  Expected longest streak: {stats['expected_longest_streak']}")
        if completions:
            print(f"  Date range: {min(completions).date()} to {max(completions).date()}")
