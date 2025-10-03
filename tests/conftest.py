"""
Shared test configuration and fixtures for the Habit Tracker application.

This module contains pytest fixtures that are shared across all test modules.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from habit_tracker.core.models import Habit, Completion, Periodicity
from habit_tracker.core.database import DatabaseManager
from habit_tracker.services.habit_service import HabitService


@pytest.fixture(scope="function")
def test_db():
    """
    Create a temporary test database for each test.
    
    This fixture creates a clean database for each test to ensure isolation.
    """
    # Create a temporary file for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Initialize test database
    test_db_url = f"sqlite:///{temp_db.name}"
    db_manager = DatabaseManager()
    db_manager.init_db(test_db_url)
    
    yield db_manager
    
    # Cleanup
    try:
        os.unlink(temp_db.name)
    except OSError:
        pass  # File might already be deleted


@pytest.fixture
def sample_habits(test_db):
    """
    Create sample habits for testing.
    
    Returns:
        List of created Habit objects
    """
    habits = []
    
    # Create daily habit
    daily_habit = HabitService.create_habit(
        name="Test Daily Habit",
        description="A test daily habit",
        periodicity=Periodicity.DAILY
    )
    habits.append(daily_habit)
    
    # Create weekly habit
    weekly_habit = HabitService.create_habit(
        name="Test Weekly Habit",
        description="A test weekly habit",
        periodicity=Periodicity.WEEKLY
    )
    habits.append(weekly_habit)
    
    return habits


@pytest.fixture
def habit_with_completions(test_db):
    """
    Create a habit with some completion data for testing analytics.
    
    Returns:
        Tuple of (habit, completions_list)
    """
    # Create a test habit
    habit = HabitService.create_habit(
        name="Test Habit with Data",
        description="A habit with completion data",
        periodicity=Periodicity.DAILY
    )
    
    # Add some completions over the past week
    completions = []
    base_date = datetime.now()
    
    for i in range(7):
        completion_date = base_date - timedelta(days=i)
        completion = HabitService.log_completion(habit.name, completion_date)
        completions.append(completion)
    
    return habit, completions


@pytest.fixture
def cli_runner():
    """
    Create a Click test runner for CLI testing.
    
    Returns:
        CliRunner instance
    """
    from click.testing import CliRunner
    return CliRunner()


# Test data fixtures
@pytest.fixture
def sample_habit_data():
    """Sample habit data for testing."""
    return {
        "name": "Exercise",
        "description": "Daily workout routine",
        "periodicity": Periodicity.DAILY
    }


@pytest.fixture
def sample_weekly_habit_data():
    """Sample weekly habit data for testing."""
    return {
        "name": "Weekly Planning",
        "description": "Plan the upcoming week",
        "periodicity": Periodicity.WEEKLY
    }


# Markers for test categories
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "cli: CLI command tests")






