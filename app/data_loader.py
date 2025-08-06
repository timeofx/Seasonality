"""
Data loader module for Seasonality Trading Tool
Handles downloading and loading historical forex data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import os
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

from app.config import FOREX_PAIRS, RAW_DATA_DIR, DOWNLOAD_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForexDataLoader:
    """
    Professional data loader for forex pairs using Yahoo Finance
    Optimized for batch downloads and error handling
    """
    
    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.forex_pairs = FOREX_PAIRS
        self.download_config = DOWNLOAD_CONFIG
        
        # Ensure data directory exists
        os.makedirs(self.raw_data_dir, exist_ok=True)
    
    def check_existing_data(self, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Check if data file already exists for a symbol
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X')
            
        Returns:
            Tuple of (exists, filepath)
        """
        # Clean symbol for filename (replace = with _)
        clean_symbol = symbol.replace('=', '_')
        csv_path = os.path.join(self.raw_data_dir, f"{clean_symbol}.csv")
        parquet_path = os.path.join(self.raw_data_dir, f"{clean_symbol}.parquet")
        
        if os.path.exists(csv_path):
            return True, csv_path
        elif os.path.exists(parquet_path):
            return True, parquet_path
        else:
            return False, csv_path  # Return CSV path for new downloads
    
    def download_pair(self, symbol: str, force_download: bool = False) -> Dict[str, any]:
        """
        Download historical data for a single forex pair
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X')
            force_download: Force download even if file exists
            
        Returns:
            Dictionary with download status and info
        """
        
        result = {
            "symbol": symbol,
            "success": False,
            "message": "",
            "rows": 0,
            "date_range": "",
            "filepath": ""
        }
        
        try:
            # Check if file already exists
            exists, filepath = self.check_existing_data(symbol)
            
            if exists and not force_download:
                # Load existing file to get info
                try:
                    if filepath.endswith('.parquet'):
                        df = pd.read_parquet(filepath)
                    else:
                        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
                    
                    result.update({
                        "success": True,
                        "message": "File already exists",
                        "rows": len(df),
                        "date_range": f"{df.index.min().date()} to {df.index.max().date()}",
                        "filepath": filepath
                    })
                    return result
                    
                except Exception as e:
                    logger.warning(f"Error reading existing file for {symbol}: {e}")
                    # Continue with download if existing file is corrupted
            
            # Download data from Yahoo Finance
            logger.info(f"Downloading {symbol} from Yahoo Finance...")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                period=self.download_config["max_period"],
                auto_adjust=self.download_config["auto_adjust"],
                prepost=self.download_config["prepost"]
            )
            
            if df.empty:
                result["message"] = "No data available from Yahoo Finance"
                return result
            
            # Clean and prepare data
            df = self._clean_data(df, symbol)
            
            # Save to CSV
            clean_symbol = symbol.replace('=', '_')
            csv_filepath = os.path.join(self.raw_data_dir, f"{clean_symbol}.csv")
            
            df.to_csv(csv_filepath, float_format="%.5f")
            
            result.update({
                "success": True,
                "message": "Downloaded successfully",
                "rows": len(df),
                "date_range": f"{df.index.min().date()} to {df.index.max().date()}",
                "filepath": csv_filepath
            })
            
            logger.info(f"✅ {symbol}: {len(df)} rows saved to {csv_filepath}")
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            result["message"] = error_msg
            logger.error(f"❌ {symbol}: {error_msg}")
        
        return result
    
    def _clean_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and standardize downloaded data
        
        Args:
            df: Raw data from Yahoo Finance
            symbol: Symbol name for logging
            
        Returns:
            Cleaned DataFrame
        """
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Rename columns to lowercase for consistency
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Handle missing volume (common for forex)
        if 'volume' not in df.columns:
            df['volume'] = 0
        
        # Remove any rows with NaN values in OHLC
        initial_rows = len(df)
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        if len(df) < initial_rows:
            logger.info(f"{symbol}: Removed {initial_rows - len(df)} rows with missing OHLC data")
        
        # Ensure proper data types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort by date
        df = df.sort_index()
        
        return df
    
    def download_all_pairs(self, force_download: bool = False, progress_callback=None) -> Dict[str, any]:
        """
        Download all forex pairs with progress tracking
        
        Args:
            force_download: Force download even if files exist
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with overall download results
        """
        
        start_time = time.time()
        results = []
        successful_downloads = 0
        
        logger.info(f"Starting download of {len(self.forex_pairs)} forex pairs...")
        
        for i, symbol in enumerate(self.forex_pairs):
            # Update progress
            if progress_callback:
                progress_callback(i, len(self.forex_pairs), symbol)
            
            # Download individual pair
            result = self.download_pair(symbol, force_download)
            results.append(result)
            
            if result["success"]:
                successful_downloads += 1
            
            # Small delay to be respectful to Yahoo Finance
            time.sleep(0.1)
        
        # Final progress update
        if progress_callback:
            progress_callback(len(self.forex_pairs), len(self.forex_pairs), "Complete")
        
        duration = time.time() - start_time
        
        summary = {
            "total_pairs": len(self.forex_pairs),
            "successful": successful_downloads,
            "failed": len(self.forex_pairs) - successful_downloads,
            "duration_seconds": duration,
            "results": results
        }
        
        logger.info(f"Download complete: {successful_downloads}/{len(self.forex_pairs)} successful in {duration:.1f}s")
        
        return summary
    
    def load_pair(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load historical data for a forex pair from saved file
        
        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X')
            
        Returns:
            DataFrame with OHLC data or None if not found
        """
        
        try:
            exists, filepath = self.check_existing_data(symbol)
            
            if not exists:
                logger.warning(f"No data file found for {symbol}")
                return None
            
            # Load data based on file type
            if filepath.endswith('.parquet'):
                df = pd.read_parquet(filepath)
            else:
                df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            
            logger.info(f"Loaded {symbol}: {len(df)} rows from {filepath}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def get_available_pairs(self) -> List[str]:
        """
        Get list of forex pairs that have data files available
        
        Returns:
            List of available forex pair symbols
        """
        
        available_pairs = []
        
        try:
            if not os.path.exists(self.raw_data_dir):
                return available_pairs
            
            # Check each forex pair
            for symbol in self.forex_pairs:
                exists, _ = self.check_existing_data(symbol)
                if exists:
                    available_pairs.append(symbol)
            
            logger.info(f"Found data for {len(available_pairs)}/{len(self.forex_pairs)} forex pairs")
            
        except Exception as e:
            logger.error(f"Error scanning for available pairs: {e}")
        
        return available_pairs
    
    def get_data_summary(self) -> Dict[str, any]:
        """
        Get summary of all available data
        
        Returns:
            Dictionary with data summary statistics
        """
        
        summary = {
            "total_forex_pairs": len(self.forex_pairs),
            "available_pairs": 0,
            "total_rows": 0,
            "date_range": {"min": None, "max": None},
            "pairs_info": []
        }
        
        try:
            for symbol in self.forex_pairs:
                exists, filepath = self.check_existing_data(symbol)
                
                if exists:
                    try:
                        # Load basic info without full data
                        if filepath.endswith('.parquet'):
                            df = pd.read_parquet(filepath)
                        else:
                            df = pd.read_csv(filepath, index_col=0, parse_dates=True, nrows=1)
                            # Get actual row count
                            with open(filepath, 'r') as f:
                                row_count = sum(1 for line in f) - 1  # Subtract header
                        
                        if not filepath.endswith('.parquet'):
                            # Load date range info
                            df_full = pd.read_csv(filepath, index_col=0, parse_dates=True)
                            min_date = df_full.index.min()
                            max_date = df_full.index.max()
                            row_count = len(df_full)
                        else:
                            min_date = df.index.min()
                            max_date = df.index.max()
                            row_count = len(df)
                        
                        summary["available_pairs"] += 1
                        summary["total_rows"] += row_count
                        
                        # Update overall date range
                        if summary["date_range"]["min"] is None or min_date < summary["date_range"]["min"]:
                            summary["date_range"]["min"] = min_date
                        if summary["date_range"]["max"] is None or max_date > summary["date_range"]["max"]:
                            summary["date_range"]["max"] = max_date
                        
                        summary["pairs_info"].append({
                            "symbol": symbol,
                            "rows": row_count,
                            "start_date": min_date.date(),
                            "end_date": max_date.date()
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error reading summary for {symbol}: {e}")
            
        except Exception as e:
            logger.error(f"Error generating data summary: {e}")
        
        return summary


# Convenience functions for easy access
def download_all_forex_data(force_download: bool = False, progress_callback=None) -> Dict[str, any]:
    """
    Convenience function to download all forex data
    
    Args:
        force_download: Force download even if files exist
        progress_callback: Optional progress callback
        
    Returns:
        Download summary
    """
    loader = ForexDataLoader()
    return loader.download_all_pairs(force_download, progress_callback)


def load_forex_pair(symbol: str) -> Optional[pd.DataFrame]:
    """
    Convenience function to load a forex pair
    
    Args:
        symbol: Forex pair symbol
        
    Returns:
        DataFrame or None
    """
    loader = ForexDataLoader()
    return loader.load_pair(symbol)


def get_available_forex_pairs() -> List[str]:
    """
    Convenience function to get available forex pairs
    
    Returns:
        List of available symbols
    """
    loader = ForexDataLoader()
    return loader.get_available_pairs()