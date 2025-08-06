# 🚀 Quick Start Guide

## Option 1: Windows Batch File (Recommended for Windows)

**Simply double-click this file:**
```
start_seasonality_tool.bat
```

This will:
1. ✅ Check Python installation
2. 📦 Install/update requirements automatically  
3. 🌐 Start the Streamlit application
4. 🔗 Open your browser automatically to http://localhost:8501

## Option 2: Python Script (Cross-Platform)

**Double-click or run:**
```
start_seasonality_tool.py
```

This Python script works on Windows, Mac, and Linux and provides better error handling.

## Option 3: Manual Start (If above don't work)

**Open Command Prompt/PowerShell in the project folder and run:**

```bash
# Install requirements (first time only)
pip install -r requirements.txt

# Start the application
python -m streamlit run app/main.py
```

Then open http://localhost:8501 in your browser.

## 🔧 Troubleshooting

### "streamlit command not found"
- Use: `python -m streamlit run app/main.py` instead
- Or try the .bat/.py starter files above

### Python not found
- Install Python 3.8+ from https://python.org
- Make sure "Add Python to PATH" is checked during installation

### Port already in use
- Close any existing Streamlit applications
- Or change the port in the starter files: `--server.port=8502`

### Permission errors
- Run Command Prompt as Administrator (Windows)
- Or use `sudo` on Mac/Linux

## 📱 Using the App

### Demo Mode (Current)
1. **All assets are pre-selected** in the sidebar (DEMO_ASSET_1, DEMO_ASSET_2, etc.)
2. **Time-focused analysis** for immediate trading opportunities:
   - **Days from Today**: Next 10 days (adjustable 1-90 days)
   - **Phase Length**: 7-30 days (min-max range)
   - **Time Range**: 2000-2025 (25 years of data)
3. **Quality parameters** optimized for best results:
   - **Minimum Win Rate**: 75%
   - **Win Rate Threshold**: 65%  
4. **Results show**:
   - **"Start in X days"**: How many days from today the pattern starts
   - **Only relevant patterns**: Within your specified timeframe
5. **Click "Start Analysis"** 
6. **View Results** - only patterns starting in next X days
7. **Export to CSV** using the export button

### Automatic Forex Data Download ⭐
**NEW FEATURE**: Automatic download of 28 standard forex pairs!

1. **Click "📥 Download Data"** in the sidebar
2. **Wait for download** - progress bar shows status
3. **Select forex pairs** from dropdown automatically
4. **Start analysis** with real historical data!

**Forex pairs included:**
- Major pairs: EURUSD, GBPUSD, USDJPY, USDCHF, etc.
- Cross pairs: EURGBP, EURJPY, GBPJPY, etc.
- Minor pairs: AUDNZD, EURNZD, GBPNZD, etc.

### Manual Data Addition
To add custom assets:
1. **Add OHLC data files** to the `data/raw/` folder
2. **Use naming format**: `SYMBOL_daily.csv` (e.g., `AAPL_daily.csv`)
3. **Restart the app** - assets will appear automatically

**CSV format:**
```
date,open,high,low,close,volume
2020-01-01,100.00,102.50,99.50,101.25,1000000
2020-01-02,101.25,103.00,100.00,102.50,1200000
```

Results will be saved in the `exports/` folder with timestamp.

---

**Need help?** Check the full README.md for detailed documentation.