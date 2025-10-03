"""
Habit service containing business logic for habit operations.

This module provides a service layer for habit CRUD operations,
abstracting the database interactions and providing business logic.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from ..core.models import Habit, Completion, Periodicity
from ..core.database import get_session_scope
from ..core.exceptions import (
    HabitNotFoundError,
    HabitAlreadyExistsError,
    HabitAlreadyCompletedError
)


class HabitService:
    """Service class for habit-related operations."""
    
    @staticmethod
    def create_habit(name: str, description: str = None, periodicity: Periodicity = Periodicity.DAILY) -> Habit:
        """
        Create a new habit in the database.
        
        Args:
            name: The name of the habit (must be unique)
            description: Optional description of the habit
            periodicity: How often the habit should be performed
            
        Returns:
            The created Habit object
            
        Raises:
            HabitAlreadyExistsError: If a habit with the same name already exists
        """
        with get_session_scope() as session:
            # Check if habit already exists
            existing_habit = session.query(Habit).filter(Habit.name == name).first()
            if existing_habit:
                raise HabitAlreadyExistsError(f"Habit '{name}' already exists")
            
            habit = Habit(
                name=name,
                description=description,
                periodicity=periodicity
            )
            session.add(habit)
            session.flush()  # Get the ID before commit
            return habit

    @staticmethod
    def get_all_habits() -> List[Habit]:
        """
        Retrieve all habits from the database.
        
        Returns:
            A list of all Habit objects, ordered by creation date
        """
        with get_session_scope() as session:
            return session.query(Habit).order_by(Habit.created_at).all()

    @staticmethod
    def get_habits_by_periodicity(periodicity: Periodicity) -> List[Habit]:
        """
        Retrieve all habits with a specific periodicity.
        
        Args:
            periodicity: The periodicity to filter by
            
        Returns:
            A list of Habit objects with the specified periodicity
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(
                Habit.periodicity == periodicity
            ).order_by(Habit.created_at).all()

    @staticmethod
    def get_habit_by_name(name: str) -> Optional[Habit]:
        """
        Retrieve a habit by its name.
        
        Args:
            name: The name of the habit to find
            
        Returns:
            The Habit object if found, None otherwise
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(Habit.name == name).first()

    @staticmethod
    def get_habit_by_id(habit_id: int) -> Optional[Habit]:
        """
        Retrieve a habit by its ID.
        
        Args:
            habit_id: The ID of the habit to find
            
        Returns:
            The Habit object if found, None otherwise
        """
        with get_session_scope() as session:
            return session.query(Habit).filter(Habit.id == habit_id).first()

    @staticmethod
    def delete_habit(name: str) -> bool:
        """
        Delete a habit and all its completions.
        
        Args:
            name: The name of the habit to delete
            
        Returns:
            True if the habit was deleted, False if not found
            
        Raises:
            HabitNotFoundError: If the habit doesn't exist
        """
        with get_session_scope() as session:
            habit = session.query(Habit).filter(Habit.name == name).first()
            if not habit:
                raise HabitNotFoundError(f"Habit '{name}' not found")
            
            session.delete(habit)
            return True

    @staticmethod
    def log_completion(name: str, completion_date: datetime = None) -> Completion:
        """
        Log a completion for a habit.
        
        Args:
            name: The name of the habit to mark as complete
            completion_date: Optional specific date/time of completion. Defaults to now.
            
        Returns:
            The created Completion object
            
        Raises:
            HabitNotFoundError: If the habit doesn't exist
            HabitAlreadyCompletedError: If the habit is already completed for the period
        """
        if completion_date is None:
            completion_date = datetime.now()
        
        with get_session_scope() as session:
            habit = session.query(Habit).filter(Habit.name == name).first()
            if not habit:
                raise HabitNotFoundError(f"Habit '{name}' not found")
            
            # Check if already completed for this period
            if HabitService._is_habit_completed_for_period(habit.id, completion_date, session):
                period_name = "day" if habit.periodicity == Periodicity.DAILY else "week"
                raise HabitAlreadyCompletedError(
                    f"Habit '{name}' is already completed for this {period_name}"
                )
            
            completion = Completion(
                habit_id=habit.id,
                completed_at=completion_date
            )
            session.add(completion)
            session.flush()
            return completion

    @staticmethod
    def _is_habit_completed_for_period(habit_id: int, check_date: datetime, session: Session = None) -> bool:
        """
        Check if a habit is already completed for a given period.
        
        Args:
            habit_id: The ID of the habit to check
            check_date: The date to check completion for
            session: Optional existing database session
            
        Returns:
            True if the habit is completed for the period, False otherwise
        """
        def _check_completion(session: Session) -> bool:
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            if not habit:
                return False
            
            if habit.periodicity == Periodicity.DAILY:
                # Check for completion on the same day
                start_of_day = check_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
            else:  # WEEKLY
                # Check for completion in the same week (Monday to Sunday)
                days_since_monday = check_date.weekday()
                start_of_week = check_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
                end_of_week = start_of_week + timedelta(days=7)
            
            completion = session.query(Completion).filter(
                and_(
                    Completion.habit_id == habit_id,
                    Completion.completed_at >= (start_of_day if habit.periodicity == Periodicity.DAILY else start_of_week),
                    Completion.completed_at < (end_of_day if habit.periodicity == Periodicity.DAILY else end_of_week)
                )
            ).first()
            
            return completion is not None
        
        if session:
            return _check_completion(session)
        else:
            with get_session_scope() as session:
                return _check_completion(session)

    @staticmethod
    def get_completions_for_habit(habit_id: int, limit: int = None) -> List[Completion]:
        """
        Get all completions for a specific habit.
        
        Args:
            habit_id: The ID of the habit
            limit: Optional limit on number of completions to return
            
        Returns:
            A list of Completion objects, ordered by completion date (newest first)
        """
        with get_session_scope() as session:
            query = session.query(Completion).filter(
                Completion.habit_id == habit_id
            ).order_by(desc(Completion.completed_at))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()

    @staticmethod
    def get_all_completions() -> List[Completion]:
        """
        Get all completions from the database.
        
        Returns:
            A list of all Completion objects, ordered by completion date (newest first)
        """
        with get_session_scope() as session:
            return session.query(Completion).order_by(desc(Completion.completed_at)).all()






