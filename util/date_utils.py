"""Utility functions for date handling in the ArXiv paper manager."""
from datetime import datetime, timedelta
from typing import Optional

def validate_date(date_str: str) -> bool:
    """Validate if a string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> tuple[str, str]:
    """Get a valid date range, defaulting to last 7 days if not specified."""
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if not start_date:
        start = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)
        start_date = start.strftime('%Y-%m-%d')
    
    return start_date, end_date
