"""
Unit tests for SQLAlchemy models.

This module tests the behavior of individual model classes.
"""

import pytest
from datetime import datetime, timedelta

from habit_tracker.core.models import Habit, Completion, Periodicity


@pytest.mark.unit
class TestPeriodicityEnum:
    """Test the Periodicity enum."""
    
    def test_enum_values(self):
        """Test that enum values are correct."""
        assert Periodicity.DAILY.value == "daily"
        assert Periodicity.WEEKLY.value == "weekly"
    
    def test_enum_comparison(self):
        """Test enum comparison."""
        assert Periodicity.DAILY != Periodicity.WEEKLY
        assert Periodicity.DAILY == Periodicity.DAILY


@pytest.mark.unit
class TestHabitModel:
    """Test the Habit model."""
    
    def test_habit_creation(self, test_db):
        """Test creating a Habit model instance."""
        habit = Habit(
            name="Test Habit",
            description="Test Description",
            periodicity=Periodicity.DAILY
        )
        
        assert habit.name == "Test Habit"
        assert habit.description == "Test Description"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.id is None  # Not saved yet
        assert habit.created_at is None  # Not saved yet
    
    def test_habit_str_representation(self, test_db):
        """Test string representation of habit."""
        habit = Habit(
            name="Exercise",
            periodicity=Periodicity.DAILY
        )
        
        assert str(habit) == "Exercise (daily)"
    
    def test_habit_repr_representation(self, test_db):
        """Test repr representation of habit."""
        habit = Habit(
            name="Exercise",
            periodicity=Periodicity.DAILY
        )
        habit.id = 1  # Simulate saved habit
        
        assert "Habit(id=1" in repr(habit)
        assert "name='Exercise'" in repr(habit)
        assert "periodicity='daily'" in repr(habit)
    
    def test_habit_periodicity_helpers(self, test_db):
        """Test periodicity helper methods."""
        daily_habit = Habit(
            name="Daily Habit",
            periodicity=Periodicity.DAILY
        )
        
        weekly_habit = Habit(
            name="Weekly Habit",
            periodicity=Periodicity.WEEKLY
        )
        
        assert daily_habit.is_daily() is True
        assert daily_habit.is_weekly() is False
        
        assert weekly_habit.is_daily() is False
        assert weekly_habit.is_weekly() is True


@pytest.mark.unit
class TestCompletionModel:
    """Test the Completion model."""
    
    def test_completion_creation(self, test_db):
        """Test creating a Completion model instance."""
        now = datetime.now()
        completion = Completion(
            habit_id=1,
            completed_at=now
        )
        
        assert completion.habit_id == 1
        assert completion.completed_at == now
        assert completion.id is None  # Not saved yet
    
    def test_completion_str_representation(self, test_db):
        """Test string representation of completion."""
        now = datetime.now()
        completion = Completion(
            habit_id=1,
            completed_at=now
        )
        
        expected = f"Completed on {now.strftime('%Y-%m-%d %H:%M')}"
        assert str(completion) == expected
    
    def test_completion_repr_representation(self, test_db):
        """Test repr representation of completion."""
        now = datetime.now()
        completion = Completion(
            habit_id=1,
            completed_at=now
        )
        completion.id = 1  # Simulate saved completion
        
        assert "Completion(id=1" in repr(completion)
        assert "habit_id=1" in repr(completion)
    
    def test_completion_date_properties(self, test_db):
        """Test date and time properties."""
        now = datetime.now()
        completion = Completion(
            habit_id=1,
            completed_at=now
        )
        
        assert completion.completion_date == now.date()
        assert completion.completion_time == now.time()
    
    def test_is_today_method(self, test_db):
        """Test the is_today method."""
        today_completion = Completion(
            habit_id=1,
            completed_at=datetime.now()
        )
        
        yesterday_completion = Completion(
            habit_id=1,
            completed_at=datetime.now() - timedelta(days=1)
        )
        
        assert today_completion.is_today() is True
        assert yesterday_completion.is_today() is False
    
    def test_days_ago_method(self, test_db):
        """Test the days_ago method."""
        today_completion = Completion(
            habit_id=1,
            completed_at=datetime.now()
        )
        
        yesterday_completion = Completion(
            habit_id=1,
            completed_at=datetime.now() - timedelta(days=1)
        )
        
        assert today_completion.days_ago() == 0
        assert yesterday_completion.days_ago() == 1
