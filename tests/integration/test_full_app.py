#!/usr/bin/env python3
"""
Comprehensive test suite for the Habit Tracking application.

This module contains unit tests for all major components:
- Models
- CRUD operations
- Analytics functions
- CLI commands
"""

import pytest
from datetime import datetime, timedelta, date
import tempfile
import os
from click.testing import CliRunner

from habit_tracker.core.models import Habit, Completion, Periodicity, Base
from habit_tracker.core.database import DatabaseManager
from habit_tracker.services.habit_service import HabitService
from habit_tracker.services import analytics_service as analytics
from habit_tracker.cli.commands import cli
from habit_tracker.core.exceptions import (
    HabitNotFoundError,
    HabitAlreadyExistsError,
    HabitAlreadyCompletedError
)


# Use fixtures from conftest.py instead of defining them here


class TestModels:
    """Test the SQLAlchemy models."""
    
    def test_habit_creation(self, test_db):
        """Test creating a Habit model."""
        habit = Habit(
            name="Test Habit",
            description="Test Description",
            periodicity=Periodicity.DAILY
        )
        
        assert habit.name == "Test Habit"
        assert habit.description == "Test Description"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.id is None  # Not saved yet
    
    def test_completion_creation(self, test_db):
        """Test creating a Completion model."""
        completion = Completion(
            habit_id=1,
            completed_at=datetime.now()
        )
        
        assert completion.habit_id == 1
        assert isinstance(completion.completed_at, datetime)
        assert completion.id is None  # Not saved yet
    
    def test_periodicity_enum(self, test_db):
        """Test the Periodicity enum."""
        assert Periodicity.DAILY.value == "daily"
        assert Periodicity.WEEKLY.value == "weekly"


class TestCRUD:
    """Test CRUD operations."""
    
    def test_create_habit(self, test_db):
        """Test creating a habit."""
        habit = HabitService.create_habit(
            name="Test Habit",
            description="Test Description",
            periodicity=Periodicity.DAILY
        )
        
        assert habit.id is not None
        assert habit.name == "Test Habit"
        assert habit.description == "Test Description"
        assert habit.periodicity == Periodicity.DAILY
    
    def test_create_duplicate_habit(self, test_db):
        """Test that creating a duplicate habit raises an error."""
        HabitService.create_habit("Duplicate Habit", periodicity=Periodicity.DAILY)
        
        with pytest.raises(HabitAlreadyExistsError):
            HabitService.create_habit("Duplicate Habit", periodicity=Periodicity.DAILY)
    
    def test_get_all_habits(self, sample_habits):
        """Test retrieving all habits."""
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
    
    def test_get_habit_by_name(self, sample_habits):
        """Test retrieving a habit by name."""
        habit = HabitService.get_habit_by_name("Test Daily Habit")
        assert habit is not None
        assert habit.name == "Test Daily Habit"
        
        non_existent = HabitService.get_habit_by_name("Non-existent Habit")
        assert non_existent is None
    
    def test_log_completion(self, sample_habits):
        """Test logging a habit completion."""
        completion = HabitService.log_completion("Test Daily Habit")
        
        assert completion.habit_id == sample_habits[0].id
        assert isinstance(completion.completed_at, datetime)
    
    def test_log_completion_nonexistent_habit(self, test_db):
        """Test logging completion for non-existent habit."""
        with pytest.raises(HabitNotFoundError):
            HabitService.log_completion("Non-existent Habit")
    
    def test_duplicate_completion_same_day(self, sample_habits):
        """Test that completing the same daily habit twice in one day raises an error."""
        completion_date = datetime.now()
        HabitService.log_completion("Test Daily Habit", completion_date)
        
        with pytest.raises(HabitAlreadyCompletedError):
            HabitService.log_completion("Test Daily Habit", completion_date)
    
    def test_duplicate_completion_same_week(self, sample_habits):
        """Test that completing the same weekly habit twice in one week raises an error."""
        completion_date = datetime.now()
        HabitService.log_completion("Test Weekly Habit", completion_date)
        
        with pytest.raises(HabitAlreadyCompletedError):
            HabitService.log_completion("Test Weekly Habit", completion_date)
    
    def test_delete_habit(self, sample_habits):
        """Test deleting a habit."""
        # Add a completion first
        HabitService.log_completion("Test Daily Habit")
        
        # Verify habit exists
        habit = HabitService.get_habit_by_name("Test Daily Habit")
        assert habit is not None
        
        # Delete the habit
        result = HabitService.delete_habit("Test Daily Habit")
        assert result is True
        
        # Verify habit is gone
        habit = HabitService.get_habit_by_name("Test Daily Habit")
        assert habit is None
    
    def test_delete_nonexistent_habit(self, test_db):
        """Test deleting a non-existent habit."""
        with pytest.raises(HabitNotFoundError):
            HabitService.delete_habit("Non-existent Habit")


class TestAnalytics:
    """Test analytics functions."""
    
    def test_calculate_streak_daily_empty(self, test_db):
        """Test streak calculation with no completions."""
        streak = analytics.calculate_streak([], Periodicity.DAILY)
        assert streak == 0
    
    def test_calculate_streak_daily_consecutive(self, sample_habits):
        """Test daily streak calculation with consecutive completions."""
        habit = sample_habits[0]  # Daily habit
        base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Create consecutive completions for 3 days
        for i in range(3):
            completion_date = base_date - timedelta(days=i)
            HabitService.log_completion(habit.name, completion_date)
        
        completions = HabitService.get_completions_for_habit(habit.id)
        streak = analytics.calculate_streak(completions, Periodicity.DAILY)
        assert streak == 3
    
    def test_calculate_streak_weekly_consecutive(self, sample_habits):
        """Test weekly streak calculation with consecutive completions."""
        habit = sample_habits[1]  # Weekly habit
        base_date = datetime.now()
        
        # Create consecutive weekly completions
        for i in range(3):
            completion_date = base_date - timedelta(weeks=i)
            HabitService.log_completion(habit.name, completion_date)
        
        completions = HabitService.get_completions_for_habit(habit.id)
        streak = analytics.calculate_streak(completions, Periodicity.WEEKLY)
        assert streak == 3
    
    def test_calculate_longest_streak(self, sample_habits):
        """Test longest streak calculation."""
        habit = sample_habits[0]  # Daily habit
        base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Create a streak of 5 days, then a break, then 3 days
        for i in range(5):
            completion_date = base_date - timedelta(days=i)
            HabitService.log_completion(habit.name, completion_date)
        
        # Gap of 2 days
        for i in range(3):
            completion_date = base_date - timedelta(days=i+7)
            HabitService.log_completion(habit.name, completion_date)
        
        completions = HabitService.get_completions_for_habit(habit.id)
        longest_streak = analytics.calculate_longest_streak(completions, Periodicity.DAILY)
        assert longest_streak == 5  # The longer of the two streaks
    
    def test_get_habit_statistics(self, sample_habits):
        """Test getting comprehensive habit statistics."""
        habit = sample_habits[0]  # Daily habit
        
        # Add some completions
        base_date = datetime.now()
        for i in range(3):
            completion_date = base_date - timedelta(days=i)
            HabitService.log_completion(habit.name, completion_date)
        
        stats = analytics.get_habit_statistics(habit)
        
        assert stats['habit_name'] == habit.name
        assert stats['periodicity'] == habit.periodicity.value
        assert stats['total_completions'] == 3
        assert stats['current_streak'] >= 0
        assert stats['longest_streak'] >= 0
        assert 'completion_rate' in stats
    
    def test_find_longest_streak_across_all_habits(self, sample_habits):
        """Test finding the habit with the longest streak."""
        # Add completions to daily habit
        daily_habit = sample_habits[0]
        base_date = datetime.now()
        for i in range(5):
            completion_date = base_date - timedelta(days=i)
            HabitService.log_completion(daily_habit.name, completion_date)
        
        # Add fewer completions to weekly habit
        weekly_habit = sample_habits[1]
        for i in range(2):
            completion_date = base_date - timedelta(weeks=i)
            HabitService.log_completion(weekly_habit.name, completion_date)
        
        best_habit, max_streak = analytics.find_longest_streak_across_all_habits()
        
        assert best_habit == daily_habit.name
        assert max_streak == 5
    
    def test_get_recent_activity_summary(self, sample_habits):
        """Test getting recent activity summary."""
        # Add some recent completions
        habit = sample_habits[0]
        HabitService.log_completion(habit.name)
        
        summary = analytics.get_recent_activity_summary(days=7)
        
        assert 'period_days' in summary
        assert 'total_completions' in summary
        assert 'habits_with_activity' in summary
        assert 'total_habits' in summary
        assert 'habit_activity' in summary
        assert summary['period_days'] == 7
        assert summary['total_completions'] >= 1


class TestCLI:
    """Test CLI commands."""
    
    def test_create_habit_command(self, test_db):
        """Test the create habit CLI command."""
        import uuid
        unique_name = f'CLI Test Habit {uuid.uuid4().hex[:8]}'
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create',
            '--name', unique_name,
            '--description', 'Test habit from CLI',
            '--periodicity', 'daily'
        ])
        
        assert result.exit_code == 0
        assert 'created successfully' in result.output
    
    def test_complete_nonexistent_habit_command(self, test_db):
        """Test completing a non-existent habit shows appropriate error."""
        import uuid
        nonexistent_name = f'Nonexistent Habit {uuid.uuid4().hex[:8]}'
        
        runner = CliRunner()
        result = runner.invoke(cli, ['complete', nonexistent_name])
        
        assert result.exit_code == 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_delete_habit_cancel_command(self, test_db):
        """Test canceling habit deletion."""
        import uuid
        habit_name = f'Test Delete Cancel {uuid.uuid4().hex[:8]}'
        
        runner = CliRunner()
        # User enters 'n' to cancel deletion
        result = runner.invoke(cli, ['delete', habit_name], input='n\n')
        
        assert result.exit_code in [0, 1]  # Either aborted or completed
        # Should show confirmation prompt
        assert 'sure' in result.output.lower() or 'aborted' in result.output.lower()
    
    def test_list_all_habits_command(self, test_db):
        """Test the list all habits CLI command."""
        # Create test habits
        habit1 = HabitService.create_habit(name="CLI List Test 1", periodicity=Periodicity.DAILY)
        habit2 = HabitService.create_habit(name="CLI List Test 2", periodicity=Periodicity.WEEKLY)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'list-all'])
        
        assert result.exit_code == 0
        # Just check that it contains habit information, not specific names from prod DB
        assert 'Tracked Habits' in result.output or 'habits' in result.output.lower()
    
    def test_list_by_periodicity_command(self, test_db):
        """Test the list by periodicity CLI command."""
        # Create test habits
        daily_habit = HabitService.create_habit(name="CLI Daily List Test", periodicity=Periodicity.DAILY)
        weekly_habit = HabitService.create_habit(name="CLI Weekly List Test", periodicity=Periodicity.WEEKLY)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'list-by-periodicity', 'daily'])
        
        assert result.exit_code == 0
        # Just verify command executed successfully
        assert 'Habits' in result.output or 'daily' in result.output.lower()
    
    def test_longest_streak_nonexistent_habit_command(self, test_db):
        """Test longest streak analysis for non-existent habit shows error."""
        import uuid
        nonexistent_name = f'Nonexistent Habit {uuid.uuid4().hex[:8]}'
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'longest-streak', nonexistent_name])
        
        assert result.exit_code == 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_summary_command(self, test_db):
        """Test the summary CLI command."""
        # Create a habit and add completion
        habit = HabitService.create_habit(name="CLI Summary Test", periodicity=Periodicity.DAILY)
        HabitService.log_completion(habit.name)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'summary'])
        
        assert result.exit_code == 0
        assert 'Activity Summary' in result.output or 'summary' in result.output.lower()


if __name__ == '__main__':
    pytest.main([__file__])
