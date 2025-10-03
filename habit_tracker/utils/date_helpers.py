"""Date utility functions for the Habit Tracker application."""

from datetime import datetime, timedelta, date
from typing import Tuple


def get_week_start(target_date: datetime) -> datetime:
    """
    Get the start of the week (Monday) for a given date.
    
    Args:
        target_date: The date to find the week start for
        
    Returns:
        The datetime representing the start of the week (Monday at 00:00:00)
    """
    days_since_monday = target_date.weekday()
    week_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return week_start - timedelta(days=days_since_monday)


def get_week_end(target_date: datetime) -> datetime:
    """
    Get the end of the week (Sunday) for a given date.
    
    Args:
        target_date: The date to find the week end for
        
    Returns:
        The datetime representing the end of the week (Sunday at 23:59:59)
    """
    week_start = get_week_start(target_date)
    return week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)


def is_same_week(date1: datetime, date2: datetime) -> bool:
    """
    Check if two dates are in the same week.
    
    Args:
        date1: First date to compare
        date2: Second date to compare
        
    Returns:
        True if both dates are in the same week (Monday to Sunday)
    """
    return get_week_start(date1).date() == get_week_start(date2).date()


def days_between(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate the number of days between two dates.
    
    Args:
        start_date: The earlier date
        end_date: The later date
        
    Returns:
        The number of days between the dates
    """
    return (end_date.date() - start_date.date()).days


def get_date_range(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Generate a list of dates between start and end dates (inclusive).
    
    Args:
        start_date: The start date
        end_date: The end date
        
    Returns:
        A list of datetime objects for each day in the range
    """
    dates = []
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def format_date_for_display(target_date: datetime) -> str:
    """
    Format a date for user-friendly display.
    
    Args:
        target_date: The date to format
        
    Returns:
        A formatted date string
    """
    return target_date.strftime("%Y-%m-%d")


def format_datetime_for_display(target_datetime: datetime) -> str:
    """
    Format a datetime for user-friendly display.
    
    Args:
        target_datetime: The datetime to format
        
    Returns:
        A formatted datetime string
    """
    return target_datetime.strftime("%Y-%m-%d %H:%M")






