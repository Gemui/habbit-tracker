"""
Habit Tracker - A comprehensive CLI application for tracking daily and weekly habits.

This package provides tools for creating habits, tracking completions, and analyzing progress.
"""

__version__ = "1.0.0"
__author__ = "Ahmed Gamal"
__email__ = "your.email@example.com"

from habit_tracker.core.models import Habit, Completion, Periodicity

__all__ = ["Habit", "Completion", "Periodicity"]

