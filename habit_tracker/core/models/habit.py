"""
Habit model for the Habit Tracker application.

This module contains the Habit model representing trackable habits.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base
from .enums import Periodicity

# Avoid circular imports
if TYPE_CHECKING:
    from .completion import Completion


class Habit(Base):
    """
    Habit model representing a trackable habit.
    
    A habit is something a user wants to track regularly, either daily or weekly.
    Each habit can have multiple completion records showing when it was performed.
    
    Attributes:
        id: Primary key
        name: Unique name of the habit
        description: Optional description of the habit
        periodicity: How often the habit should be performed (daily/weekly)
        created_at: Timestamp when the habit was created
        completions: Relationship to completion records
    """
    __tablename__ = "habits"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core habit information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    periodicity = Column(Enum(Periodicity), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    completions = relationship(
        "Completion", 
        back_populates="habit", 
        cascade="all, delete-orphan",
        lazy="dynamic"  # For better performance with large completion lists
    )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<Habit(id={self.id}, name='{self.name}', periodicity='{self.periodicity.value}')>"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        return f"{self.name} ({self.periodicity.value})"
    
    def is_daily(self) -> bool:
        """Check if this is a daily habit."""
        return self.periodicity == Periodicity.DAILY
    
    def is_weekly(self) -> bool:
        """Check if this is a weekly habit."""
        return self.periodicity == Periodicity.WEEKLY
    
    @property
    def completion_count(self) -> int:
        """Get the total number of completions for this habit."""
        return self.completions.count()
    
    def get_recent_completions(self, limit: int = 10):
        """
        Get the most recent completions for this habit.
        
        Args:
            limit: Maximum number of completions to return
            
        Returns:
            List of recent Completion objects
        """
        return (self.completions
                .order_by(self.completions.property.mapper.class_.completed_at.desc())
                .limit(limit)
                .all())
    
    def check_off(self, completion_date=None):
        """
        Mark this habit as completed for a given date.
        
        This is the main OOP method for habit completion. It encapsulates
        the business logic for checking off a habit.
        
        Args:
            completion_date: Optional datetime when the habit was completed.
                           Defaults to now.
                           
        Returns:
            Completion object representing the check-off event
            
        Raises:
            HabitAlreadyCompletedError: If already completed for the period
        """
        from ..exceptions import HabitAlreadyCompletedError
        from ...services.habit_service import HabitService
        
        return HabitService.log_completion(self.name, completion_date)
    
    def to_dict(self) -> dict:
        """
        Convert habit to dictionary representation.
        
        Returns:
            Dictionary containing habit attributes
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'periodicity': self.periodicity.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completion_count': self.completion_count,
            'is_daily': self.is_daily(),
            'is_weekly': self.is_weekly()
        }
    
    def get_current_streak(self) -> int:
        """
        Get the current streak for this habit.
        
        Returns:
            Current streak length
        """
        from ...services.analytics_service import calculate_streak, HabitService
        
        completions = HabitService.get_completions_for_habit(self.id)
        return calculate_streak(completions, self.periodicity)
    
    def get_longest_streak(self) -> int:
        """
        Get the longest streak ever achieved for this habit.
        
        Returns:
            Longest streak length
        """
        from ...services.analytics_service import calculate_longest_streak, HabitService
        
        completions = HabitService.get_completions_for_habit(self.id)
        return calculate_longest_streak(completions, self.periodicity)
    
    def is_completed_today(self) -> bool:
        """
        Check if this habit is completed for today/this week.
        
        Returns:
            True if completed for the current period
        """
        from datetime import datetime
        from ...services.habit_service import HabitService
        
        return HabitService._is_habit_completed_for_period(
            self.id, 
            datetime.now()
        )