import sys
import os
from PyInstaller.__main__ import run

if __name__ == '__main__':
    options = [
        '--onefile',  # Create a single executable file
        '--windowed',  # Suppress the console window (for GUI applications)
        'your_script.py',  # Replace with your Python script name
    ]
    run(options)
