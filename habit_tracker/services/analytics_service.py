"""
Analytics module for the Habit Tracking application.

This module provides analytical functions to gain insights into habit data,
including streak calculations and habit statistics. Uses functional programming
principles with pure functions.
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

from ..core.models import Habit, Completion, Periodicity
from .habit_service import HabitService


def calculate_streak(completions: List[Completion], periodicity: Periodicity, 
                    end_date: datetime = None) -> int:
    """
    Calculate the current streak for a habit based on its completions.
    
    Args:
        completions: List of completion records, should be sorted by date desc
        periodicity: Whether the habit is daily or weekly
        end_date: Optional end date for streak calculation. Defaults to today.
        
    Returns:
        The current streak length (number of consecutive periods)
    """
    if not completions:
        return 0
    
    if end_date is None:
        end_date = datetime.now()
    
    # Convert completions to dates for easier calculation
    completion_dates = [comp.completed_at.date() for comp in completions]
    completion_dates.sort(reverse=True)  # Most recent first
    
    streak = 0
    current_date = end_date.date()
    
    if periodicity == Periodicity.DAILY:
        # For daily habits, check consecutive days
        for completion_date in completion_dates:
            if completion_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif completion_date == current_date + timedelta(days=1):
                # Allow for today not being completed yet
                streak += 1
                current_date = completion_date - timedelta(days=1)
            else:
                break
    else:  # WEEKLY
        # For weekly habits, check consecutive weeks
        # Find the start of the current week (Monday)
        days_since_monday = current_date.weekday()
        current_week_start = current_date - timedelta(days=days_since_monday)
        
        for completion_date in completion_dates:
            # Find the start of the completion week
            comp_days_since_monday = completion_date.weekday()
            comp_week_start = completion_date - timedelta(days=comp_days_since_monday)
            
            if comp_week_start == current_week_start:
                streak += 1
                current_week_start -= timedelta(weeks=1)
            elif comp_week_start == current_week_start + timedelta(weeks=1):
                # Allow for current week not being completed yet
                streak += 1
                current_week_start = comp_week_start - timedelta(weeks=1)
            else:
                break
    
    return streak


def calculate_longest_streak(completions: List[Completion], periodicity: Periodicity) -> int:
    """
    Calculate the longest streak ever achieved for a habit.
    
    Args:
        completions: List of completion records
        periodicity: Whether the habit is daily or weekly
        
    Returns:
        The longest streak length achieved
    """
    if not completions:
        return 0
    
    # Convert to dates and sort chronologically
    completion_dates = [comp.completed_at.date() for comp in completions]
    completion_dates = sorted(set(completion_dates))  # Remove duplicates and sort
    
    if not completion_dates:
        return 0
    
    longest_streak = 1
    current_streak = 1
    
    if periodicity == Periodicity.DAILY:
        # Check for consecutive days
        for i in range(1, len(completion_dates)):
            if completion_dates[i] == completion_dates[i-1] + timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
    else:  # WEEKLY
        # Group completions by week and check consecutive weeks
        weeks = set()
        for comp_date in completion_dates:
            # Find the start of the week (Monday)
            days_since_monday = comp_date.weekday()
            week_start = comp_date - timedelta(days=days_since_monday)
            weeks.add(week_start)
        
        weeks = sorted(weeks)
        if not weeks:
            return 0
        
        current_streak = 1
        longest_streak = 1
        
        for i in range(1, len(weeks)):
            if weeks[i] == weeks[i-1] + timedelta(weeks=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
    
    return longest_streak


def get_habit_statistics(habit: Habit) -> Dict[str, any]:
    """
    Get comprehensive statistics for a single habit.
    
    Args:
        habit: The habit to analyze
        
    Returns:
        Dictionary containing various statistics about the habit
    """
    completions = HabitService.get_completions_for_habit(habit.id)
    
    stats = {
        'habit_id': habit.id,
        'habit_name': habit.name,
        'periodicity': habit.periodicity.value,
        'created_at': habit.created_at,
        'total_completions': len(completions),
        'current_streak': calculate_streak(completions, habit.periodicity),
        'longest_streak': calculate_longest_streak(completions, habit.periodicity),
        'first_completion': completions[-1].completed_at if completions else None,
        'last_completion': completions[0].completed_at if completions else None,
    }
    
    # Calculate completion rate if habit has been active for more than 0 days
    if habit.created_at:
        days_since_creation = (datetime.now() - habit.created_at).days + 1
        if habit.periodicity == Periodicity.DAILY:
            expected_completions = days_since_creation
        else:  # WEEKLY
            expected_completions = max(1, (days_since_creation + 6) // 7)  # Round up weeks
        
        completion_rate = (len(completions) / expected_completions) * 100 if expected_completions > 0 else 0
        stats['completion_rate'] = min(100.0, completion_rate)  # Cap at 100%
        stats['expected_completions'] = expected_completions
    
    return stats


def get_all_habits_statistics() -> List[Dict[str, any]]:
    """
    Get statistics for all habits.
    
    Returns:
        List of dictionaries containing statistics for each habit
    """
    habits = HabitService.get_all_habits()
    return [get_habit_statistics(habit) for habit in habits]


def get_habits_by_periodicity_with_stats(periodicity: Periodicity) -> List[Dict[str, any]]:
    """
    Get habits of a specific periodicity with their statistics.
    
    Args:
        periodicity: The periodicity to filter by
        
    Returns:
        List of dictionaries containing habit information and statistics
    """
    habits = HabitService.get_habits_by_periodicity(periodicity)
    return [get_habit_statistics(habit) for habit in habits]


def find_longest_streak_across_all_habits() -> Tuple[Optional[str], int]:
    """
    Find the habit with the longest streak across all habits.
    
    Returns:
        Tuple of (habit_name, longest_streak_length)
        Returns (None, 0) if no habits exist
    """
    habits = HabitService.get_all_habits()
    if not habits:
        return None, 0
    
    max_streak = 0
    best_habit = None
    
    for habit in habits:
        completions = HabitService.get_completions_for_habit(habit.id)
        longest_streak = calculate_longest_streak(completions, habit.periodicity)
        
        if longest_streak > max_streak:
            max_streak = longest_streak
            best_habit = habit.name
    
    return best_habit, max_streak


def get_completion_calendar(habit_name: str, start_date: date = None, 
                          end_date: date = None) -> Dict[str, bool]:
    """
    Get a calendar view of completions for a habit within a date range.
    
    Args:
        habit_name: Name of the habit
        start_date: Start date for the calendar. Defaults to 30 days ago.
        end_date: End date for the calendar. Defaults to today.
        
    Returns:
        Dictionary mapping date strings (YYYY-MM-DD) to completion status
        
    Raises:
        HabitNotFoundError: If the habit doesn't exist
    """
    habit = HabitService.get_habit_by_name(habit_name)
    if not habit:
        from ..core.exceptions import HabitNotFoundError
        raise HabitNotFoundError(f"Habit '{habit_name}' not found")
    
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    completions = HabitService.get_completions_for_habit(habit.id)
    completion_dates = {comp.completed_at.date() for comp in completions}
    
    calendar = {}
    current_date = start_date
    
    while current_date <= end_date:
        if habit.periodicity == Periodicity.DAILY:
            calendar[current_date.isoformat()] = current_date in completion_dates
            current_date += timedelta(days=1)
        else:  # WEEKLY
            # For weekly habits, show the week as completed if any day in that week has a completion
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_completed = any(
                week_start <= comp_date <= week_end 
                for comp_date in completion_dates
            )
            
            calendar[week_start.isoformat()] = week_completed
            current_date = week_end + timedelta(days=1)
    
    return calendar


def get_recent_activity_summary(days: int = 7) -> Dict[str, any]:
    """
    Get a summary of recent habit activity.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Dictionary containing recent activity statistics
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    all_completions = HabitService.get_all_completions()
    recent_completions = [
        comp for comp in all_completions 
        if comp.completed_at >= start_date
    ]
    
    # Group by habit
    completions_by_habit = defaultdict(list)
    for comp in recent_completions:
        completions_by_habit[comp.habit_id].append(comp)
    
    habits = HabitService.get_all_habits()
    
    summary = {
        'period_days': days,
        'total_completions': len(recent_completions),
        'habits_with_activity': len(completions_by_habit),
        'total_habits': len(habits),
        'habit_activity': []
    }
    
    for habit in habits:
        habit_recent_completions = completions_by_habit.get(habit.id, [])
        activity = {
            'habit_name': habit.name,
            'periodicity': habit.periodicity.value,
            'completions_in_period': len(habit_recent_completions),
            'current_streak': calculate_streak(
                HabitService.get_completions_for_habit(habit.id), 
                habit.periodicity
            )
        }
        summary['habit_activity'].append(activity)
    
    return summary
