#!/usr/bin/env python3
"""
Setup script for Internship Watcher
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Setting up Internship Watcher 2.0...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print(".env file not found! Please create it with your email configuration.")
        return False
    
    # Install dependencies
    if not run_command("python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt", "Installing dependencies in virtual environment"):
        return False
    
    # Run test
    print("\n🧪 Running test to verify setup...")
    if not run_command("source venv/bin/activate && python test_watcher.py", "Testing watcher functionality"):
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run 'source venv/bin/activate && python internship_watcher.py' to start monitoring")
    print("   2. Press Ctrl+C to stop monitoring")
    print("   3. Check 'internship_watcher.log' for detailed logs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 