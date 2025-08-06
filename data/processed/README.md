# Processed Data Directory

This directory contains cleaned and processed data files ready for analysis.

## Contents
- Cleaned OHLC data with proper date indexing
- Pre-calculated returns and indicators
- Cached analysis results for faster re-runs

## File Types
- `{SYMBOL}_cleaned.parquet` - Cleaned OHLC data
- `{SYMBOL}_returns.parquet` - Pre-calculated returns
- `seasonality_cache_{hash}.parquet` - Cached analysis results

## Performance Notes
- Files here are optimized for fast loading
- Use Parquet format for better compression and speed
- Cached results significantly improve analysis performance for repeated runs