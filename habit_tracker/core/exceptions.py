"""Custom exceptions for the Habit Tracker application."""


class HabitTrackerError(Exception):
    """Base exception for all Habit Tracker errors."""
    pass


class HabitNotFoundError(HabitTrackerError):
    """Raised when a habit is not found in the database."""
    pass


class HabitAlreadyExistsError(HabitTrackerError):
    """Raised when trying to create a habit that already exists."""
    pass


class HabitAlreadyCompletedError(HabitTrackerError):
    """Raised when trying to complete a habit that's already completed for the period."""
    pass


class DatabaseError(HabitTrackerError):
    """Raised when there's a database-related error."""
    pass


class ValidationError(HabitTrackerError):
    """Raised when input validation fails."""
    pass






