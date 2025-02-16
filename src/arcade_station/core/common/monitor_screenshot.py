import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QScreen
import tomllib

# Load configuration from TOML file
def load_config(config_path='config/screenshot_config.toml'):
    with open(config_path, 'rb') as f:
        return tomllib.load(f)

# Function to take a screenshot using configuration
def take_screenshot_from_config():
    config = load_config()
    monitor_index = config['screenshot']['monitor_index']
    file_location = config['screenshot']['file_location']
    file_name = config['screenshot']['file_name'] or datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    quality = config['screenshot']['quality']
    take_screenshot(monitor_index, file_location, file_name, quality)

# Function to take a screenshot
def take_screenshot(monitor_index=0, file_location='.', file_name=None, quality='High'):
    app = QApplication(sys.argv)
    screens = app.screens()
    if not screens:
        print("No screens detected. Ensure you are running in a GUI-capable environment.")
        return

    if monitor_index >= len(screens):
        print(f"Monitor index {monitor_index} is out of range. Defaulting to primary monitor.")
        monitor_index = 0

    screen = screens[monitor_index]
    screenshot = screen.grabWindow(0)

    # Set default file name if not provided
    if not file_name:
        file_name = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # Determine file path
    file_path = os.path.join(file_location, f"{file_name}.png")

    # Save the screenshot with adjustable quality
    if quality == 'High':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=95)
    elif quality == 'Medium':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=75)
    elif quality == 'Low':
        screenshot.save(file_path.replace('.png', '.jpg'), 'JPEG', quality=50)

    print(f"Screenshot saved to {file_path}")

    app.quit()

if __name__ == "__main__":
    take_screenshot_from_config() 