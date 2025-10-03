#!/usr/bin/env python3
"""
Seed script for the Habit Tracking application.

This script populates the database with 5 predefined habits and sample tracking data
to demonstrate the application functionality.
"""

from datetime import datetime, timedelta
import random

import sys
import os

# Add the parent directory to the path to import habit_tracker modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from habit_tracker.core.models import Habit, Completion, Periodicity
from habit_tracker.services.habit_service import HabitService
from habit_tracker.core.database import db_manager
from habit_tracker.fixtures.predefined_habits import (
    PREDEFINED_HABITS, 
    generate_four_weeks_sample_events,
    validate_fixture_data,
    get_expected_statistics
)


def create_sample_habits():
    """Create the 5 predefined sample habits as per requirements."""
    # Validate fixtures first
    validate_fixture_data()
    
    # Use the predefined habits from fixtures
    sample_habits = PREDEFINED_HABITS
    
    created_habits = []
    
    for habit_data in sample_habits:
        try:
            habit = HabitService.create_habit(
                name=habit_data['name'],
                description=habit_data['description'],
                periodicity=habit_data['periodicity']
            )
            created_habits.append(habit)
            print(f"✅ Created habit: {habit_data['name']}")
        except Exception:
            # Habit already exists, get it instead
            habit = HabitService.get_habit_by_name(habit_data['name'])
            created_habits.append(habit)
            print(f"ℹ️  Habit already exists: {habit_data['name']}")
    
    return created_habits


def generate_realistic_completion_data(habits, days_back=None):
    """
    Generate exactly 4 weeks of sample completion data as per requirements.
    
    Args:
        habits: List of created habits (for compatibility)
        days_back: Unused, we generate exactly 4 weeks of data
    """
    print("📅 Generating exactly 4 weeks of sample completion events...")
    
    # Get the predefined 4 weeks of sample events
    completion_events = generate_four_weeks_sample_events()
    
    # Create completions for each habit
    for habit_name, completions_list in completion_events.items():
        print(f"  Creating {len(completions_list)} completions for '{habit_name}'...")
        
        for completion_date in completions_list:
            try:
                HabitService.log_completion(habit_name, completion_date)
            except Exception as e:
                # Skip if already exists or other error
                pass
    
    print(f"✅ Generated completion data for {len(completion_events)} habits")


def print_seed_summary():
    """Print a summary of the seeded data with expected statistics."""
    print("\n" + "="*50)
    print("📊 SEED DATA SUMMARY")
    print("="*50)
    
    habits = HabitService.get_all_habits()
    expected_stats = get_expected_statistics()
    
    for habit in habits:
        completions = HabitService.get_completions_for_habit(habit.id)
        print(f"\n📝 {habit.name} ({habit.periodicity.value})")
        print(f"   Total completions: {len(completions)}")
        
        # Show expected vs actual
        if habit.name in expected_stats:
            expected = expected_stats[habit.name]
            print(f"   Expected completions: {expected['total_completions']}")
            print(f"   Expected completion rate: {expected['completion_rate']:.1f}%")
        
        if completions:
            first_completion = min(comp.completed_at for comp in completions)
            last_completion = max(comp.completed_at for comp in completions)
            print(f"   First completion: {first_completion.strftime('%Y-%m-%d')}")
            print(f"   Last completion: {last_completion.strftime('%Y-%m-%d')}")
        
        # Get current streak
        from habit_tracker.services.analytics_service import calculate_streak, calculate_longest_streak
        current_streak = calculate_streak(completions, habit.periodicity)
        longest_streak = calculate_longest_streak(completions, habit.periodicity)
        
        streak_unit = "days" if habit.periodicity == Periodicity.DAILY else "weeks"
        print(f"   Current streak: {current_streak} {streak_unit}")
        print(f"   Longest streak: {longest_streak} {streak_unit}")
        
        # Show expected streak
        if habit.name in expected_stats:
            expected = expected_stats[habit.name]
            print(f"   Expected longest streak: {expected['expected_longest_streak']} {streak_unit}")


def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    # Initialize database
    db_manager.init_db()
    print("✅ Database initialized")
    
    # Create sample habits
    print("\n📝 Creating sample habits...")
    habits = create_sample_habits()
    
    # Generate exactly 4 weeks of completion data as per requirements
    print("\n📊 Generating exactly 4 weeks of sample completion data...")
    generate_realistic_completion_data(habits)
    
    # Print summary
    print_seed_summary()
    
    print("\n🎉 Seeding completed successfully!")
    print("You can now use the habit tracker CLI:")
    print("  python main.py analyze list-all")
    print("  python main.py analyze summary")


if __name__ == '__main__':
    main()
