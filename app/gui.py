"""
Streamlit GUI for Seasonality Trading Tool
Professional interface with performance considerations
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os

from app.config import (
    STREAMLIT_CONFIG, EXPORT_DIR, AnalysisConfig, FOREX_PAIRS,
    get_current_day_of_year, get_next_10_days_range, get_formatted_next_10_days
)
from app.data_models import SeasonalityAnalyzer, DataExporter
from app.data_loader import ForexDataLoader, download_all_forex_data
from app.auth import check_admin_permission, require_admin
from datetime import datetime


class SeasonalityGUI:
    """
    Main GUI class for the Seasonality Trading Tool
    Handles all Streamlit interface components
    """
    
    def __init__(self):
        self.analyzer = SeasonalityAnalyzer()  # Auto-detect real vs dummy data
        self.exporter = DataExporter()
        self.data_loader = ForexDataLoader()
        self._setup_page_config()
        
    def _setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(**STREAMLIT_CONFIG)
        
    def render_sidebar(self) -> Dict[str, Any]:
        """
        Render sidebar with all analysis parameters
        
        Returns:
            Dictionary with all user-selected parameters
        """
        
        st.sidebar.title("📈 Seasonality Analysis")
        st.sidebar.markdown("---")
        
        # Asset selection
        st.sidebar.subheader("Asset Selection")
        
        # Get available assets dynamically
        available_assets = SeasonalityAnalyzer.get_available_assets()
        
        # Show info about data source
        if "DEMO_" in str(available_assets[0]):
            st.sidebar.info("📊 **Demo Mode**: Using sample assets for demonstration. Add real OHLC files to `data/raw/` folder (format: `SYMBOL_daily.csv`) to analyze real assets.")
        else:
            st.sidebar.success(f"📈 **Real Data Mode**: Found {len(available_assets)} data files!")
        
        selected_assets = st.sidebar.multiselect(
            "Select Assets to Analyze",
            options=available_assets,
            default=available_assets,  # Select all assets by default
            help="Choose assets for seasonality analysis"
        )
        
        st.sidebar.markdown("---")
        
        # Analysis parameters
        st.sidebar.subheader("Analysis Parameters")
        
        # Days from today input
        days_from_today = st.sidebar.number_input(
            "Days from Today (Period Start Window)",
            min_value=1,
            max_value=90,
            value=10,  # Default to next 10 days
            help="Show patterns that start within the next X days from today"
        )
        
        # Calculate and show the date range
        from datetime import datetime, timedelta
        today = datetime.now()
        end_date = today + timedelta(days=days_from_today)
        date_range_text = f"{today.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"
        
        st.sidebar.info(f"🗓️ **Focus Period**\n\n📅 {date_range_text}\n\n🎯 Next {days_from_today} days from today")
        
        # Convert to start_period for backward compatibility with analysis
        current_day = get_current_day_of_year()
        start_period = current_day
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            min_phase_length = st.number_input(
                "Min Phase Length",
                min_value=1,
                max_value=365,
                value=7,
                help="Minimum length of phases"
            )
        
        with col2:
            max_phase_length = st.number_input(
                "Max Phase Length", 
                min_value=1,
                max_value=365,
                value=30,
                help="Maximum length of phases"
            )
        
        # Ensure max >= min
        if max_phase_length < min_phase_length:
            max_phase_length = min_phase_length
        
        min_winrate = st.sidebar.slider(
            "Minimum Win Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.75,  # Set to 75% as requested
            step=0.05,
            format="%.2f",
            help="Minimum acceptable win rate for phases"
        )
        
        winrate_threshold_longest = st.sidebar.slider(
            "Win Rate Threshold for Longest",
            min_value=0.0,
            max_value=1.0,
            value=0.65,  # Set to 65% as requested
            step=0.05,
            format="%.2f",
            help="Win rate threshold for longest streak calculation"
        )
        
        # Pattern Deduplication Settings
        st.sidebar.markdown("### 🔄 Pattern Deduplication")
        
        deduplicate_patterns = st.sidebar.checkbox(
            "Remove Duplicate Assets",
            value=True,
            help="Show max 1 Long + 1 Short pattern per asset (recommended)"
        )
        
        if not deduplicate_patterns:
            st.sidebar.warning("⚠️ May show many similar patterns for same asset")
        
        st.sidebar.markdown("---")
        
        # Time range
        st.sidebar.subheader("Analysis Time Range")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_year = st.number_input(
                "Start Year",
                min_value=1990,
                max_value=2030,
                value=2000,  # Default to 2000
                step=1
            )
        
        with col2:
            end_year = st.number_input(
                "End Year",
                min_value=2000,
                max_value=2030,
                value=2025,  # Default to 2025
                step=1
            )
        
        st.sidebar.markdown("---")
        
        # Data Management Section
        st.sidebar.subheader("📊 Data Management")
        
        # Show current data status
        data_summary = self.data_loader.get_data_summary()
        if data_summary["available_pairs"] > 0:
            st.sidebar.success(f"✅ {data_summary['available_pairs']}/{data_summary['total_forex_pairs']} Forex pairs available")
            with st.sidebar.expander("📈 Data Overview", expanded=False):
                st.write(f"**Total Data Points:** {data_summary['total_rows']:,}")
                if data_summary['date_range']['min']:
                    st.write(f"**Date Range:** {data_summary['date_range']['min'].date()} to {data_summary['date_range']['max'].date()}")
        else:
            st.sidebar.warning("⚠️ No forex data available")
        
        # Download controls (Admin only)
        if require_admin():
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                download_button = st.button(
                    "📥 Download Data",
                    type="secondary",
                    use_container_width=True,
                    help="Download all 28 forex pairs from Yahoo Finance"
                )
            
            with col2:
                force_download = st.checkbox(
                    "Force Update",
                    help="Re-download even if data exists"
                )
        else:
            download_button = False
            force_download = False
            st.sidebar.info("🔒 Data download requires admin privileges")
        
        st.sidebar.markdown("---")
        
        # Analysis button
        analyze_button = st.sidebar.button(
            "🚀 Start Analysis",
            type="primary",
            use_container_width=True,
            help="Begin seasonality analysis with selected parameters"
        )
        
        return {
            "selected_assets": selected_assets,
            "start_period": start_period,
            "days_from_today": days_from_today,
            "min_phase_length": min_phase_length,
            "max_phase_length": max_phase_length,
            "min_winrate": min_winrate,
            "winrate_threshold_longest": winrate_threshold_longest,
            "start_year": start_year,
            "end_year": end_year,
            "deduplicate_patterns": deduplicate_patterns,
            "analyze_button": analyze_button,
            "download_button": download_button,
            "force_download": force_download
        }
    
    def render_main_content(self, params: Dict[str, Any]):
        """
        Render main content area with results
        
        Args:
            params: Dictionary with analysis parameters from sidebar
        """
        
        # Header
        st.title("🔄 Seasonality Trading Tool")
        st.markdown(
            """
            Professional tool for analyzing seasonal trading patterns. 
            Built for **high-performance analysis** of large datasets.
            """
        )
        
        # Show current analysis focus
        days_from_today = params.get('days_from_today', 10)
        min_phase = params.get('min_phase_length', 7)
        max_phase = params.get('max_phase_length', 30)
        
        # Calculate date range
        from datetime import datetime, timedelta
        today = datetime.now()
        end_date = today + timedelta(days=days_from_today)
        date_range_text = f"{today.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"
        
        focus_text = f"🎯 **Focus**: Next {days_from_today} days ({date_range_text}) | 📊 **Phases**: {min_phase}-{max_phase} days | **Quality**: 75%+ win rate"
        
        st.info(focus_text)
        
        # Show data mode info
        available_assets = SeasonalityAnalyzer.get_available_assets()
        if "DEMO_" in str(available_assets[0]):
            with st.expander("🚀 How to Add Real Asset Data", expanded=False):
                st.markdown(
                    """
                    **Currently in Demo Mode** - To analyze real assets:
                    
                    1. **Click "📥 Download Data"** in sidebar for automatic forex data
                    2. **Or manually add OHLC files** to `data/raw/` folder 
                    3. **Use naming format**: `SYMBOL_daily.csv` (e.g., `AAPL_daily.csv`)
                    4. **Restart the app** - real assets will appear automatically
                    
                    **CSV Format:**
                    ```
                    date,open,high,low,close,volume
                    2020-01-01,100.00,102.50,99.50,101.25,1000000
                    2020-01-02,101.25,103.00,100.00,102.50,1200000
                    ```
                    
                    **Data Sources:** Yahoo Finance (auto), Alpha Vantage, your broker, etc.
                    """
                )
        else:
            data_summary = self.data_loader.get_data_summary()
            st.success(f"✅ **Real Data Mode**: Analyzing {len(available_assets)} forex pairs with {data_summary['total_rows']:,} historical data points!")
            with st.expander("📊 Data Summary", expanded=False):
                if data_summary['date_range']['min']:
                    st.write(f"**Date Range:** {data_summary['date_range']['min'].date()} to {data_summary['date_range']['max'].date()}")
                    st.write(f"**Available Pairs:** {', '.join(available_assets[:10])}{'...' if len(available_assets) > 10 else ''}")
                    st.write(f"**Total Data Points:** {data_summary['total_rows']:,} price records")
        
        # Show selected parameters
        if params["selected_assets"]:
            with st.expander("📋 Current Analysis Parameters", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Selected Assets", len(params["selected_assets"]))
                    st.metric("Days from Today", f"{params['days_from_today']} days")
                
                with col2:
                    st.metric("Phase Length", f"{params['min_phase_length']}-{params['max_phase_length']} days")
                    st.metric("Min Win Rate", f"{params['min_winrate']:.1%}")
                
                with col3:
                    st.metric("Analysis Years", f"{params['start_year']}-{params['end_year']}")
                    st.metric("Longest Threshold", f"{params['winrate_threshold_longest']:.1%}")
        
        # Handle data download
        if params["download_button"]:
            self._run_data_download(params["force_download"])
            return  # Refresh page after download
        
        # Main analysis section
        if not params["selected_assets"]:
            st.warning("⚠️ Please select at least one asset to analyze.")
            return
        
        if params["analyze_button"]:
            self._run_analysis(params)
        else:
            # Show placeholder when no analysis has been run
            st.info("👆 Configure your parameters in the sidebar and click **Start Analysis** to begin.")
            
            # Show example of what results will look like
            st.subheader("📊 Expected Results Format")
            
            # Create a sample showing patterns starting in next X days
            days_from_today = params.get('days_from_today', 10)
            min_phase = params.get('min_phase_length', 7)
            max_phase = params.get('max_phase_length', 30)
            
            # Generate sample patterns that start within the timeframe
            sample_start_1 = 2  # Starts in 2 days
            sample_start_2 = min(days_from_today - 1, 7)  # Starts in 7 days (or max days-1)
            
            sample_data = {
                "asset": ["DEMO_ASSET_1", "DEMO_ASSET_2"],
                "direction": ["Long", "Short"],
                "start_in": [sample_start_1, sample_start_2],
                "length": [15, 30],
                "n_years": [25, 25],  # Updated to reflect 2000-2025 range
                "winrate": [0.857, 0.786],  # Both above 75% threshold
                "avg_return": [0.0324, 0.0198],
                "sharpe_annualized": [2.14, 1.67],
                "cycle_winrate": [0.900, 0.820],
                "cycle_supported": [True, True],
                "longest": [28, 42]
            }
            
            sample_df = pd.DataFrame(sample_data)
            formatted_sample = self.exporter.format_for_display(sample_df)
            
            st.dataframe(
                formatted_sample,
                use_container_width=True,
                hide_index=True
            )
    
    def _run_analysis(self, params: Dict[str, Any]):
        """
        Execute the seasonality analysis with professional progress tracking
        
        Args:
            params: Analysis parameters
        """
        
        # Determine if using real data
        available_real_assets = []
        try:
            from app.seasonality_engine import get_available_real_assets
            available_real_assets = get_available_real_assets()
        except:
            pass
        
        using_real_data = len(available_real_assets) > 0
        
        # Status display
        st.subheader("🔍 Running Seasonality Analysis")
        
        if using_real_data:
            st.success("✅ **Real Data Mode**: Analyzing historical price data for accurate results")
        else:
            st.info("📊 **Demo Mode**: Using simulated data for demonstration")
        
        # Analysis details
        with st.expander("📋 Analysis Details", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Assets**: {len(params['selected_assets'])}")
                st.write(f"**Period**: Next {params['days_from_today']} days")
                
            with col2:
                st.write(f"**Phase Length**: {params['min_phase_length']}-{params['max_phase_length']} days")
                st.write(f"**Min Win Rate**: {params['min_winrate']:.1%}")
                
            with col3:
                st.write(f"**Data Range**: {params['start_year']}-{params['end_year']}")
                if using_real_data:
                    years = params['end_year'] - params['start_year']
                    st.write(f"**Analysis**: {years} years of data")
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            progress_text = st.empty()
        
        # Analysis progress callback
        def progress_callback(current, total, message):
            progress = current / total if total > 0 else 0
            progress_bar.progress(progress)
            progress_text.text(f"📊 {message} ({current}/{total})")
        
        try:
            start_time = datetime.now()
            
            if using_real_data:
                st.info("🔄 **Processing**: Analyzing historical price patterns...")
                
                # Pass progress callback to real analysis
                results_df = self.analyzer.real_engine.analyze_multiple_assets(
                    assets=params["selected_assets"],
                    min_phase_length=params["min_phase_length"],
                    max_phase_length=params["max_phase_length"],
                    min_winrate=params["min_winrate"],
                    start_year=params["start_year"],
                    end_year=params["end_year"],
                    days_from_today=params["days_from_today"],
                    progress_callback=progress_callback
                )
            else:
                st.info("🔄 **Generating**: Creating demo seasonal patterns...")
                
                # Simulate progress for dummy data
                total_steps = len(params["selected_assets"])
                for i, asset in enumerate(params["selected_assets"]):
                    progress_callback(i, total_steps, f"Processing {asset}")
                    import time
                    time.sleep(0.1)  # Small delay for demonstration
                
                results_df = self.analyzer.analyze_assets(
                    assets=params["selected_assets"],
                    start_period=params["start_period"],
                    min_phase_length=params["min_phase_length"],
                    min_winrate=params["min_winrate"],
                    winrate_threshold_longest=params["winrate_threshold_longest"],
                    start_year=params["start_year"],
                    end_year=params["end_year"],
                    days_from_today=params["days_from_today"],
                    max_phase_length=params["max_phase_length"]
                )
            
            # Apply deduplication if requested
            if params.get("deduplicate_patterns", True):
                # Import the engine for deduplication
                from app.seasonality_engine import RealSeasonalityEngine
                engine = RealSeasonalityEngine()
                original_count = len(results_df)
                results_df = engine._deduplicate_patterns(results_df)
                dedupe_msg = f" (reduced from {original_count} to {len(results_df)} after deduplication)"
            else:
                dedupe_msg = ""
            
            # Final progress update
            progress_callback(1, 1, "Analysis complete!")
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Clear progress display
            progress_container.empty()
            
            # Show completion status
            if results_df.empty:
                st.warning("⚠️ **No Results**: No seasonal patterns found matching your criteria.")
                st.info(f"**Suggestion**: Try lowering the minimum win rate or expanding the time range.")
                return
            else:
                st.success(f"✅ **Analysis Complete**: Found {len(results_df)} patterns in {duration:.1f} seconds{dedupe_msg}")
            
            # Display results
            self._display_results(results_df, params, using_real_data)
            
        except Exception as e:
            progress_container.empty()
            st.error(f"❌ **Analysis Failed**: {str(e)}")
            
            # Show more details for debugging
            with st.expander("🔧 Technical Details", expanded=False):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
    
    def _display_results(self, results_df: pd.DataFrame, params: Dict[str, Any], using_real_data: bool = False):
        """
        Display analysis results with export functionality
        
        Args:
            results_df: Analysis results DataFrame
            params: Analysis parameters
            using_real_data: Whether real data was used for analysis
        """
        
        st.success(f"✅ Analysis completed! Found {len(results_df)} seasonal patterns.")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_winrate = results_df['winrate'].mean()
            st.metric("Avg Win Rate", f"{avg_winrate:.1%}")
        
        with col2:
            avg_return = results_df['avg_return'].mean()
            st.metric("Avg Return", f"{avg_return:.2%}")
        
        with col3:
            avg_sharpe = results_df['sharpe_annualized'].mean()
            st.metric("Avg Sharpe", f"{avg_sharpe:.2f}")
        
        with col4:
            supported_cycles = results_df['cycle_supported'].sum()
            st.metric("Supported Cycles", f"{supported_cycles}/{len(results_df)}")
        
        st.markdown("---")
        
        # Results table
        st.subheader("📈 Seasonality Analysis Results")
        
        # Format for display
        display_df = self.exporter.format_for_display(results_df)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Export functionality
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("💾 Export to CSV", type="secondary", use_container_width=True):
                self._export_results(results_df)
        
        with col2:
            if using_real_data:
                st.success("💡 **Real Data**: Results based on actual historical price movements and statistical analysis.")
            else:
                st.info("💡 **Demo Mode**: Results are simulated. Download real forex data for accurate analysis.")
    
    def _export_results(self, results_df: pd.DataFrame):
        """
        Export results to CSV file
        
        Args:
            results_df: Results DataFrame to export
        """
        
        try:
            filepath = self.exporter.export_to_csv(
                df=results_df,
                filename="seasonality_analysis",
                export_dir=EXPORT_DIR
            )
            
            st.success(f"✅ Results exported to: `{os.path.basename(filepath)}`")
            st.info(f"📁 Full path: `{filepath}`")
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    def _run_data_download(self, force_download: bool):
        """
        Execute forex data download with progress tracking
        
        Args:
            force_download: Whether to force re-download existing files
        """
        
        st.header("📥 Forex Data Download")
        
        if force_download:
            st.info("🔄 **Force update enabled** - Re-downloading all data files")
        else:
            st.info("📥 **Smart download** - Only downloading missing files")
        
        # Show forex pairs that will be downloaded
        with st.expander("📋 Forex Pairs to Download", expanded=False):
            cols = st.columns(4)
            for i, pair in enumerate(FOREX_PAIRS):
                with cols[i % 4]:
                    st.write(f"• {pair}")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()
        
        def progress_callback(current, total, symbol):
            """Callback function to update progress"""
            progress = current / total
            progress_bar.progress(progress)
            
            if symbol == "Complete":
                status_text.success("✅ Download completed!")
            else:
                status_text.info(f"📥 Downloading {symbol}... ({current}/{total})")
        
        # Start download
        try:
            with st.spinner("Initializing download..."):
                summary = download_all_forex_data(
                    force_download=force_download,
                    progress_callback=progress_callback
                )
            
            # Show results
            st.success(f"🎉 **Download Complete!**")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Pairs", summary["total_pairs"])
            
            with col2:
                st.metric("Successful", summary["successful"])
            
            with col3:
                st.metric("Failed", summary["failed"])
            
            with col4:
                st.metric("Duration", f"{summary['duration_seconds']:.1f}s")
            
            # Detailed results
            if summary["results"]:
                st.subheader("📊 Download Details")
                
                # Create results dataframe
                results_data = []
                for result in summary["results"]:
                    results_data.append({
                        "Symbol": result["symbol"],
                        "Status": "✅ Success" if result["success"] else "❌ Failed",
                        "Message": result["message"],
                        "Rows": result["rows"] if result["success"] else "-",
                        "Date Range": result["date_range"] if result["success"] else "-"
                    })
                
                results_df = pd.DataFrame(results_data)
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
                # Show failed downloads if any
                failed_results = [r for r in summary["results"] if not r["success"]]
                if failed_results:
                    st.warning(f"⚠️ {len(failed_results)} downloads failed:")
                    for result in failed_results:
                        st.write(f"• **{result['symbol']}**: {result['message']}")
            
            # Refresh instruction
            st.info("🔄 **Refresh the page** to see the new data in the asset selection dropdown!")
            
            if st.button("🔄 Refresh Page", type="primary"):
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Download failed: {str(e)}")
            st.exception(e)
    
    def run(self):
        """
        Main application runner
        """
        
        # Render sidebar and get parameters
        params = self.render_sidebar()
        
        # Render main content
        self.render_main_content(params)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666;'>
                <small>
                    🚀 Built for high-performance seasonality analysis | 
                    Ready for millions of data points | 
                    Modular & scalable architecture
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )