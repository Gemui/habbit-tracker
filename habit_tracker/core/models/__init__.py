"""
Models package for the Habit Tracker application.

This package contains all data models used by the application.
"""

from sqlalchemy.orm import declarative_base

# Create the base class for all models
Base = declarative_base()

# Import enums first
from .enums import Periodicity

# Import models after Base is defined
from .habit import Habit
from .completion import Completion

__all__ = ['Base', 'Periodicity', 'Habit', 'Completion']
