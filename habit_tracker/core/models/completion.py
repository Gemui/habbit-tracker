"""
Completion model for the Habit Tracker application.

This module contains the Completion model representing when habits were completed.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base

# Avoid circular imports
if TYPE_CHECKING:
    from .habit import Habit


class Completion(Base):
    """
    Completion model representing when a habit was completed.
    
    A completion record shows that a user performed a specific habit
    at a particular date and time.
    
    Attributes:
        id: Primary key
        habit_id: Foreign key to the associated habit
        completed_at: Timestamp when the habit was marked as complete
        habit: Relationship back to the habit
    """
    __tablename__ = "completions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to habit
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    
    # Timestamp
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    habit = relationship("Habit", back_populates="completions")
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Completion(id={self.id}, habit_id={self.habit_id}, completed_at='{self.completed_at}')>"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        if self.completed_at:
            return f"Completed on {self.completed_at.strftime('%Y-%m-%d %H:%M')}"
        return "Completion (pending)"
    
    @property
    def completion_date(self) -> datetime:
        """Get the date portion of the completion timestamp."""
        return self.completed_at.date() if self.completed_at else None
    
    @property
    def completion_time(self) -> datetime:
        """Get the time portion of the completion timestamp."""
        return self.completed_at.time() if self.completed_at else None
    
    def is_today(self) -> bool:
        """Check if this completion was made today."""
        if not self.completed_at:
            return False
        return self.completed_at.date() == datetime.now().date()
    
    def days_ago(self) -> int:
        """Get the number of days since this completion."""
        if not self.completed_at:
            return 999999  # Large number instead of float('inf')
        return (datetime.now().date() - self.completed_at.date()).days
    
    def to_dict(self) -> dict:
        """
        Convert completion to dictionary representation.
        
        Returns:
            Dictionary containing completion attributes
        """
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'habit_name': self.habit.name if self.habit else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'is_today': self.is_today(),
            'days_ago': self.days_ago()
        }
    
    def is_in_same_period(self, other_completion) -> bool:
        """
        Check if this completion is in the same period as another completion.
        
        Args:
            other_completion: Another Completion object or datetime
            
        Returns:
            True if both completions are in the same period (day/week)
        """
        if not self.completed_at:
            return False
            
        if hasattr(other_completion, 'completed_at'):
            other_date = other_completion.completed_at
        else:
            other_date = other_completion
            
        if not other_date:
            return False
            
        # Get habit to determine periodicity
        if not self.habit:
            return False
            
        if self.habit.periodicity.name == 'DAILY':
            return self.completed_at.date() == other_date.date()
        else:  # WEEKLY
            # Check if both dates are in the same week
            self_week_start = self.completed_at.date() - timedelta(days=self.completed_at.weekday())
            other_week_start = other_date.date() - timedelta(days=other_date.weekday())
            return self_week_start == other_week_start
    
    @classmethod
    def create_event(cls, habit_id: int, completion_date=None):
        """
        Factory method to create a new habit completion event.
        
        Args:
            habit_id: ID of the habit being completed
            completion_date: Optional datetime of completion
            
        Returns:
            New Completion instance
        """
        from datetime import datetime
        
        if completion_date is None:
            completion_date = datetime.now()
            
        return cls(
            habit_id=habit_id,
            completed_at=completion_date
        )