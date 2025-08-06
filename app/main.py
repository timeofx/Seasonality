"""
Main entry point for Seasonality Trading Tool
Professional Streamlit application for seasonality analysis

Run with: streamlit run app/main.py
"""

import sys
import os

# Add project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.gui import SeasonalityGUI
from app.auth import require_authentication


def main():
    """
    Main application entry point with secure authentication
    """
    
    # Require authentication before accessing the app
    require_authentication()
    
    # Initialize and run the GUI
    app = SeasonalityGUI()
    app.run()


if __name__ == "__main__":
    main()