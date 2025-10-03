"""
Unit tests for service layer components.

This module tests business logic in the services layer.
"""

import pytest
from datetime import datetime, timedelta

from habit_tracker.core.models import Periodicity
from habit_tracker.core.exceptions import (
    HabitNotFoundError,
    HabitAlreadyExistsError,
    HabitAlreadyCompletedError
)
from habit_tracker.services.habit_service import HabitService
from habit_tracker.services import analytics_service


@pytest.mark.unit
class TestHabitService:
    """Test the HabitService class."""
    
    def test_create_habit_success(self, test_db):
        """Test successful habit creation."""
        habit = HabitService.create_habit(
            name="Test Habit",
            description="Test Description",
            periodicity=Periodicity.DAILY
        )
        
        assert habit.name == "Test Habit"
        assert habit.description == "Test Description"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.id is not None
        assert habit.created_at is not None
    
    def test_create_habit_duplicate_name(self, test_db):
        """Test that creating a habit with duplicate name fails."""
        # Create first habit
        HabitService.create_habit("Duplicate Name", periodicity=Periodicity.DAILY)
        
        # Try to create another with same name
        with pytest.raises(HabitAlreadyExistsError):
            HabitService.create_habit("Duplicate Name", periodicity=Periodicity.DAILY)
    
    def test_get_all_habits_empty(self, test_db):
        """Test getting all habits when none exist."""
        habits = HabitService.get_all_habits()
        assert habits == []
    
    def test_get_all_habits_with_data(self, sample_habits):
        """Test getting all habits when some exist."""
        habits = HabitService.get_all_habits()
        assert len(habits) == 2
        assert any(h.name == "Test Daily Habit" for h in habits)
        assert any(h.name == "Test Weekly Habit" for h in habits)
    
    def test_get_habits_by_periodicity(self, sample_habits):
        """Test filtering habits by periodicity."""
        daily_habits = HabitService.get_habits_by_periodicity(Periodicity.DAILY)
        weekly_habits = HabitService.get_habits_by_periodicity(Periodicity.WEEKLY)
        
        assert len(daily_habits) == 1
        assert len(weekly_habits) == 1
        assert daily_habits[0].name == "Test Daily Habit"
        assert weekly_habits[0].name == "Test Weekly Habit"
    
    def test_get_habit_by_name_exists(self, sample_habits):
        """Test getting a habit by name when it exists."""
        habit = HabitService.get_habit_by_name("Test Daily Habit")
        assert habit is not None
        assert habit.name == "Test Daily Habit"
    
    def test_get_habit_by_name_not_exists(self, test_db):
        """Test getting a habit by name when it doesn't exist."""
        habit = HabitService.get_habit_by_name("Non-existent Habit")
        assert habit is None
    
    def test_delete_habit_success(self, sample_habits):
        """Test successful habit deletion."""
        result = HabitService.delete_habit("Test Daily Habit")
        assert result is True
        
        # Verify habit is gone
        habit = HabitService.get_habit_by_name("Test Daily Habit")
        assert habit is None
    
    def test_delete_habit_not_found(self, test_db):
        """Test deleting a non-existent habit."""
        with pytest.raises(HabitNotFoundError):
            HabitService.delete_habit("Non-existent Habit")
    
    def test_log_completion_success(self, sample_habits):
        """Test successful completion logging."""
        completion = HabitService.log_completion("Test Daily Habit")
        
        assert completion.habit_id == sample_habits[0].id
        assert completion.completed_at is not None
    
    def test_log_completion_habit_not_found(self, test_db):
        """Test logging completion for non-existent habit."""
        with pytest.raises(HabitNotFoundError):
            HabitService.log_completion("Non-existent Habit")
    
    def test_log_completion_duplicate_daily(self, sample_habits):
        """Test that completing the same daily habit twice in one day fails."""
        completion_date = datetime.now()
        
        # First completion should succeed
        HabitService.log_completion("Test Daily Habit", completion_date)
        
        # Second completion on same day should fail
        with pytest.raises(HabitAlreadyCompletedError):
            HabitService.log_completion("Test Daily Habit", completion_date)
    
    def test_log_completion_duplicate_weekly(self, sample_habits):
        """Test that completing the same weekly habit twice in one week fails."""
        completion_date = datetime.now()
        
        # First completion should succeed
        HabitService.log_completion("Test Weekly Habit", completion_date)
        
        # Second completion in same week should fail
        with pytest.raises(HabitAlreadyCompletedError):
            HabitService.log_completion("Test Weekly Habit", completion_date)


@pytest.mark.unit
class TestAnalyticsService:
    """Test the analytics service functions."""
    
    def test_calculate_streak_empty(self, test_db):
        """Test streak calculation with no completions."""
        streak = analytics_service.calculate_streak([], Periodicity.DAILY)
        assert streak == 0
    
    def test_calculate_longest_streak_empty(self, test_db):
        """Test longest streak calculation with no completions."""
        longest = analytics_service.calculate_longest_streak([], Periodicity.DAILY)
        assert longest == 0
    
    def test_get_habit_statistics(self, habit_with_completions):
        """Test getting comprehensive habit statistics."""
        habit, completions = habit_with_completions
        
        stats = analytics_service.get_habit_statistics(habit)
        
        assert stats['habit_id'] == habit.id
        assert stats['habit_name'] == habit.name
        assert stats['periodicity'] == habit.periodicity.value
        assert stats['total_completions'] == 7
        assert stats['current_streak'] > 0
        assert stats['longest_streak'] > 0
        assert 'completion_rate' in stats
    
    def test_find_longest_streak_no_habits(self, test_db):
        """Test finding longest streak when no habits exist."""
        best_habit, max_streak = analytics_service.find_longest_streak_across_all_habits()
        
        assert best_habit is None
        assert max_streak == 0
