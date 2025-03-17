#!/usr/bin/env python
"""
Test script for dynamic marquee functionality.
This script simulates ITGMania writing to the log file and tests if
the monitor can properly read and display images.
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

# Import necessary modules
from arcade_station.core.common.core_functions import load_toml_config, log_message
from arcade_station.core.common.display_image import display_image

def test_write_to_log_file():
    """Write test data to the ITGMania log file"""
    # Load configuration to get log file path
    config = load_toml_config('display_config.toml')
    log_file_path = config.get('dynamic_marquee', {}).get('itgmania_display_file_path')
    
    if not log_file_path:
        print("ERROR: No log file path configured in display_config.toml")
        return False
    
    # Ensure directory exists
    log_file = Path(log_file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Get default banner path from config
    default_image_path = config.get('display', {}).get('default_image_path')
    
    # Create test content
    test_content = f"""Event: Chosen
Pack: TestPack
SongTitle: Test Song

SongDir: C:/Games/ITGmania/Songs/TestPack/TestSong
Banner: {default_image_path}
ChartFile: C:/Games/ITGmania/Songs/TestPack/TestSong/TestSong.sm
MusicFile: C:/Games/ITGmania/Songs/TestPack/TestSong/TestSong.ogg
"""
    
    try:
        # Write test content to log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"Successfully wrote test data to log file: {log_file}")
        print(f"Using banner path: {default_image_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write to log file: {e}")
        return False

def test_display_image():
    """Test displaying an image directly"""
    config = load_toml_config('display_config.toml')
    image_path = config.get('display', {}).get('default_image_path')
    background_color = config.get('display', {}).get('background_color', 'black')
    
    try:
        print(f"Testing image display with: {image_path}")
        display_image(image_path, background_color)
        print("Image should now be displayed")
        return True
    except Exception as e:
        print(f"ERROR: Failed to display image: {e}")
        return False

def main():
    """Main test function"""
    print("\n===== Testing Dynamic Marquee Functionality =====")
    
    # Test image display directly
    print("\n1. Testing direct image display...")
    if test_display_image():
        print("SUCCESS: Image display test passed")
    else:
        print("FAILED: Image display test failed")
    
    # Test writing to log file
    print("\n2. Testing log file writing...")
    if test_write_to_log_file():
        print("SUCCESS: Log file write test passed")
    else:
        print("FAILED: Log file write test failed")
    
    # Suggestion to run monitor script
    print("\n3. To complete testing, run:")
    print("   python src/arcade_station/launchers/monitor_itgmania.py")
    print("\nThis should read the test log file and display the image")
    
    print("\n===== Test Complete =====")

if __name__ == "__main__":
    main() 