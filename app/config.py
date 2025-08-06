"""
Configuration module for Seasonality Trading Tool
Centralized settings and constants for the application
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import os
from datetime import datetime, timedelta

# Directory structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Time-based functions for current period analysis
def get_current_day_of_year() -> int:
    """Get current day of year (1-366)"""
    return datetime.now().timetuple().tm_yday

def get_next_10_days_range() -> Tuple[int, int]:
    """
    Get day-of-year range for next 10 days including today
    
    Returns:
        Tuple of (start_day, end_day) in day-of-year format
    """
    today = datetime.now()
    end_date = today + timedelta(days=9)  # 9 days from today = 10 days total including today
    
    start_day = today.timetuple().tm_yday
    end_day = end_date.timetuple().tm_yday
    
    # Handle year rollover (e.g., Dec 28 -> Jan 6)
    if end_day < start_day:
        # Year boundary crossed, need special handling
        # This will be handled in the analysis logic
        pass
    
    return start_day, end_day

def is_day_in_next_10_days(day_of_year: int) -> bool:
    """
    Check if a given day of year is within the next 10 days
    
    Args:
        day_of_year: Day of year (1-366)
        
    Returns:
        True if day is within next 10 days
    """
    start_day, end_day = get_next_10_days_range()
    
    # Handle normal case (no year boundary)
    if end_day >= start_day:
        return start_day <= day_of_year <= end_day
    else:
        # Handle year boundary crossing
        # Either in the end of current year OR beginning of next year
        days_in_year = 366 if datetime.now().year % 4 == 0 else 365
        return day_of_year >= start_day or day_of_year <= end_day
        
def get_formatted_next_10_days() -> str:
    """Get formatted string showing the next 10 days date range"""
    today = datetime.now()
    end_date = today + timedelta(days=9)
    return f"{today.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"

@dataclass
class AnalysisConfig:
    """Configuration for seasonality analysis parameters"""
    min_phase_length: int = 7
    max_phase_length: int = 30
    min_winrate: float = 0.75  # Updated to 75% as requested
    winrate_threshold_longest: float = 0.65  # Updated to 65% as requested
    start_year: int = 2000
    end_year: int = 2025
    
    # Performance settings
    use_vectorized_operations: bool = True
    enable_parallel_processing: bool = False  # For future implementation
    
    # Data processing
    chunk_size: int = 10000  # For large dataset processing

# Asset list - currently using dummy data for demonstration
# TODO: Replace with actual assets when real data files are added to data/raw/
DUMMY_ASSETS = [
    "DEMO_ASSET_1", "DEMO_ASSET_2", "DEMO_ASSET_3", 
    "DEMO_ASSET_4", "DEMO_ASSET_5"
]

# Standard 28 Forex pairs for Yahoo Finance download
FOREX_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "EURGBP=X",
    "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CHFJPY=X",
    "NZDJPY=X", "CADJPY=X", "EURCHF=X", "GBPCHF=X",
    "AUDCHF=X", "NZDCHF=X", "CADCHF=X", "EURAUD=X",
    "GBPAUD=X", "AUDNZD=X", "EURNZD=X", "GBPNZD=X",
    "EURCAD=X", "GBPCAD=X", "AUDCAD=X", "NZDCAD=X"
]

# Real assets will be auto-detected from data/raw/ folder when implemented
# Expected format: {SYMBOL}.csv or {SYMBOL}.parquet (e.g., EURUSD=X.csv)
SUPPORTED_ASSETS = []  # Will be populated dynamically from data files

# Data download settings
DOWNLOAD_CONFIG = {
    "max_period": "max",  # Download maximum available history
    "auto_adjust": True,  # Automatically adjust OHLC for splits/dividends
    "prepost": False,     # Don't include pre/post market data
    "threads": True,      # Use threading for faster downloads
    "group_by": "ticker", # Group results by ticker
    "progress": True      # Show download progress
}

# Analysis result columns
RESULT_COLUMNS = [
    "asset",
    "direction", 
    "start_in",  # Now represents "days from today" instead of "day of year"
    "length",
    "n_years", 
    "winrate",
    "avg_return",
    "sharpe_annualized",
    "cycle_winrate",
    "cycle_supported",
    "longest"
]

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "Seasonality Trading Tool",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Performance thresholds for large data processing
PERFORMANCE_THRESHOLDS = {
    "large_dataset_rows": 1_000_000,
    "use_polars_threshold": 100_000,
    "parallel_processing_threshold": 500_000
}

# Remote access configuration
REMOTE_CONFIG = {
    "default_port": 8501,
    "allow_remote_access": True,
    "require_authentication": True,
    "session_timeout_hours": 8,
    "max_concurrent_users": 10
}