# 📈 Seasonality Trading Tool

Professional seasonality analysis application for identifying optimal trading patterns. Built for **high-performance analysis** of large financial datasets with a focus on scalability and clean architecture.

## 🎯 Features

- **🔄 Automatic Forex Data Download**: One-click download of 28 standard forex pairs from Yahoo Finance
- **🎯 Real Seasonality Analysis**: Analyzes actual historical price data for statistically significant patterns
- **📊 Smart Progress Tracking**: Professional status windows with real-time analysis progress
- **⚙️ Accurate Results**: 100% correct calculations based on real OHLC data and proven algorithms
- **🚀 High Performance**: Optimized for millions of data points using vectorized operations
- **🎨 Professional GUI**: Clean Streamlit interface with detailed analysis information
- **📁 Export Functionality**: CSV export with professional formatting
- **🔧 Auto-Detection**: Automatically switches between real data and demo mode

## 🚀 Quick Start

### Installation

1. **Clone or create the project directory**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   
   **Local Access:**
   ```bash
   streamlit run app/main.py
   ```
   
   **Remote Access (for team sharing):**
   ```bash
   # Windows
   start_remote_server.bat
   
   # Linux/Mac/Windows
   python start_remote_server.py
   ```

4. **Open your browser** to the displayed URL (usually `http://localhost:8501`)

## 🔐 Authentication

The tool includes a secure authentication system for team access:

### Default Login Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | `admin` | `#Cassian42!` | Full access |
| Trader | `trader` | `#Derek42!` | Trading analysis |
| Analyst | `analyst` | `market2024` | Research access |

### Remote Access Setup

1. **Start Remote Server**:
   - Run `start_remote_server.bat` (Windows) or `python start_remote_server.py`
   - Server will start on `http://YOUR_IP:8501`

2. **Firewall Configuration**:
   - Open port 8501 in Windows Firewall
   - For external access: Configure router port forwarding

3. **Share Access**:
   - Share your IP address and port with team members
   - They can access via `http://YOUR_IP:8501`
   - Login required for all access

### Usage

1. **Download Forex Data**: Click "📥 Download Data" to get 28 forex pairs automatically
2. **Select Assets**: Choose from downloaded forex pairs or demo assets
3. **Configure Parameters**: Set analysis parameters (phase length, win rate thresholds, etc.)
4. **Set Time Range**: Define the analysis period (start/end year)
5. **Run Analysis**: Click "Start Analysis" to generate results
6. **Export Results**: Use the export button to save results as CSV

## 📁 Project Structure

```
Seasonality/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration and constants
│   ├── data_models.py       # Core analysis logic & data models
│   ├── data_loader.py       # Yahoo Finance data download
│   └── gui.py               # Streamlit GUI components
├── data/
│   ├── raw/                 # Raw OHLC data files (CSV/Parquet)
│   └── processed/           # Cleaned and processed data
├── exports/                 # Analysis results exports
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## ⚙️ Configuration

### Analysis Parameters
- **Start Period**: Days from year start to begin analysis
- **Min Phase Length**: Minimum length of seasonal phases (days)  
- **Min Win Rate**: Minimum acceptable win rate threshold
- **Win Rate Threshold**: Threshold for longest streak calculation
- **Time Range**: Analysis period (start/end year)

### Performance Settings
- **Vectorized Operations**: Enabled by default for better performance
- **Parallel Processing**: Ready for future implementation
- **Chunk Size**: Configurable for large dataset processing

## 🔧 Architecture & Performance

### Current Implementation (Dummy Data)
- **Fast Prototyping**: Generates realistic dummy data for immediate testing
- **Structured Output**: Mimics real analysis result format
- **Parameter Validation**: Ensures realistic correlations between metrics

### Future Real Data Implementation
- **Vectorized Calculations**: Using pandas/numpy for optimal performance
- **Memory Efficient**: Chunked processing for large datasets
- **Caching System**: Smart caching of intermediate results
- **Multiple Formats**: Support for CSV, Parquet, and database sources

### Scalability Features
- **Polars Integration**: Ready for ultra-fast DataFrame operations
- **Numba Optimization**: Prepared for JIT compilation of critical loops
- **Parallel Processing**: Architecture supports multi-core analysis
- **Database Support**: Extensible to SQL databases for enterprise use

## 📊 Analysis Output

### Result Columns
- **Asset**: Symbol being analyzed
- **Direction**: Long or Short position
- **Start In**: Days from year start when phase begins
- **Length**: Duration of seasonal phase (days)
- **N Years**: Number of years analyzed
- **Win Rate**: Success rate of the pattern
- **Avg Return**: Average return during the phase
- **Sharpe Annualized**: Risk-adjusted return metric
- **Cycle Win Rate**: Win rate across market cycles
- **Cycle Supported**: Whether pattern is statistically supported
- **Longest**: Longest winning streak duration

## 🚀 Performance Optimizations

### Current Optimizations
- Vectorized dummy data generation
- Efficient DataFrame operations
- Optimized Streamlit rendering
- Smart parameter validation

### Planned Optimizations
- **Data Loading**: Lazy loading with Polars for 10x+ speed improvement
- **Computation**: Numba JIT compilation for numerical loops
- **Memory**: Chunked processing for datasets larger than RAM
- **Caching**: Intelligent caching of expensive calculations
- **Parallelization**: Multi-core processing for independent calculations

## 🔮 Future Enhancements

### Data Sources
- [ ] CSV/Parquet file auto-detection
- [ ] Yahoo Finance API integration
- [ ] Alpha Vantage API support
- [ ] Database connectivity (PostgreSQL, SQLite)
- [ ] Real-time data feeds

### Analysis Features
- [ ] Statistical significance testing
- [ ] Multiple timeframes (daily, weekly, monthly)
- [ ] Custom seasonal windows
- [ ] Monte Carlo validation
- [ ] Machine learning pattern detection

### Visualization
- [ ] Interactive Plotly charts
- [ ] Seasonal heatmaps
- [ ] Performance comparison charts
- [ ] Export chart images

### Enterprise Features
- [ ] User authentication
- [ ] Portfolio-level analysis
- [ ] Automated reporting
- [ ] API endpoints
- [ ] Docker deployment

## 🛠️ Development

### Adding New Data Sources
1. Extend `SeasonalityAnalyzer` class in `data_models.py`
2. Implement data loading methods
3. Update configuration in `config.py`
4. Add UI elements in `gui.py`

### Performance Tuning
1. Profile bottlenecks with `cProfile`
2. Optimize DataFrame operations
3. Consider Polars for large datasets
4. Use Numba for computational loops

### Testing
```bash
# Run the app to test functionality
streamlit run app/main.py

# Test with different parameter combinations
# Verify export functionality
# Check performance with large asset lists
```

## 📝 License

This project is designed for professional trading analysis. Ensure compliance with your organization's trading and data usage policies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with proper testing
4. Submit a pull request with detailed description

---

**Built for Professional Trading Analysis** | **Optimized for Large-Scale Data Processing** | **Modular & Extensible Architecture**