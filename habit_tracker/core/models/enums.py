"""
Enums for the Habit Tracker application.

This module contains all enumeration types used across the application.
"""

from enum import Enum as PyEnum


class Periodicity(PyEnum):
    """
    Enum for habit periodicity options.
    
    This defines how frequently a habit should be performed.
    """
    DAILY = "daily"
    WEEKLY = "weekly"


class HabitStatus(PyEnum):
    """
    Enum for habit status options.
    
    This could be used for future features like pausing habits.
    """
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class CompletionType(PyEnum):
    """
    Enum for completion type options.
    
    This could be used to distinguish manual vs automatic completions.
    """
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    IMPORTED = "imported"






