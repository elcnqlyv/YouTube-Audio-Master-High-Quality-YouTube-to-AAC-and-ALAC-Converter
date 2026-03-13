# YouTube Audio Master

> High-quality YouTube to AAC, ALAC, and MP3 desktop converter.

---

## Features

- 🎵 Download individual YouTube videos or entire playlists
- 🔊 Convert to **AAC**, **ALAC**, or **MP3**
- ⚡ Quality presets: 128, 192, 256, 320 kbps
- 📁 Custom download folder with folder browser
- ♻️ File conflict resolution (overwrite or auto-rename)
- 📊 Real-time download progress
- 🖥️ Clean GUI — no browser required
- 🌐 Cross-platform: Windows, macOS, Linux

---

## Quick Start

### 1. Install FFmpeg

FFmpeg must be installed separately. See [INSTALLATION.md](INSTALLATION.md) for OS-specific steps.

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python -m youtube_audio_master.main
```

Or, after `pip install -e .`:

```bash
youtube-audio-master
```

---

## Project Structure

```
src/youtube_audio_master/
├── main.py              ← entry point
├── core/
│   ├── downloader.py    ← yt-dlp download logic
│   └── converter.py     ← codec / quality helpers
└── ui/
    └── app.py           ← FreeSimpleGUI interface
```

---

## Build Standalone Executable

```bash
python build_executable.py
```

The executable is written to `dist/YouTubeAudioMaster` (or `.exe` on Windows).

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "FFmpeg not found" | Install FFmpeg and ensure it is on `PATH` |
| Download fails | Update yt-dlp: `pip install -U yt-dlp` |
| GUI does not open | Ensure `FreeSimpleGUI` is installed |
| Permission denied on folder | Choose a folder your user account can write to |

---

## License

MIT
