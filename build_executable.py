#!/usr/bin/env python3
"""
build_executable.py - Package YouTube Audio Master as a standalone executable.

Usage:
    python build_executable.py

Requirements:
    - FFmpeg must be installed and available on PATH
    - PyInstaller is installed automatically if absent
"""

import os
import platform
import subprocess
import sys


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ensure_pyinstaller() -> None:
    """Install PyInstaller if it is not already available."""
    try:
        import PyInstaller  # noqa: F401  # pylint: disable=import-outside-toplevel
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller…")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            stdout=subprocess.DEVNULL,
        )
        print("✅ PyInstaller installed")


def _check_ffmpeg() -> bool:
    """Return True if FFmpeg is found on PATH, False otherwise."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
        print("✅ FFmpeg found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found on PATH!")
        system = platform.system()
        if system == "Windows":
            print("   Install via Chocolatey:  choco install ffmpeg")
            print("   Install via Scoop:       scoop install ffmpeg")
        elif system == "Darwin":
            print("   Install via Homebrew:    brew install ffmpeg")
        else:
            print("   Ubuntu/Debian:           sudo apt-get install ffmpeg")
        return False


# ── Build ─────────────────────────────────────────────────────────────────────

def build() -> None:
    """Run the PyInstaller build process."""
    print("=" * 70)
    print("🎵 YouTube Audio Master — Building desktop executable")
    print("=" * 70)

    print("\n📋 Checking prerequisites…")
    if not _check_ffmpeg():
        print("\n⚠️  FFmpeg is required. Please install it and retry.")
        sys.exit(1)

    _ensure_pyinstaller()

    # Entry point: src/youtube_audio_master/main.py
    entry = os.path.join("src", "youtube_audio_master", "main.py")
    if not os.path.isfile(entry):
        print(f"\n❌ Entry point not found: {entry}")
        print("   Make sure you run this script from the project root directory.")
        sys.exit(1)

    hidden_imports = [
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--hidden-import=yt_dlp.postprocessor",
        "--hidden-import=FreeSimpleGUI",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=YouTubeAudioMaster",
        "--paths=src",
    ] + hidden_imports + [entry]

    print(f"\n🔨 Running PyInstaller…\n")

    result = subprocess.run(cmd)

    print()
    print("=" * 70)
    if result.returncode == 0:
        exe = (
            "dist\\YouTubeAudioMaster.exe"
            if platform.system() == "Windows"
            else "dist/YouTubeAudioMaster"
        )
        print("✅ Build successful!")
        print(f"📁 Executable: {exe}")
        print("\nYou can run it directly or distribute it to other users.")
    else:
        print("❌ Build failed. Review the output above for details.")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    build()
