#!/usr/bin/env python3
"""
Main entry point for the RAG Customer Service System.
Run this script to start both API and frontend.
"""

import os
import sys
import subprocess
import time
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
