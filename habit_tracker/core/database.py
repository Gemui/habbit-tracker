"""
Database configuration and session management for the Habit Tracking application.

This module handles SQLite database connection, session creation, and initialization.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


class DatabaseManager:
    """
    Manages database connections and sessions for the application.
    
    This class provides a singleton pattern for database access and handles
    session lifecycle management.
    """
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self.init_db()
    
    def init_db(self, database_url: str = None) -> None:
        """
        Initialize the database connection and create tables.
        
        Args:
            database_url: Optional database URL. Defaults to SQLite file.
        """
        if database_url is None:
            # Use SQLite database in the project directory
            # Store database in data directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(project_root, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "habits.db")
            database_url = f"sqlite:///{db_path}"
        
        self._engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,  # Verify connections before use
        )
        
        # Create session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Prevent detached instance errors
        )
        
        # Create all tables
        Base.metadata.create_all(bind=self._engine)
    
    def get_engine(self):
        """Get the SQLAlchemy engine."""
        if self._engine is None:
            self.init_db()
        return self._engine
    
    def get_session(self) -> Session:
        """
        Create and return a new database session.
        
        Returns:
            A new SQLAlchemy session instance.
            
        Note:
            The caller is responsible for closing the session.
        """
        if self._session_factory is None:
            self.init_db()
        return self._session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        This context manager handles session lifecycle, commits on success,
        and rolls back on exceptions.
        
        Yields:
            A database session within a transaction.
            
        Example:
            with db_manager.session_scope() as session:
                habit = Habit(name="Exercise", periodicity=Periodicity.DAILY)
                session.add(habit)
                # Automatic commit on success, rollback on exception
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def reset_database(self) -> None:
        """
        Drop all tables and recreate them.
        
        Warning:
            This will delete all data in the database.
        """
        if self._engine is not None:
            Base.metadata.drop_all(bind=self._engine)
            Base.metadata.create_all(bind=self._engine)


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session() -> Session:
    """
    Convenience function to get a database session.
    
    Returns:
        A new database session.
    """
    return db_manager.get_session()


def get_session_scope():
    """
    Convenience function to get a session context manager.
    
    Returns:
        A context manager for database sessions.
    """
    return db_manager.session_scope()
