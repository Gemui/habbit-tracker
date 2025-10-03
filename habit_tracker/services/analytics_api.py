"""
Analytics API for the Habit Tracker application.

This module defines the pure functional programming API for analytics as requested.
All functions are pure (no side effects) and focus on I/O operations and computations.

Required Functions:
- list_all_habits(): Get all habits
- list_by_periodicity(period): Get habits by periodicity  
- longest_streak_overall(): Find the longest streak across all habits
- longest_streak_for(habit_id): Find the longest streak for a specific habit
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime

from ..core.models import Habit, Completion, Periodicity
from ..core.models.repository import habit_repository, completion_repository
from .analytics_service import calculate_longest_streak


def list_all_habits() -> List[Dict[str, any]]:
    """
    Pure function to list all habits with their basic information.
    
    Returns:
        List of dictionaries containing habit information
        
    Example:
        [
            {
                'id': 1,
                'name': 'Drink Water',
                'description': 'Drink 8 glasses daily',
                'periodicity': 'daily',
                'created_at': '2024-01-01T00:00:00',
                'completion_count': 25
            },
            ...
        ]
    """
    habits = habit_repository.find_all()
    return [habit.to_dict() for habit in habits]


def list_by_periodicity(periodicity: str) -> List[Dict[str, any]]:
    """
    Pure function to list habits filtered by their periodicity.
    
    Args:
        periodicity: Either 'daily' or 'weekly'
        
    Returns:
        List of dictionaries containing habit information for the specified periodicity
        
    Raises:
        ValueError: If periodicity is not 'daily' or 'weekly'
        
    Example:
        list_by_periodicity('daily') returns all daily habits
        list_by_periodicity('weekly') returns all weekly habits
    """
    if periodicity.lower() not in ['daily', 'weekly']:
        raise ValueError("Periodicity must be 'daily' or 'weekly'")
    
    period_enum = Periodicity.DAILY if periodicity.lower() == 'daily' else Periodicity.WEEKLY
    habits = habit_repository.find_by_periodicity(period_enum)
    return [habit.to_dict() for habit in habits]


def longest_streak_overall() -> Tuple[Optional[str], int, str]:
    """
    Pure function to find the habit with the longest streak across all habits.
    
    Returns:
        Tuple of (habit_name, streak_length, periodicity)
        Returns (None, 0, '') if no habits exist
        
    Example:
        ('Drink Water', 15, 'daily') means "Drink Water" has the longest streak of 15 days
        ('Weekly Review', 8, 'weekly') means "Weekly Review" has the longest streak of 8 weeks
    """
    habits = habit_repository.find_all()
    
    if not habits:
        return None, 0, ''
    
    max_streak = 0
    best_habit_name = None
    best_periodicity = ''
    
    for habit in habits:
        completions = completion_repository.find_by_habit_id(habit.id)
        longest_streak = calculate_longest_streak(completions, habit.periodicity)
        
        if longest_streak > max_streak:
            max_streak = longest_streak
            best_habit_name = habit.name
            best_periodicity = habit.periodicity.value
    
    return best_habit_name, max_streak, best_periodicity


def longest_streak_for(habit_id: int) -> Tuple[int, str]:
    """
    Pure function to find the longest streak for a specific habit.
    
    Args:
        habit_id: The ID of the habit to analyze
        
    Returns:
        Tuple of (streak_length, periodicity)
        Returns (0, '') if habit doesn't exist
        
    Example:
        longest_streak_for(1) returns (12, 'daily') for habit ID 1 with 12-day streak
        longest_streak_for(2) returns (5, 'weekly') for habit ID 2 with 5-week streak
    """
    habit = habit_repository.find_by_id(habit_id)
    
    if not habit:
        return 0, ''
    
    completions = completion_repository.find_by_habit_id(habit.id)
    longest_streak = calculate_longest_streak(completions, habit.periodicity)
    
    return longest_streak, habit.periodicity.value


# Additional pure functions for comprehensive analytics API

def get_habit_statistics(habit_id: int) -> Dict[str, any]:
    """
    Pure function to get comprehensive statistics for a specific habit.
    
    Args:
        habit_id: The ID of the habit to analyze
        
    Returns:
        Dictionary containing habit statistics or empty dict if habit doesn't exist
        
    Example:
        {
            'habit_id': 1,
            'habit_name': 'Drink Water',
            'periodicity': 'daily',
            'total_completions': 25,
            'longest_streak': 12,
            'current_streak': 5,
            'created_at': '2024-01-01T00:00:00',
            'first_completion': '2024-01-02T08:00:00',
            'last_completion': '2024-01-25T09:30:00'
        }
    """
    habit = habit_repository.find_by_id(habit_id)
    
    if not habit:
        return {}
    
    completions = completion_repository.find_by_habit_id(habit.id)
    
    from .analytics_service import calculate_streak
    
    stats = {
        'habit_id': habit.id,
        'habit_name': habit.name,
        'periodicity': habit.periodicity.value,
        'total_completions': len(completions),
        'longest_streak': calculate_longest_streak(completions, habit.periodicity),
        'current_streak': calculate_streak(completions, habit.periodicity),
        'created_at': habit.created_at.isoformat() if habit.created_at else None,
        'first_completion': completions[-1].completed_at.isoformat() if completions else None,
        'last_completion': completions[0].completed_at.isoformat() if completions else None
    }
    
    return stats


def get_all_habits_with_streaks() -> List[Dict[str, any]]:
    """
    Pure function to get all habits with their current and longest streaks.
    
    Returns:
        List of dictionaries containing habit information with streak data
        
    Example:
        [
            {
                'id': 1,
                'name': 'Drink Water',
                'periodicity': 'daily',
                'current_streak': 5,
                'longest_streak': 12
            },
            ...
        ]
    """
    habits = habit_repository.find_all()
    result = []
    
    from .analytics_service import calculate_streak
    
    for habit in habits:
        completions = completion_repository.find_by_habit_id(habit.id)
        
        habit_data = {
            'id': habit.id,
            'name': habit.name,
            'periodicity': habit.periodicity.value,
            'current_streak': calculate_streak(completions, habit.periodicity),
            'longest_streak': calculate_longest_streak(completions, habit.periodicity)
        }
        result.append(habit_data)
    
    return result


def count_habits_by_periodicity() -> Dict[str, int]:
    """
    Pure function to count habits by their periodicity.
    
    Returns:
        Dictionary with counts for each periodicity
        
    Example:
        {
            'daily': 3,
            'weekly': 2,
            'total': 5
        }
    """
    habits = habit_repository.find_all()
    
    daily_count = sum(1 for habit in habits if habit.periodicity == Periodicity.DAILY)
    weekly_count = sum(1 for habit in habits if habit.periodicity == Periodicity.WEEKLY)
    
    return {
        'daily': daily_count,
        'weekly': weekly_count,
        'total': len(habits)
    }


def find_habits_with_streak_above(minimum_streak: int, periodicity: str = None) -> List[Dict[str, any]]:
    """
    Pure function to find habits with current streak above a threshold.
    
    Args:
        minimum_streak: Minimum streak length to filter by
        periodicity: Optional filter by 'daily' or 'weekly'
        
    Returns:
        List of habits meeting the criteria
        
    Example:
        find_habits_with_streak_above(7, 'daily') returns daily habits with 7+ day streaks
    """
    habits = habit_repository.find_all()
    
    if periodicity:
        if periodicity.lower() not in ['daily', 'weekly']:
            raise ValueError("Periodicity must be 'daily' or 'weekly'")
        period_enum = Periodicity.DAILY if periodicity.lower() == 'daily' else Periodicity.WEEKLY
        habits = [h for h in habits if h.periodicity == period_enum]
    
    result = []
    from .analytics_service import calculate_streak
    
    for habit in habits:
        completions = completion_repository.find_by_habit_id(habit.id)
        current_streak = calculate_streak(completions, habit.periodicity)
        
        if current_streak >= minimum_streak:
            result.append({
                'id': habit.id,
                'name': habit.name,
                'periodicity': habit.periodicity.value,
                'current_streak': current_streak
            })
    
    return result





