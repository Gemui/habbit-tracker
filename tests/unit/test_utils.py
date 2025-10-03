"""
Unit tests for utility functions.

This module tests utility helper functions.
"""

import pytest
from datetime import datetime, timedelta

from habit_tracker.utils.date_helpers import (
    get_week_start,
    get_week_end,
    is_same_week,
    days_between,
    get_date_range,
    format_date_for_display,
    format_datetime_for_display
)


@pytest.mark.unit
class TestDateHelpers:
    """Test date utility functions."""
    
    def test_get_week_start(self):
        """Test getting the start of the week."""
        # Test with a Wednesday (weekday = 2)
        wednesday = datetime(2023, 11, 15, 14, 30, 0)  # November 15, 2023 (Wednesday)
        week_start = get_week_start(wednesday)
        
        # Should return Monday November 13, 2023 at 00:00:00
        expected = datetime(2023, 11, 13, 0, 0, 0)
        assert week_start == expected
    
    def test_get_week_end(self):
        """Test getting the end of the week."""
        wednesday = datetime(2023, 11, 15, 14, 30, 0)
        week_end = get_week_end(wednesday)
        
        # Should return Sunday November 19, 2023 at 23:59:59
        expected = datetime(2023, 11, 19, 23, 59, 59)
        assert week_end == expected
    
    def test_is_same_week_true(self):
        """Test that dates in the same week return True."""
        monday = datetime(2023, 11, 13)
        friday = datetime(2023, 11, 17)
        
        assert is_same_week(monday, friday) is True
    
    def test_is_same_week_false(self):
        """Test that dates in different weeks return False."""
        this_week = datetime(2023, 11, 15)
        next_week = datetime(2023, 11, 22)
        
        assert is_same_week(this_week, next_week) is False
    
    def test_days_between(self):
        """Test calculating days between dates."""
        start = datetime(2023, 11, 10)
        end = datetime(2023, 11, 15)
        
        days = days_between(start, end)
        assert days == 5
    
    def test_days_between_same_day(self):
        """Test days between same day."""
        same_day = datetime(2023, 11, 15)
        
        days = days_between(same_day, same_day)
        assert days == 0
    
    def test_get_date_range(self):
        """Test generating a range of dates."""
        start = datetime(2023, 11, 10)
        end = datetime(2023, 11, 12)
        
        date_range = get_date_range(start, end)
        
        assert len(date_range) == 3
        assert date_range[0].date() == start.date()
        assert date_range[1].date() == (start + timedelta(days=1)).date()
        assert date_range[2].date() == end.date()
    
    def test_format_date_for_display(self):
        """Test formatting date for display."""
        test_date = datetime(2023, 11, 15, 14, 30, 0)
        
        formatted = format_date_for_display(test_date)
        assert formatted == "2023-11-15"
    
    def test_format_datetime_for_display(self):
        """Test formatting datetime for display."""
        test_datetime = datetime(2023, 11, 15, 14, 30, 0)
        
        formatted = format_datetime_for_display(test_datetime)
        assert formatted == "2023-11-15 14:30"






