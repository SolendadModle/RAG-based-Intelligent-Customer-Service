"""
Main entry point for the RAG Customer Service System.
Run this script to start both API and frontend.

Usage:
    python run.py           # Start both backend and frontend
    python run.py --help    # Show help message

Note: The shebang line (#!/usr/bin/env python3) has been removed for
      better Windows compatibility. Use 'python run.py' to run the script.
"""

import os
import sys
import subprocess
import time
import argparse
from multiprocessing import Process

def start_api():
    """Start the FastAPI backend."""
    print("Starting API server...")
    os.system("python -m src.api.app")

def start_frontend():
    """Start the Streamlit frontend."""
    print("Starting Streamlit frontend...")
    time.sleep(3)  # Wait for API to start
    os.system("streamlit run src/frontend/streamlit_app.py")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='RAG-based Intelligent Customer Service System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py              # Start both backend and frontend
  python run.py --help       # Show this help message

For Windows users:
  If you encounter errors, make sure to use 'python run.py' instead of './run.py'
        """
    )
    parser.add_argument('--version', action='version', version='1.0.0')
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG-based Intelligent Customer Service System")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your API keys.")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    print("Starting services...")
    print()
    print("💡 Tip: Press Ctrl+C to stop all services")
    print()
    
    # Start API in separate process
    api_process = Process(target=start_api)
    api_process.start()
    
    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
        api_process.terminate()
        api_process.join()
        print("Goodbye!")

if __name__ == "__main__":
    main()
