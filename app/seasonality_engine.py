"""
Real Seasonality Analysis Engine
High-performance, accurate seasonality pattern detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path

from app.config import RAW_DATA_DIR, FOREX_PAIRS

logger = logging.getLogger(__name__)


class RealSeasonalityEngine:
    """
    Production-grade seasonality analysis engine
    Analyzes real OHLC data to find statistically significant seasonal patterns
    """
    
    def __init__(self):
        self.data_cache = {}
        
    def load_asset_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load OHLC data for an asset
        
        Args:
            symbol: Asset symbol (e.g., 'EURUSD=X')
            
        Returns:
            DataFrame with OHLC data or None if not found
        """
        
        if symbol in self.data_cache:
            return self.data_cache[symbol]
        
        try:
            # Handle file naming (EURUSD=X -> EURUSD_X.csv)
            clean_symbol = symbol.replace('=', '_')
            file_path = Path(RAW_DATA_DIR) / f"{clean_symbol}.csv"
            
            if not file_path.exists():
                logger.warning(f"Data file not found for {symbol}: {file_path}")
                return None
            
            # Load data properly handling timezone issues
            df = pd.read_csv(file_path)
            
            # Set up the date column properly
            df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
            df = df.set_index('Date')
            
            # Standardize column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Ensure required columns exist
            required_cols = ['open', 'high', 'low', 'close']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in {symbol} data. Available: {list(df.columns)}")
                return None
            
            # Sort by date and remove any NaN values
            df = df.sort_index().dropna(subset=required_cols)
            
            # Cache the data
            self.data_cache[symbol] = df
            
            logger.info(f"Loaded {len(df)} rows of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def calculate_returns(self, df: pd.DataFrame, period_days: int) -> pd.Series:
        """
        Calculate returns for a specific holding period
        
        Args:
            df: OHLC DataFrame
            period_days: Holding period in days
            
        Returns:
            Series of period returns
        """
        
        # Calculate period returns: (close[t+period] - close[t]) / close[t]
        close_prices = df['close']
        period_returns = close_prices.pct_change(periods=period_days).shift(-period_days)
        
        return period_returns.dropna()
    
    def find_seasonal_patterns(
        self,
        symbol: str,
        min_phase_length: int,
        max_phase_length: int,
        min_winrate: float,
        start_year: int,
        end_year: int,
        days_from_today: int
    ) -> List[Dict]:
        """
        Find seasonal patterns for a specific asset
        
        Args:
            symbol: Asset symbol
            min_phase_length: Minimum phase length in days
            max_phase_length: Maximum phase length in days
            min_winrate: Minimum acceptable win rate
            start_year: Analysis start year
            end_year: Analysis end year
            days_from_today: Only patterns starting in next X days
            
        Returns:
            List of seasonal pattern dictionaries
        """
        
        # Load data
        df = self.load_asset_data(symbol)
        if df is None:
            return []
        
        # Filter data to analysis period with validation
        original_length = len(df)
        df = df[
            (df.index.year >= start_year) & 
            (df.index.year <= end_year)
        ]
        
        # Validate sufficient data for meaningful analysis
        if len(df) < 200:  # Need at least 200 trading days (~1 year) 
            logger.warning(f"Insufficient data for {symbol}: {len(df)} days (filtered from {original_length} original)")
            return []
        
        # Validate data quality
        if df['close'].isna().sum() > len(df) * 0.1:  # More than 10% missing data
            logger.warning(f"Too much missing data for {symbol}: {df['close'].isna().sum()}/{len(df)} NaN values")
            return []
        
        patterns = []
        
        # Calculate current day of year for filtering
        today = datetime.now()
        current_day_of_year = today.timetuple().tm_yday
        
        # Define valid start days (next X days from today)
        valid_start_days = set()
        for i in range(days_from_today + 1):  # Include today (i=0)
            future_date = today + timedelta(days=i)
            day_of_year = future_date.timetuple().tm_yday
            valid_start_days.add(day_of_year)
        
        # Test different phase lengths  
        for phase_length in range(min_phase_length, max_phase_length + 1):
            
            # Test all possible start days of the year, but focus on the requested period
            search_range = list(valid_start_days)
            
            # If no patterns found in valid days, expand search to nearby days
            if not search_range:
                search_range = list(range(max(1, current_day_of_year - 10), 
                                        min(366, current_day_of_year + days_from_today + 10)))
            
            for start_day in search_range:
                
                # Analyze this specific seasonal window
                pattern_results = self._analyze_seasonal_window(
                    df, start_day, phase_length, symbol
                )
                
                if pattern_results and pattern_results['winrate'] >= min_winrate:
                    # Convert start_day to days_from_today for display using correct leap year logic
                    if start_day >= current_day_of_year:
                        days_from_today_val = start_day - current_day_of_year
                    else:
                        # Next year - use correct leap year calculation
                        current_is_leap = (today.year % 4 == 0 and today.year % 100 != 0) or (today.year % 400 == 0)
                        days_in_current_year = 366 if current_is_leap else 365
                        days_from_today_val = (days_in_current_year - current_day_of_year) + start_day
                    
                    pattern_results['start_in'] = days_from_today_val
                    patterns.append(pattern_results)
        
        # Group patterns that start on the same day and merge them
        patterns = self._merge_same_day_patterns(patterns)
        
        # Sort by winrate descending
        patterns.sort(key=lambda x: x['winrate'], reverse=True)
        
        logger.info(f"Found {len(patterns)} seasonal patterns for {symbol}")
        return patterns
    
    def _analyze_seasonal_window(
        self,
        df: pd.DataFrame,
        start_day: int,
        phase_length: int,
        symbol: str
    ) -> Optional[Dict]:
        """
        Analyze a specific seasonal window (start_day + phase_length)
        
        Args:
            df: OHLC DataFrame
            start_day: Day of year to start (1-365)
            phase_length: Length of seasonal phase in days
            symbol: Asset symbol
            
        Returns:
            Dictionary with pattern statistics or None
        """
        
        try:
            # Find all occurrences of this seasonal window across all years
            window_returns = []
            years_analyzed = set()
            
            for year in df.index.year.unique():
                year_data = df[df.index.year == year]
                
                if len(year_data) < 50:  # Skip years with insufficient data
                    continue
                
                # Find start date for this year using correct calendar calculation
                try:
                    # Proper leap year calculation
                    is_leap_year = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                    max_day = 366 if is_leap_year else 365
                    
                    if start_day > max_day:
                        continue  # Skip if day doesn't exist in this year
                    
                    # Convert day-of-year to actual date
                    start_date = pd.Timestamp(year=year, month=1, day=1) + pd.Timedelta(days=start_day-1)
                    
                    end_date = start_date + pd.Timedelta(days=phase_length-1)
                    
                    # Get data for this window - must be sorted by date
                    window_data = year_data[
                        (year_data.index >= start_date) & 
                        (year_data.index <= end_date)
                    ].sort_index()
                    
                    # Need sufficient trading days for reliable calculation
                    min_required_days = max(3, int(phase_length * 0.6))  # At least 60% of expected days
                    
                    if len(window_data) >= min_required_days:
                        # Ensure we have valid price data
                        if window_data['close'].isna().any():
                            window_data = window_data.dropna(subset=['close'])
                            if len(window_data) < min_required_days:
                                continue
                        
                        # Calculate return using first and last available trading day in period
                        start_price = window_data['close'].iloc[0]
                        end_price = window_data['close'].iloc[-1]
                        
                        # Validate prices are positive and realistic
                        if start_price <= 0 or end_price <= 0:
                            continue
                        
                        # Calculate return with additional validation
                        window_return = (end_price - start_price) / start_price
                        
                        # Filter out extreme outliers (>100% change in short period)
                        # These are likely data errors or stock splits not properly adjusted
                        if abs(window_return) > 1.0:  # More than 100% change
                            logger.warning(f"Extreme return filtered out: {window_return:.4f} for {symbol}")
                            continue
                        
                        window_returns.append(window_return)
                        years_analyzed.add(year)
                        
                except (ValueError, IndexError, KeyError):
                    # Skip invalid dates or missing data
                    continue
            
            # Need sufficient occurrences for statistical significance
            # Minimum 5 years for robust analysis, but allow 3 for initial detection
            min_required_years = 5 if len(years_analyzed) >= 5 else 3
            if len(window_returns) < min_required_years:
                return None
            
            # Calculate statistics for both Long and Short scenarios
            returns_array = np.array(window_returns)
            
            # Test both Long and Short directions to find the better one
            long_stats = self._calculate_direction_stats(returns_array, 'Long', phase_length)
            short_stats = self._calculate_direction_stats(returns_array, 'Short', phase_length)
            
            # Choose the direction with better performance (higher win rate, then higher return)
            if long_stats['winrate'] > short_stats['winrate']:
                best_stats = long_stats
                direction = 'Long'
            elif short_stats['winrate'] > long_stats['winrate']:
                best_stats = short_stats  
                direction = 'Short'
            else:
                # Same win rate, choose by average return
                if long_stats['avg_return'] >= short_stats['avg_return']:
                    best_stats = long_stats
                    direction = 'Long'
                else:
                    best_stats = short_stats
                    direction = 'Short'
            
            # Cycle analysis (simplified)
            cycle_winrate = best_stats['winrate']  # Same as overall winrate
            cycle_supported = best_stats['winrate'] >= 0.5 and len(returns_array) >= 3
            
            return {
                'asset': symbol,
                'direction': direction,
                'start_in': start_day,  # Will be converted to days_from_today later
                'length': phase_length,
                'n_years': len(years_analyzed),
                'winrate': round(best_stats['winrate'], 3),
                'avg_return': round(best_stats['avg_return'], 4),
                'sharpe_annualized': round(best_stats['sharpe_ratio'], 2),
                'cycle_winrate': round(cycle_winrate, 3),
                'cycle_supported': cycle_supported,
                'longest': best_stats['longest_streak']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing window for {symbol}: {e}")
            return None
    
    def _calculate_longest_streak(self, returns: np.ndarray) -> int:
        """
        Calculate the longest consecutive winning streak
        
        Args:
            returns: Array of returns
            
        Returns:
            Length of longest winning streak
        """
        
        if len(returns) == 0:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for ret in returns:
            if ret > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_direction_stats(self, returns_array: np.ndarray, direction: str, phase_length: int) -> Dict:
        """
        Calculate statistics for a specific trading direction (Long or Short)
        
        Args:
            returns_array: Array of raw price returns
            direction: 'Long' or 'Short'
            phase_length: Phase length for annualization
            
        Returns:
            Dictionary with direction-specific statistics
        """
        
        if direction == 'Long':
            # For Long positions, positive price returns are profitable
            trading_returns = returns_array
        else:
            # For Short positions, negative price returns are profitable
            # Invert the returns: -5% price decline = +5% Short profit
            trading_returns = -returns_array
        
        # Calculate win rate (percentage of profitable trades)
        winning_trades = np.sum(trading_returns > 0)
        total_trades = len(trading_returns)
        winrate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Average return for this direction
        avg_return = np.mean(trading_returns)
        
        # Sharpe ratio calculation
        returns_std = np.std(trading_returns, ddof=1)  # Sample standard deviation
        if returns_std > 1e-10:  # Avoid division by very small numbers
            # Annualize assuming 252 trading days per year
            annualization_factor = np.sqrt(252 / phase_length)
            sharpe_ratio = (avg_return / returns_std) * annualization_factor
            # Cap extreme values for practical interpretation
            sharpe_ratio = max(-10, min(10, sharpe_ratio))
        else:
            sharpe_ratio = 0
        
        # Longest winning streak for this direction
        longest_streak = self._calculate_longest_streak(trading_returns)
        
        return {
            'winrate': winrate,
            'avg_return': avg_return,
            'sharpe_ratio': sharpe_ratio,
            'longest_streak': longest_streak
        }
    
    def _merge_same_day_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """
        Merge patterns that start on the same day by averaging their metrics
        
        Args:
            patterns: List of pattern dictionaries
            
        Returns:
            List of merged patterns (one per start day)
        """
        from collections import defaultdict
        
        if len(patterns) <= 1:
            return patterns
        
        # Group patterns by start_in (days from today)
        grouped = defaultdict(list)
        for pattern in patterns:
            start_day = pattern['start_in']
            grouped[start_day].append(pattern)
        
        merged_patterns = []
        
        for start_day, day_patterns in grouped.items():
            if len(day_patterns) == 1:
                # No merging needed
                merged_patterns.append(day_patterns[0])
            else:
                # Merge multiple patterns for same start day
                merged = self._merge_pattern_group(day_patterns)
                merged_patterns.append(merged)
        
        return merged_patterns
    
    def _merge_pattern_group(self, patterns: List[Dict]) -> Dict:
        """
        Merge a group of patterns that start on the same day
        Uses weighted average based on number of years analyzed
        """
        if len(patterns) == 1:
            return patterns[0]
        
        # Calculate total weight (sum of all n_years)
        total_weight = sum(p['n_years'] for p in patterns)
        
        # Weighted averages for numerical values
        merged = {
            'asset': patterns[0]['asset'],
            'direction': patterns[0]['direction'],  # Use most common direction
            'start_in': patterns[0]['start_in'],    # Same for all
            'length': round(sum(p['length'] * p['n_years'] for p in patterns) / total_weight),
            'n_years': max(p['n_years'] for p in patterns),  # Use maximum years (most data available)
            'winrate': sum(p['winrate'] * p['n_years'] for p in patterns) / total_weight,
            'avg_return': sum(p['avg_return'] * p['n_years'] for p in patterns) / total_weight,
            'sharpe_annualized': sum(p['sharpe_annualized'] * p['n_years'] for p in patterns) / total_weight,
            'cycle_winrate': sum(p['cycle_winrate'] * p['n_years'] for p in patterns) / total_weight,
            'cycle_supported': any(p['cycle_supported'] for p in patterns),  # True if any supports
            'longest': max(p['longest'] for p in patterns)  # Best longest streak
        }
        
        # Determine most common direction
        directions = [p['direction'] for p in patterns]
        long_count = directions.count('Long')
        short_count = directions.count('Short')
        merged['direction'] = 'Long' if long_count >= short_count else 'Short'
        
        return merged
    
    def _deduplicate_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate patterns by keeping only the best pattern per asset and direction.
        This prevents showing the same asset multiple times with slightly different parameters.
        
        Strategy:
        1. Group by asset and direction (Long/Short)
        2. For each group, keep only the pattern with the highest score
        3. Score = (winrate * 0.6) + (sharpe_annualized * 0.3) + (avg_return * 100 * 0.1)
        
        Args:
            df: DataFrame with all patterns
            
        Returns:
            DataFrame with deduplicated patterns (max 2 per asset: 1 Long, 1 Short)
        """
        if df.empty:
            return df
        
        logger.info(f"Deduplicating {len(df)} patterns...")
        
        # Calculate composite score for ranking
        df['_score'] = (df['winrate'] * 0.6 + 
                       df['sharpe_annualized'] * 0.3 + 
                       df['avg_return'] * 100 * 0.1)
        
        # Group by asset and direction, keep best pattern for each combination
        deduplicated = []
        
        for (asset, direction), group in df.groupby(['asset', 'direction']):
            # Sort by score and take the best one
            best_pattern = group.loc[group['_score'].idxmax()]
            
            # Remove the temporary score column
            best_pattern_dict = best_pattern.to_dict()
            if '_score' in best_pattern_dict:
                del best_pattern_dict['_score']
            
            deduplicated.append(best_pattern_dict)
        
        # Convert back to DataFrame
        result_df = pd.DataFrame(deduplicated)
        
        logger.info(f"After deduplication: {len(result_df)} patterns (max 2 per asset: Long + Short)")
        
        return result_df
    
    def analyze_multiple_assets(
        self,
        assets: List[str],
        min_phase_length: int,
        max_phase_length: int,
        min_winrate: float,
        start_year: int,
        end_year: int,
        days_from_today: int,
        progress_callback=None
    ) -> pd.DataFrame:
        """
        Analyze multiple assets for seasonal patterns
        
        Args:
            assets: List of asset symbols
            min_phase_length: Minimum phase length
            max_phase_length: Maximum phase length
            min_winrate: Minimum win rate
            start_year: Analysis start year
            end_year: Analysis end year
            days_from_today: Days from today window
            progress_callback: Progress update function
            
        Returns:
            DataFrame with all found patterns
        """
        
        all_patterns = []
        
        for i, asset in enumerate(assets):
            if progress_callback:
                progress_callback(i, len(assets), f"Analyzing {asset}...")
            
            try:
                patterns = self.find_seasonal_patterns(
                    asset, min_phase_length, max_phase_length,
                    min_winrate, start_year, end_year, days_from_today
                )
                all_patterns.extend(patterns)
                
            except Exception as e:
                logger.error(f"Error analyzing {asset}: {e}")
                continue
        
        if progress_callback:
            progress_callback(len(assets), len(assets), "Analysis complete")
        
        if not all_patterns:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_patterns)
        
        # Intelligent deduplication: Keep only the best pattern per asset and direction
        df = self._deduplicate_patterns(df)
        
        # Sort by winrate and sharpe ratio
        df = df.sort_values(['winrate', 'sharpe_annualized'], ascending=[False, False])
        df = df.reset_index(drop=True)
        
        logger.info(f"Found {len(df)} total seasonal patterns across {len(assets)} assets")
        
        return df


def get_available_real_assets() -> List[str]:
    """
    Get list of assets that have real data files available
    
    Returns:
        List of asset symbols with data
    """
    
    available_assets = []
    
    try:
        data_dir = Path(RAW_DATA_DIR)
        if not data_dir.exists():
            return []
        
        # Check each forex pair
        for symbol in FOREX_PAIRS:
            clean_symbol = symbol.replace('=', '_')
            file_path = data_dir / f"{clean_symbol}.csv"
            
            if file_path.exists():
                available_assets.append(symbol)
        
        logger.info(f"Found {len(available_assets)} assets with real data")
        
    except Exception as e:
        logger.error(f"Error scanning for real assets: {e}")
    
    return available_assets