"""
Repository pattern implementation for the Habit Tracker application.

This module provides repository classes that encapsulate data access logic
following the Repository design pattern, making the OOP structure more explicit.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from .habit import Habit
from .completion import Completion
from .enums import Periodicity
from ..database import get_session_scope


class HabitRepositoryInterface(Protocol):
    """Protocol defining the interface for habit repositories."""
    
    def save(self, habit: Habit) -> Habit:
        """Save a habit to the repository."""
        ...
    
    def find_by_id(self, habit_id: int) -> Optional[Habit]:
        """Find a habit by its ID."""
        ...
    
    def find_by_name(self, name: str) -> Optional[Habit]:
        """Find a habit by its name."""
        ...
    
    def find_all(self) -> List[Habit]:
        """Get all habits."""
        ...
    
    def find_by_periodicity(self, periodicity: Periodicity) -> List[Habit]:
        """Find habits by their periodicity."""
        ...
    
    def delete(self, habit: Habit) -> bool:
        """Delete a habit from the repository."""
        ...


class CompletionRepositoryInterface(Protocol):
    """Protocol defining the interface for completion repositories."""
    
    def save(self, completion: Completion) -> Completion:
        """Save a completion to the repository."""
        ...
    
    def find_by_habit_id(self, habit_id: int) -> List[Completion]:
        """Find all completions for a specific habit."""
        ...
    
    def find_all(self) -> List[Completion]:
        """Get all completions."""
        ...
    
    def delete(self, completion: Completion) -> bool:
        """Delete a completion from the repository."""
        ...


class SQLAlchemyHabitRepository:
    """SQLAlchemy implementation that conforms to HabitRepositoryInterface protocol."""
    
    def save(self, habit: Habit) -> Habit:
        """
        Save a habit to the database.
        
        Args:
            habit: The habit to save
            
        Returns:
            The saved habit with updated ID if new
        """
        with get_session_scope() as session:
            if habit.id:
                # Update existing habit
                session.merge(habit)
            else:
                # Create new habit
                session.add(habit)
            session.flush()
            return habit
    
    def find_by_id(self, habit_id: int) -> Optional[Habit]:
        """
        Find a habit by its ID.
        
        Args:
            habit_id: The ID to search for
            
        Returns:
            The habit if found, None otherwise
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(Habit.id == habit_id).first()
    
    def find_by_name(self, name: str) -> Optional[Habit]:
        """
        Find a habit by its name.
        
        Args:
            name: The name to search for
            
        Returns:
            The habit if found, None otherwise
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(Habit.name == name).first()
    
    def find_all(self) -> List[Habit]:
        """
        Get all habits from the database.
        
        Returns:
            List of all habits ordered by creation date
        """
        with get_session_scope() as session:
            return session.query(Habit).order_by(Habit.created_at).all()
    
    def find_by_periodicity(self, periodicity: Periodicity) -> List[Habit]:
        """
        Find habits by their periodicity.
        
        Args:
            periodicity: The periodicity to filter by
            
        Returns:
            List of habits with the specified periodicity
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(
                Habit.periodicity == periodicity
            ).order_by(Habit.created_at).all()
    
    def delete(self, habit: Habit) -> bool:
        """
        Delete a habit from the database.
        
        Args:
            habit: The habit to delete
            
        Returns:
            True if deleted successfully
        """
        with get_session_scope() as session:
            if habit.id:
                session.delete(session.merge(habit))
                return True
            return False
    
    def exists_by_name(self, name: str) -> bool:
        """
        Check if a habit with the given name exists.
        
        Args:
            name: The name to check
            
        Returns:
            True if a habit with this name exists
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(Habit.name == name).count() > 0


class SQLAlchemyCompletionRepository:
    """SQLAlchemy implementation of the CompletionRepository."""
    
    def save(self, completion: Completion) -> Completion:
        """
        Save a completion to the database.
        
        Args:
            completion: The completion to save
            
        Returns:
            The saved completion with updated ID if new
        """
        with get_session_scope() as session:
            if completion.id:
                session.merge(completion)
            else:
                session.add(completion)
            session.flush()
            return completion
    
    def find_by_habit_id(self, habit_id: int) -> List[Completion]:
        """
        Find all completions for a specific habit.
        
        Args:
            habit_id: The habit ID to search for
            
        Returns:
            List of completions ordered by completion date (newest first)
        """
        with get_session_scope() as session:
            return session.query(Completion).filter(
                Completion.habit_id == habit_id
            ).order_by(desc(Completion.completed_at)).all()
    
    def find_all(self) -> List[Completion]:
        """
        Get all completions from the database.
        
        Returns:
            List of all completions ordered by completion date (newest first)
        """
        with get_session_scope() as session:
            return session.query(Completion).order_by(
                desc(Completion.completed_at)
            ).all()
    
    def find_in_period(self, habit_id: int, start_date: datetime, 
                      end_date: datetime) -> List[Completion]:
        """
        Find completions for a habit within a date range.
        
        Args:
            habit_id: The habit ID
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            List of completions within the date range
        """
        with get_session_scope() as session:
            return session.query(Completion).filter(
                and_(
                    Completion.habit_id == habit_id,
                    Completion.completed_at >= start_date,
                    Completion.completed_at < end_date
                )
            ).order_by(desc(Completion.completed_at)).all()
    
    def delete(self, completion: Completion) -> bool:
        """
        Delete a completion from the database.
        
        Args:
            completion: The completion to delete
            
        Returns:
            True if deleted successfully
        """
        with get_session_scope() as session:
            if completion.id:
                session.delete(session.merge(completion))
                return True
            return False


# Singleton instances for easy access
habit_repository = SQLAlchemyHabitRepository()
completion_repository = SQLAlchemyCompletionRepository()
