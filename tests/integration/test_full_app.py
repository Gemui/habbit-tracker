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


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create a temporary file for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Initialize test database
    test_db_url = f"sqlite:///{temp_db.name}"
    db_manager = DatabaseManager()
    db_manager.init_db(test_db_url)
    
    yield db_manager
    
    # Cleanup
    os.unlink(temp_db.name)


@pytest.fixture
def sample_habits(test_db):
    """Create sample habits for testing."""
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
        crud.create_habit("Duplicate Habit", periodicity=Periodicity.DAILY)
        
        with pytest.raises(crud.HabitAlreadyExistsError):
            crud.create_habit("Duplicate Habit", periodicity=Periodicity.DAILY)
    
    def test_get_all_habits(self, sample_habits):
        """Test retrieving all habits."""
        habits = crud.get_all_habits()
        assert len(habits) == 2
        assert any(h.name == "Test Daily Habit" for h in habits)
        assert any(h.name == "Test Weekly Habit" for h in habits)
    
    def test_get_habits_by_periodicity(self, sample_habits):
        """Test filtering habits by periodicity."""
        daily_habits = crud.get_habits_by_periodicity(Periodicity.DAILY)
        weekly_habits = crud.get_habits_by_periodicity(Periodicity.WEEKLY)
        
        assert len(daily_habits) == 1
        assert len(weekly_habits) == 1
        assert daily_habits[0].name == "Test Daily Habit"
        assert weekly_habits[0].name == "Test Weekly Habit"
    
    def test_get_habit_by_name(self, sample_habits):
        """Test retrieving a habit by name."""
        habit = crud.get_habit_by_name("Test Daily Habit")
        assert habit is not None
        assert habit.name == "Test Daily Habit"
        
        non_existent = crud.get_habit_by_name("Non-existent Habit")
        assert non_existent is None
    
    def test_log_completion(self, sample_habits):
        """Test logging a habit completion."""
        completion = crud.log_completion("Test Daily Habit")
        
        assert completion.habit_id == sample_habits[0].id
        assert isinstance(completion.completed_at, datetime)
    
    def test_log_completion_nonexistent_habit(self, test_db):
        """Test logging completion for non-existent habit."""
        with pytest.raises(crud.HabitNotFoundError):
            crud.log_completion("Non-existent Habit")
    
    def test_duplicate_completion_same_day(self, sample_habits):
        """Test that completing the same daily habit twice in one day raises an error."""
        completion_date = datetime.now()
        crud.log_completion("Test Daily Habit", completion_date)
        
        with pytest.raises(crud.HabitAlreadyCompletedError):
            crud.log_completion("Test Daily Habit", completion_date)
    
    def test_duplicate_completion_same_week(self, sample_habits):
        """Test that completing the same weekly habit twice in one week raises an error."""
        completion_date = datetime.now()
        crud.log_completion("Test Weekly Habit", completion_date)
        
        with pytest.raises(crud.HabitAlreadyCompletedError):
            crud.log_completion("Test Weekly Habit", completion_date)
    
    def test_delete_habit(self, sample_habits):
        """Test deleting a habit."""
        # Add a completion first
        crud.log_completion("Test Daily Habit")
        
        # Verify habit exists
        habit = crud.get_habit_by_name("Test Daily Habit")
        assert habit is not None
        
        # Delete the habit
        result = crud.delete_habit("Test Daily Habit")
        assert result is True
        
        # Verify habit is gone
        habit = crud.get_habit_by_name("Test Daily Habit")
        assert habit is None
    
    def test_delete_nonexistent_habit(self, test_db):
        """Test deleting a non-existent habit."""
        with pytest.raises(crud.HabitNotFoundError):
            crud.delete_habit("Non-existent Habit")


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
            crud.log_completion(habit.name, completion_date)
        
        completions = crud.get_completions_for_habit(habit.id)
        streak = analytics.calculate_streak(completions, Periodicity.DAILY)
        assert streak == 3
    
    def test_calculate_streak_weekly_consecutive(self, sample_habits):
        """Test weekly streak calculation with consecutive completions."""
        habit = sample_habits[1]  # Weekly habit
        base_date = datetime.now()
        
        # Create consecutive weekly completions
        for i in range(3):
            completion_date = base_date - timedelta(weeks=i)
            crud.log_completion(habit.name, completion_date)
        
        completions = crud.get_completions_for_habit(habit.id)
        streak = analytics.calculate_streak(completions, Periodicity.WEEKLY)
        assert streak == 3
    
    def test_calculate_longest_streak(self, sample_habits):
        """Test longest streak calculation."""
        habit = sample_habits[0]  # Daily habit
        base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Create a streak of 5 days, then a break, then 3 days
        for i in range(5):
            completion_date = base_date - timedelta(days=i)
            crud.log_completion(habit.name, completion_date)
        
        # Gap of 2 days
        for i in range(3):
            completion_date = base_date - timedelta(days=i+7)
            crud.log_completion(habit.name, completion_date)
        
        completions = crud.get_completions_for_habit(habit.id)
        longest_streak = analytics.calculate_longest_streak(completions, Periodicity.DAILY)
        assert longest_streak == 5  # The longer of the two streaks
    
    def test_get_habit_statistics(self, sample_habits):
        """Test getting comprehensive habit statistics."""
        habit = sample_habits[0]  # Daily habit
        
        # Add some completions
        base_date = datetime.now()
        for i in range(3):
            completion_date = base_date - timedelta(days=i)
            crud.log_completion(habit.name, completion_date)
        
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
            crud.log_completion(daily_habit.name, completion_date)
        
        # Add fewer completions to weekly habit
        weekly_habit = sample_habits[1]
        for i in range(2):
            completion_date = base_date - timedelta(weeks=i)
            crud.log_completion(weekly_habit.name, completion_date)
        
        best_habit, max_streak = analytics.find_longest_streak_across_all_habits()
        
        assert best_habit == daily_habit.name
        assert max_streak == 5
    
    def test_get_recent_activity_summary(self, sample_habits):
        """Test getting recent activity summary."""
        # Add some recent completions
        habit = sample_habits[0]
        crud.log_completion(habit.name)
        
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
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create',
            '--name', 'CLI Test Habit',
            '--description', 'Test habit from CLI',
            '--periodicity', 'daily'
        ])
        
        assert result.exit_code == 0
        assert 'created successfully' in result.output
        
        # Verify habit was created
        habit = crud.get_habit_by_name('CLI Test Habit')
        assert habit is not None
    
    def test_complete_habit_command(self, sample_habits):
        """Test the complete habit CLI command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['complete', 'Test Daily Habit'])
        
        assert result.exit_code == 0
        assert 'marked as complete' in result.output
    
    def test_delete_habit_command(self, sample_habits):
        """Test the delete habit CLI command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['delete', 'Test Daily Habit'], input='y\n')
        
        assert result.exit_code == 0
        assert 'deleted successfully' in result.output
        
        # Verify habit was deleted
        habit = crud.get_habit_by_name('Test Daily Habit')
        assert habit is None
    
    def test_list_all_habits_command(self, sample_habits):
        """Test the list all habits CLI command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'list-all'])
        
        assert result.exit_code == 0
        assert 'Test Daily Habit' in result.output
        assert 'Test Weekly Habit' in result.output
    
    def test_list_by_periodicity_command(self, sample_habits):
        """Test the list by periodicity CLI command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'list-by-periodicity', 'daily'])
        
        assert result.exit_code == 0
        assert 'Test Daily Habit' in result.output
        assert 'Test Weekly Habit' not in result.output
    
    def test_longest_streak_command(self, sample_habits):
        """Test the longest streak CLI command."""
        # Add some completions
        habit = sample_habits[0]
        for i in range(3):
            completion_date = datetime.now() - timedelta(days=i)
            crud.log_completion(habit.name, completion_date)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'longest-streak', 'Test Daily Habit'])
        
        assert result.exit_code == 0
        assert 'Streak Analysis' in result.output
    
    def test_summary_command(self, sample_habits):
        """Test the summary CLI command."""
        # Add a completion
        crud.log_completion('Test Daily Habit')
        
        runner = CliRunner()
        result = runner.invoke(cli, ['analyze', 'summary'])
        
        assert result.exit_code == 0
        assert 'Activity Summary' in result.output


if __name__ == '__main__':
    pytest.main([__file__])
