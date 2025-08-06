#!/usr/bin/env python3
"""
Cross-platform starter script for Seasonality Trading Tool
Alternative to the .bat file for better Python environment handling
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_python():
    """Check if Python is properly installed"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ ERROR: Python 3.8+ required. Current version:", sys.version)
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    except Exception as e:
        print(f"❌ ERROR checking Python: {e}")
        return False

def install_requirements():
    """Install required packages"""
    try:
        print("\n[2/4] Installing/updating requirements...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ ERROR installing requirements:\n{result.stderr}")
            return False
        
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Installation timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def start_streamlit():
    """Start the Streamlit application"""
    try:
        print("\n[3/4] Starting Seasonality Trading Tool...")
        print("🌐 Application will be available at: http://localhost:8501")
        print("🔄 Browser will open automatically in 3 seconds...")
        
        # Start Streamlit process without auto-opening browser
        cmd = [sys.executable, "-m", "streamlit", "run", "app/main.py", 
               "--server.port=8501", "--server.headless=false", 
               "--browser.gatherUsageStats=false"]
        
        process = subprocess.Popen(cmd)
        
        # Wait for server to start, then open browser manually
        time.sleep(4)
        webbrowser.open("http://localhost:8501")
        
        print("\n🚀 Application started successfully!")
        print("📱 Browser should open automatically")
        print("⏹️  Press Ctrl+C to stop the application")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Application stopped by user")
        try:
            process.terminate()
        except:
            pass
    except Exception as e:
        print(f"\n❌ ERROR starting application: {e}")
        return False
    
    return True

def main():
    """Main startup sequence"""
    print("=" * 50)
    print("    🔄 Seasonality Trading Tool Starter")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Step 1: Check Python
    print("\n[1/4] Checking Python installation...")
    if not check_python():
        input("\n❌ Press Enter to exit...")
        sys.exit(1)
    
    # Step 2: Install requirements
    if not install_requirements():
        input("\n❌ Press Enter to exit...")
        sys.exit(1)
    
    # Step 3: Start application
    print("\n[4/4] Launching application...")
    if not start_streamlit():
        input("\n❌ Press Enter to exit...")
        sys.exit(1)
    
    print("\n✅ Application session completed")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()