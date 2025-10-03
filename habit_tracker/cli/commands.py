#!/usr/bin/env python3
"""
Main CLI application for the Habit Tracking app.

This module provides the command-line interface using Click library
to interact with the habit tracking system.
"""

import click
from datetime import datetime
from typing import Optional

from ..core.models import Periodicity
from ..core.database import db_manager
from ..core.exceptions import (
    HabitNotFoundError,
    HabitAlreadyExistsError,
    HabitAlreadyCompletedError
)
from ..services.habit_service import HabitService
from ..services import analytics_service as analytics


@click.group()
@click.version_option(version="1.0.0", prog_name="Habit Tracker")
def cli():
    """
    Habit Tracker - A simple CLI application to track your daily and weekly habits.
    
    Use this tool to create habits, mark them as complete, and analyze your progress.
    """
    # Initialize database on startup
    db_manager.init_db()


@cli.command()
@click.option('--name', prompt='Enter habit name', help='Name of the habit')
@click.option('--description', help='Description of the habit (optional)')
@click.option('--periodicity', 
              type=click.Choice(['daily', 'weekly'], case_sensitive=False),
              prompt='Enter periodicity (daily/weekly)', 
              help='How often the habit should be performed')
def create(name: str, description: Optional[str], periodicity: str):
    """Create a new habit to track."""
    try:
        period_enum = Periodicity.DAILY if periodicity.lower() == 'daily' else Periodicity.WEEKLY
        
        habit = HabitService.create_habit(
            name=name.strip(),
            description=description.strip() if description else None,
            periodicity=period_enum
        )
        
        click.echo(click.style(
            f"✅ Habit '{habit.name}' ({habit.periodicity.value}) created successfully!",
            fg='green'
        ))
        
    except HabitAlreadyExistsError as e:
        click.echo(click.style(f"❌ Error: {e}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg='red'))


@cli.command()
@click.argument('habit_name')
def complete(habit_name: str):
    """Mark a habit as completed for the current period."""
    try:
        HabitService.log_completion(habit_name)
        habit = HabitService.get_habit_by_name(habit_name)
        
        period_name = "today" if habit.periodicity == Periodicity.DAILY else "this week"
        
        click.echo(click.style(
            f"✅ Habit '{habit_name}' marked as complete for {period_name}!",
            fg='green'
        ))
        
        # Show current streak
        completions = HabitService.get_completions_for_habit(habit.id)
        current_streak = analytics.calculate_streak(completions, habit.periodicity)
        
        if current_streak > 1:
            streak_unit = "days" if habit.periodicity == Periodicity.DAILY else "weeks"
            click.echo(click.style(
                f"🔥 Current streak: {current_streak} {streak_unit}",
                fg='yellow'
            ))
        
    except HabitNotFoundError as e:
        click.echo(click.style(f"❌ Error: {e}", fg='red'))
    except HabitAlreadyCompletedError as e:
        click.echo(click.style(f"⚠️  {e}", fg='yellow'))
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg='red'))


@cli.command()
@click.argument('habit_name')
@click.confirmation_option(prompt='Are you sure you want to delete this habit and all its data?')
def delete(habit_name: str):
    """Delete a habit and all its completion data."""
    try:
        HabitService.delete_habit(habit_name)
        click.echo(click.style(
            f"✅ Habit '{habit_name}' and all its completion data deleted successfully!",
            fg='green'
        ))
        
    except HabitNotFoundError as e:
        click.echo(click.style(f"❌ Error: {e}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg='red'))


@cli.group()
def analyze():
    """Analyze your habits and view statistics."""
    pass


@analyze.command('list-all')
def list_all_habits():
    """List all currently tracked habits."""
    try:
        stats = analytics.get_all_habits_statistics()
        
        if not stats:
            click.echo(click.style("📝 No habits found. Create your first habit with 'create' command!", fg='yellow'))
            return
        
        click.echo(click.style("\n📊 All Tracked Habits:", fg='blue', bold=True))
        click.echo("-" * 50)
        
        for stat in stats:
            # Format creation date
            created_date = stat['created_at'].strftime('%Y-%m-%d') if stat['created_at'] else 'Unknown'
            
            # Create status indicators
            streak_emoji = "🔥" if stat['current_streak'] > 0 else "💤"
            
            click.echo(f"• ID: {stat.get('habit_id', 'N/A')}")
            click.echo(f"  Name: {stat['habit_name']}")
            click.echo(f"  Periodicity: {stat['periodicity']}")
            click.echo(f"  Created: {created_date}")
            click.echo(f"  {streak_emoji} Current Streak: {stat['current_streak']}")
            click.echo(f"  🏆 Best Streak: {stat['longest_streak']}")
            click.echo(f"  ✅ Total Completions: {stat['total_completions']}")
            
            if 'completion_rate' in stat:
                if stat['completion_rate'] >= 80:
                    rate_color = 'green'
                elif stat['completion_rate'] >= 60:
                    rate_color = 'yellow'
                else:
                    rate_color = 'red'
                click.echo(click.style(f"  📈 Completion Rate: {stat['completion_rate']:.1f}%", fg=rate_color))
            
            click.echo()
            
    except Exception as e:
        click.echo(click.style(f"❌ Error retrieving habits: {e}", fg='red'))


@analyze.command('list-by-periodicity')
@click.argument('periodicity', type=click.Choice(['daily', 'weekly'], case_sensitive=False))
def list_by_periodicity(periodicity: str):
    """List habits filtered by periodicity (daily or weekly)."""
    try:
        period_enum = Periodicity.DAILY if periodicity.lower() == 'daily' else Periodicity.WEEKLY
        stats = analytics.get_habits_by_periodicity_with_stats(period_enum)
        
        if not stats:
            click.echo(click.style(f"📝 No {periodicity} habits found.", fg='yellow'))
            return
        
        click.echo(click.style(f"\n📊 {periodicity.title()} Habits:", fg='blue', bold=True))
        click.echo("-" * 40)
        
        for stat in stats:
            created_date = stat['created_at'].strftime('%Y-%m-%d') if stat['created_at'] else 'Unknown'
            streak_emoji = "🔥" if stat['current_streak'] > 0 else "💤"
            
            click.echo(f"• Name: {stat['habit_name']}")
            click.echo(f"  Created: {created_date}")
            click.echo(f"  {streak_emoji} Current Streak: {stat['current_streak']}")
            click.echo(f"  🏆 Best Streak: {stat['longest_streak']}")
            click.echo()
            
    except Exception as e:
        click.echo(click.style(f"❌ Error retrieving habits: {e}", fg='red'))


@analyze.command('longest-streak')
@click.argument('habit_name')
def longest_streak_for_habit(habit_name: str):
    """Show the longest streak for a specific habit."""
    try:
        habit = HabitService.get_habit_by_name(habit_name)
        if not habit:
            click.echo(click.style(f"❌ Habit '{habit_name}' not found.", fg='red'))
            return
        
        stats = analytics.get_habit_statistics(habit)
        longest_streak = stats['longest_streak']
        current_streak = stats['current_streak']
        
        streak_unit = "days" if habit.periodicity == Periodicity.DAILY else "weeks"
        
        click.echo(click.style(f"\n🏆 Streak Analysis for '{habit_name}':", fg='blue', bold=True))
        click.echo(f"Longest streak: {longest_streak} {streak_unit}")
        click.echo(f"Current streak: {current_streak} {streak_unit}")
        
        if current_streak == longest_streak and current_streak > 0:
            click.echo(click.style("🎉 You're at your personal best!", fg='green'))
        elif longest_streak > 0:
            difference = longest_streak - current_streak
            click.echo(f"📈 {difference} {streak_unit} away from your best!")
            
    except Exception as e:
        click.echo(click.style(f"❌ Error calculating streak: {e}", fg='red'))


@analyze.command('longest-streak-all')
def longest_streak_all_habits():
    """Show the habit with the longest streak across all habits."""
    try:
        best_habit, max_streak = analytics.find_longest_streak_across_all_habits()
        
        if best_habit is None:
            click.echo(click.style("📝 No habits found.", fg='yellow'))
            return
        
        if max_streak == 0:
            click.echo(click.style("📊 No completions found for any habit.", fg='yellow'))
            return
        
        # Get the habit details to determine the unit
        habit = HabitService.get_habit_by_name(best_habit)
        streak_unit = "days" if habit.periodicity == Periodicity.DAILY else "weeks"
        
        click.echo(click.style(f"\n🏆 Overall Champion:", fg='blue', bold=True))
        click.echo(f"Longest streak: '{best_habit}' with {max_streak} {streak_unit}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error finding longest streak: {e}", fg='red'))


@analyze.command('summary')
@click.option('--days', default=7, help='Number of days to look back (default: 7)')
def recent_summary(days: int):
    """Show a summary of recent habit activity."""
    try:
        summary = analytics.get_recent_activity_summary(days)
        
        click.echo(click.style(f"\n📊 Activity Summary (Last {days} days):", fg='blue', bold=True))
        click.echo("-" * 40)
        click.echo(f"Total completions: {summary['total_completions']}")
        click.echo(f"Habits with activity: {summary['habits_with_activity']}/{summary['total_habits']}")
        
        if summary['habit_activity']:
            click.echo(click.style("\n📈 Per-Habit Activity:", fg='cyan'))
            for activity in summary['habit_activity']:
                name = activity['habit_name']
                completions = activity['completions_in_period']
                streak = activity['current_streak']
                periodicity = activity['periodicity']
                
                streak_unit = "days" if periodicity == 'daily' else "weeks"
                streak_emoji = "🔥" if streak > 0 else "💤"
                
                click.echo(f"• {name}: {completions} completions, {streak_emoji} {streak} {streak_unit} streak")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error generating summary: {e}", fg='red'))


@cli.command()
@click.confirmation_option(prompt='This will delete ALL habits and data. Are you sure?')
def reset():
    """Reset the database (delete all habits and data)."""
    try:
        db_manager.reset_database()
        click.echo(click.style("✅ Database reset successfully! All data has been cleared.", fg='green'))
    except Exception as e:
        click.echo(click.style(f"❌ Error resetting database: {e}", fg='red'))


if __name__ == '__main__':
    cli()
