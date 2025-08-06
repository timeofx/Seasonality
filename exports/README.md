# Exports Directory

This directory contains exported analysis results and reports.

## Export Types
- `seasonality_analysis_YYYYMMDD_HHMMSS.csv` - Main analysis results
- `summary_report_YYYYMMDD_HHMMSS.csv` - Summary statistics
- `charts_export_YYYYMMDD_HHMMSS/` - Exported chart images (future feature)

## File Format
CSV files with proper formatting:
- Percentages displayed as readable format (e.g., "65.2%")
- Timestamps in ISO format
- UTF-8 encoding for international compatibility

## Automated Cleanup
- Files older than 30 days may be automatically archived
- Large export files can be compressed for storage