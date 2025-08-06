"""
Data models and core analysis logic for Seasonality Trading Tool
Optimized for performance with large datasets
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, date
import random

from app.config import RESULT_COLUMNS, DUMMY_ASSETS, RAW_DATA_DIR, FOREX_PAIRS, is_day_in_next_10_days
from app.seasonality_engine import RealSeasonalityEngine, get_available_real_assets


@dataclass
class SeasonalPhase:
    """Data model for a seasonal trading phase"""
    asset: str
    direction: str  # "Long" or "Short"
    start_in: int  # Days from year start
    length: int  # Phase length in days
    n_years: int  # Number of years analyzed
    winrate: float  # Win rate (0-1)
    avg_return: float  # Average return
    sharpe_annualized: float  # Annualized Sharpe ratio
    cycle_winrate: float  # Cycle win rate
    cycle_supported: bool  # Whether cycle is supported
    longest: int  # Longest winning streak


class SeasonalityAnalyzer:
    """
    Core analysis engine for seasonality patterns
    Designed for high performance with vectorized operations
    """
    
    def __init__(self, use_dummy_data: bool = None):
        # Auto-detect if we should use dummy data based on available real data
        if use_dummy_data is None:
            available_real_assets = get_available_real_assets()
            self.use_dummy_data = len(available_real_assets) == 0
        else:
            self.use_dummy_data = use_dummy_data
        
        self.real_engine = RealSeasonalityEngine()
    
    @staticmethod
    def get_available_assets() -> List[str]:
        """
        Get list of available assets for analysis
        Returns real assets if available, otherwise dummy assets
        """
        try:
            # Check for real data first
            real_assets = get_available_real_assets()
            
            if real_assets:
                print(f"Found {len(real_assets)} real data files: {real_assets}")
                return sorted(real_assets)
            else:
                print("No real data files found, using demo assets")
                return DUMMY_ASSETS
                
        except Exception as e:
            print(f"Error scanning for data files: {e}")
            return DUMMY_ASSETS
        
    def analyze_assets(
        self,
        assets: List[str],
        start_period: int,
        min_phase_length: int,
        min_winrate: float,
        winrate_threshold_longest: float,
        start_year: int,
        end_year: int,
        days_from_today: int = 10,
        max_phase_length: int = 30
    ) -> pd.DataFrame:
        """
        Main analysis function - currently generates dummy data
        Future: Will process real OHLC data with vectorized operations
        
        Args:
            assets: List of asset symbols to analyze
            start_period: Starting period in days
            min_phase_length: Minimum phase length
            min_winrate: Minimum acceptable win rate
            winrate_threshold_longest: Threshold for longest calculation
            start_year: Analysis start year
            end_year: Analysis end year
            
        Returns:
            DataFrame with analysis results
        """
        
        if self.use_dummy_data:
            return self._generate_dummy_results(
                assets, start_period, min_phase_length, min_winrate,
                winrate_threshold_longest, start_year, end_year,
                days_from_today, max_phase_length
            )
        else:
            # Use real seasonality analysis engine
            return self.real_engine.analyze_multiple_assets(
                assets=assets,
                min_phase_length=min_phase_length,
                max_phase_length=max_phase_length,
                min_winrate=min_winrate,
                start_year=start_year,
                end_year=end_year,
                days_from_today=days_from_today
            )
    
    def _generate_dummy_results(
        self,
        assets: List[str],
        start_period: int,
        min_phase_length: int,
        min_winrate: float,
        winrate_threshold_longest: float,
        start_year: int,
        end_year: int,
        days_from_today: int = 10,
        max_phase_length: int = 30
    ) -> pd.DataFrame:
        """
        Generate realistic dummy data for testing
        Simulates the output structure of real seasonality analysis
        """
        
        results = []
        n_years = end_year - start_year
        
        # Generate phases that start within the next X days from today
        from datetime import datetime, timedelta
        
        today = datetime.now()
        current_day_of_year = today.timetuple().tm_yday
        
        # Calculate valid start days (days from today converted to day-of-year)
        valid_start_days = []
        for i in range(days_from_today):
            future_date = today + timedelta(days=i)
            day_of_year = future_date.timetuple().tm_yday
            valid_start_days.append(day_of_year)
        
        # Generate 1-3 seasonal phases per asset that start within the valid window
        for asset in assets:
            num_phases = random.randint(1, 3)  # Fewer phases since we're filtering strictly
            
            for _ in range(num_phases):
                # Generate realistic parameters
                direction = random.choice(["Long", "Short"])
                
                # Start day must be within the next X days
                start_in = random.choice(valid_start_days)
                
                # Phase length between min and max
                length = random.randint(min_phase_length, max_phase_length)
                
                # Generate correlated metrics (higher winrate -> better metrics)
                # Ensure we have a good mix of results above and below the threshold
                base_winrate = random.uniform(min_winrate * 0.8, 0.95)  # Some below threshold for variety
                winrate = round(base_winrate, 3)
                
                # Correlate returns with winrate
                avg_return = round(random.uniform(0.005, 0.08) * (winrate / 0.7), 4)
                
                # Sharpe ratio correlated with winrate and returns
                sharpe_base = (winrate - 0.5) * 4 + (avg_return * 20)
                sharpe_annualized = round(max(0.1, sharpe_base + random.uniform(-0.5, 0.5)), 2)
                
                # Cycle metrics
                cycle_winrate = round(min(1.0, winrate + random.uniform(-0.1, 0.1)), 3)
                cycle_supported = winrate >= 0.65
                
                # Longest streak based on winrate threshold
                if winrate >= winrate_threshold_longest:
                    longest = length + random.randint(3, 15)
                else:
                    longest = length + random.randint(0, 8)
                
                phase = SeasonalPhase(
                    asset=asset,
                    direction=direction,
                    start_in=start_in,
                    length=length,
                    n_years=n_years,
                    winrate=winrate,
                    avg_return=avg_return,
                    sharpe_annualized=sharpe_annualized,
                    cycle_winrate=cycle_winrate,
                    cycle_supported=cycle_supported,
                    longest=longest
                )
                
                results.append(phase)
        
        # Convert to DataFrame for efficient processing
        df = pd.DataFrame([
            {
                "asset": p.asset,
                "direction": p.direction,
                "start_in": p.start_in,
                "length": p.length,
                "n_years": p.n_years,
                "winrate": p.winrate,
                "avg_return": p.avg_return,
                "sharpe_annualized": p.sharpe_annualized,
                "cycle_winrate": p.cycle_winrate,
                "cycle_supported": p.cycle_supported,
                "longest": p.longest
            }
            for p in results
        ])
        
        # Filter to only show phases that start within the specified days from today
        if not df.empty:
            # Convert start_in (day of year) to days from today
            from datetime import datetime, timedelta
            
            today = datetime.now()
            current_day_of_year = today.timetuple().tm_yday
            
            def days_from_today_calc(start_day_of_year):
                """Calculate how many days from today a pattern starts"""
                if start_day_of_year >= current_day_of_year:
                    # Same year
                    return start_day_of_year - current_day_of_year
                else:
                    # Next year (year boundary)
                    days_in_year = 366 if today.year % 4 == 0 else 365
                    return (days_in_year - current_day_of_year) + start_day_of_year
            
            df['days_from_today'] = df['start_in'].apply(days_from_today_calc)
            
            # Only keep patterns that start within the specified window
            df = df[df['days_from_today'] <= days_from_today]
            
            # Update start_in to show days from today instead of day of year
            df['start_in'] = df['days_from_today']
            df = df.drop('days_from_today', axis=1)
        
        # Sort by winrate descending for better presentation
        df = df.sort_values(['winrate', 'sharpe_annualized'], ascending=[False, False])
        df = df.reset_index(drop=True)
        
        return df
    
    def _analyze_real_data(self, assets: List[str], start_year: int, end_year: int) -> pd.DataFrame:
        """
        Placeholder for real data analysis
        Will implement vectorized seasonality calculations
        """
        # TODO: Implement real data analysis
        # Key components:
        # 1. Load OHLC data efficiently (pandas/polars)
        # 2. Calculate returns for all possible seasonal windows
        # 3. Vectorized win rate calculations
        # 4. Statistical significance testing
        # 5. Performance metrics (Sharpe, etc.)
        
        print("Real data analysis not yet implemented. Using dummy data.")
        return self._generate_dummy_results(assets, 0, 7, 0.6, 0.7, start_year, end_year)


class DataExporter:
    """
    Handles data export functionality
    Optimized for large datasets with proper formatting
    """
    
    @staticmethod
    def export_to_csv(
        df: pd.DataFrame, 
        filename: str, 
        export_dir: str
    ) -> str:
        """
        Export DataFrame to CSV with proper formatting
        
        Args:
            df: DataFrame to export
            filename: Base filename (without extension)
            export_dir: Export directory path
            
        Returns:
            Full path to exported file
        """
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.csv"
        filepath = os.path.join(export_dir, full_filename)
        
        # Export with proper formatting
        df.to_csv(
            filepath,
            index=False,
            float_format="%.4f",
            encoding="utf-8"
        )
        
        return filepath
    
    @staticmethod
    def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """
        Format DataFrame for better display in Streamlit
        """
        
        df_display = df.copy()
        
        # Format percentage columns
        percentage_cols = ['winrate', 'cycle_winrate']
        for col in percentage_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{x:.1%}")
        
        # Format return column
        if 'avg_return' in df_display.columns:
            df_display['avg_return'] = df_display['avg_return'].apply(lambda x: f"{x:.2%}")
        
        # Format Sharpe ratio
        if 'sharpe_annualized' in df_display.columns:
            df_display['sharpe_annualized'] = df_display['sharpe_annualized'].apply(lambda x: f"{x:.2f}")
        
        return df_display


import os  # Add missing import