# Installation Guide

Complete setup instructions for YouTube Audio Master on all supported platforms.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.9 or newer |
| FFmpeg | Any recent release |

---

## 1. Python

Download the official installer from <https://www.python.org/downloads/> and ensure
the **"Add Python to PATH"** checkbox is selected during installation.

---

## 2. FFmpeg

FFmpeg handles audio conversion and must be installed separately.

### Windows

**Option A — Chocolatey (recommended)**

```powershell
choco install ffmpeg
```

**Option B — Scoop**

```powershell
scoop install ffmpeg
```

**Option C — Manual**

1. Download a build from <https://ffmpeg.org/download.html>
2. Extract to a permanent location (e.g. `C:\ffmpeg`)
3. Add the `bin` directory to your `PATH` environment variable

### macOS

```bash
brew install ffmpeg
```

If Homebrew is not installed, run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux (Ubuntu / Debian)

```bash
sudo apt update && sudo apt install ffmpeg
```

### Linux (Fedora / RHEL)

```bash
sudo dnf install ffmpeg
```

### Linux (Arch)

```bash
sudo pacman -S ffmpeg
```

Verify installation:

```bash
ffmpeg -version
```

---

## 3. Python Dependencies

It is recommended to use a virtual environment:

```bash
# Create
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 4. Running the Application

```bash
python -m youtube_audio_master.main
```

Or install the package for a convenient command:

```bash
pip install -e .
youtube-audio-master
```

---

## 5. Building a Standalone Executable (Optional)

```bash
python build_executable.py
```

The resulting executable in `dist/` can be copied to any machine with FFmpeg
installed — no Python required on the target machine.

---

## Troubleshooting

**"FFmpeg not found on PATH"**  
Make sure FFmpeg's `bin` directory is in your system `PATH` and restart your
terminal (or reboot on Windows).

**ModuleNotFoundError for FreeSimpleGUI / yt-dlp**  
Run `pip install -r requirements.txt` inside your activated virtual environment.

**Download errors**  
yt-dlp is updated frequently. Upgrade it with:

```bash
pip install -U yt-dlp
```
