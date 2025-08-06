# Raw Data Directory

This directory contains raw OHLC (Open, High, Low, Close) data files for analysis.

📊 **Currently using demo data** - Add your real data files here to analyze actual assets!

## How to Add Real Assets

1. **Download OHLC data** for your desired assets (from Yahoo Finance, broker, etc.)
2. **Save as CSV or Parquet** with the naming convention below
3. **Restart the application** - assets will be auto-detected

## Expected File Format

### CSV Format
```
date,open,high,low,close,volume
2020-01-01,100.00,102.50,99.50,101.25,1000000
2020-01-02,101.25,103.00,100.00,102.50,1200000
...
```

### Parquet Format (Recommended for Performance)
- Same columns as CSV but in Parquet format for faster I/O
- Supports compression for smaller file sizes
- Better for large datasets (millions of rows)

## File Naming Convention
- `{SYMBOL}_daily.csv` or `{SYMBOL}_daily.parquet`
- Examples: `AAPL_daily.csv`, `SPY_daily.parquet`, `BTCUSD_daily.csv`

## Example Files
- `EXAMPLE_daily.csv` - Sample file showing the correct format

## Integration Points
- Files placed here will be **automatically detected** by the application
- The analysis engine will process all supported formats
- Large files (>100MB) should use Parquet format for better performance
- Assets appear in the sidebar dropdown immediately after adding files

## Quick Test
Try adding a file like `TEST_daily.csv` with the format above, then restart the app to see it appear in the asset list!