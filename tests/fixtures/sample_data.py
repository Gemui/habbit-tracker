"""
Sample data fixtures for testing.

This module contains sample data that can be used across different test modules.
"""

from datetime import datetime, timedelta
from habit_tracker.core.models import Periodicity


# Sample habit data
SAMPLE_HABITS = [
    {
        "name": "Morning Exercise",
        "description": "30 minutes of morning workout",
        "periodicity": Periodicity.DAILY
    },
    {
        "name": "Weekly Review",
        "description": "Review goals and progress weekly",
        "periodicity": Periodicity.WEEKLY
    },
    {
        "name": "Read Books",
        "description": "Read for at least 30 minutes",
        "periodicity": Periodicity.DAILY
    },
    {
        "name": "Clean House",
        "description": "Deep clean the house",
        "periodicity": Periodicity.WEEKLY
    },
    {
        "name": "Meditation",
        "description": "10 minutes of mindfulness meditation",
        "periodicity": Periodicity.DAILY
    }
]


def generate_completion_dates(days_back: int = 30, success_rate: float = 0.7):
    """
    Generate sample completion dates.
    
    Args:
        days_back: Number of days in the past to generate data for
        success_rate: Probability of completion on any given day (0.0 to 1.0)
        
    Returns:
        List of datetime objects representing completion dates
    """
    import random
    
    completion_dates = []
    base_date = datetime.now()
    
    for i in range(days_back):
        if random.random() < success_rate:
            completion_date = base_date - timedelta(days=i)
            completion_dates.append(completion_date)
    
    return sorted(completion_dates)


def create_streak_pattern(consecutive_days: int = 5, start_date: datetime = None):
    """
    Create a perfect streak pattern for testing.
    
    Args:
        consecutive_days: Number of consecutive days to create
        start_date: Starting date for the streak (defaults to today)
        
    Returns:
        List of consecutive completion dates
    """
    if start_date is None:
        start_date = datetime.now()
    
    return [
        start_date - timedelta(days=i) 
        for i in range(consecutive_days)
    ]


# Test scenarios
TEST_SCENARIOS = {
    "perfect_week": {
        "description": "A user who completed habits every day for a week",
        "completion_rate": 1.0,
        "days": 7
    },
    "occasional_user": {
        "description": "A user who completes habits about 50% of the time",
        "completion_rate": 0.5,
        "days": 30
    },
    "inconsistent_user": {
        "description": "A user with sporadic habit completion",
        "completion_rate": 0.3,
        "days": 30
    },
    "new_user": {
        "description": "A new user with minimal data",
        "completion_rate": 0.8,
        "days": 3
    }
}






