#!/usr/bin/env python3
"""
Build script to package the desktop app as a standalone executable.
Run: python build_executable.py

Requirements:
- FFmpeg must be installed on your system
- PyInstaller will be installed automatically if not present
"""

import subprocess
import sys
import os
import platform

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found!")
        print("   Please install FFmpeg:")
        if platform.system() == 'Windows':
            print("   - Chocolatey: choco install ffmpeg")
            print("   - Scoop: scoop install ffmpeg")
        elif platform.system() == 'Darwin':
            print("   - Homebrew: brew install ffmpeg")
        else:
            print("   - Ubuntu/Debian: sudo apt-get install ffmpeg")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("=" * 70)
    print("🎵 YouTube Audio Master - Building Desktop App")
    print("=" * 70)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg is required but not installed.")
        sys.exit(1)
    
    install_pyinstaller()
    
    # Build command
    hidden_imports = [
        'yt_dlp',
        'yt_dlp.extractor',
    ]
    
    hidden_imports_str = ' '.join([f'--hidden-import={imp}' for imp in hidden_imports])
    
    cmd = (
        f'{sys.executable} -m PyInstaller '
        f'--onefile '
        f'--windowed '
        f'--name=YouTubeAudioMaster '
        f'--icon=NONE '
        f'{hidden_imports_str} '
        f'desktop_app.py'
    )
    
    print(f"\n🔨 Building executable...")
    print(f"Command: {cmd}\n")
    
    result = os.system(cmd)
    
    if result == 0:
        print("\n" + "=" * 70)
        print("✅ Build successful!")
        print("=" * 70)
        
        exe_path = "dist/YouTubeAudioMaster.exe" if platform.system() == 'Windows' else "dist/YouTubeAudioMaster"
        print(f"\n📁 Executable location: {exe_path}")
        print(f"\n✨ You can now:")
        print(f"   • Run the executable directly")
        print(f"   • Share it with others")
        print(f"   • Create a shortcut to it")
        print(f"\n🚀 The app is ready to use!")
    else:
        print("\n" + "=" * 70)
        print("❌ Build failed!")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    build_executable()