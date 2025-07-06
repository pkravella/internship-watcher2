#!/usr/bin/env python3
"""
Test script for the Internship Watcher - runs once to verify functionality
"""

from internship_watcher import InternshipWatcher
import logging

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_watcher():
    """Test the internship watcher functionality."""
    try:
        print("Testing Internship Watcher...")
        
        watcher = InternshipWatcher()
        
        # Test fetching data
        print("Fetching repository data...")
        content = watcher.fetch_repository_data()
        if content:
            print(f"Successfully fetched {len(content)} characters of data")
        else:
            print("Failed to fetch repository data")
            return
        
        # Test parsing
        print("Parsing internship listings...")
        internships = watcher.parse_internships(content)
        print(f"Found {len(internships)} internship listings")
        
        # Show some examples
        if internships:
            print("\n Sample internships found:")
            for i, internship in enumerate(internships[:3]):  # Show first 3
                print(f"  {i+1}. {internship['company']} - {internship['role']} ({internship['location']})")
        
        # Test saving/loading
        print("\nTesting data persistence...")
        watcher.save_internships(internships)
        loaded_ids = watcher.load_previous_internships()
        print(f"Successfully saved and loaded {len(loaded_ids)} internship IDs")
        
        print("\nAll tests passed! The watcher is ready to run.")
        print("\nTo start monitoring, run: python internship_watcher.py")
        
    except Exception as e:
        print(f"Test failed: {e}")
        logging.error(f"Test error: {e}")

if __name__ == "__main__":
    test_watcher() 