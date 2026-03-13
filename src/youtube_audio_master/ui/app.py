"""
app.py - FreeSimpleGUI desktop application for YouTube Audio Master.

Provides a professional, threaded GUI for downloading and converting
YouTube audio to AAC, ALAC, or MP3 with real-time progress updates.
"""

import logging
import os
import platform
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import FreeSimpleGUI as sg

from youtube_audio_master.core.converter import (
    DEFAULT_FORMAT,
    DEFAULT_QUALITY,
    QUALITY_OPTIONS,
    get_codec,
    get_extension,
    is_ffmpeg_available,
    list_formats,
)
from youtube_audio_master.core.downloader import download_audio, validate_url

logger = logging.getLogger(__name__)

# ── Theme ────────────────────────────────────────────────────────────────────
sg.theme("DarkBlue3")
sg.set_options(font=("Arial", 10))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _log(window: sg.Window, message: str) -> None:
    """Append a timestamped line to the GUI log widget."""
    window["-LOG-"].print(f"[{_timestamp()}] {message}")


def _open_folder(folder: str) -> None:
    """Open *folder* in the system file manager."""
    system = platform.system()
    if system == "Windows":
        os.startfile(folder)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])


def _resolve_conflict(filepath: str) -> Optional[str]:
    """Ask the user what to do when *filepath* already exists.

    Returns the resolved path, or *None* if the user cancels.
    """
    if not os.path.exists(filepath):
        return filepath

    layout = [
        [sg.Text(f"File already exists:\n{os.path.basename(filepath)}", size=(50, 3))],
        [sg.Button("Overwrite"), sg.Button("Rename"), sg.Button("Cancel")],
    ]
    win = sg.Window("File Conflict", layout, modal=True)
    event, _ = win.read()
    win.close()

    if event == "Overwrite":
        try:
            os.remove(filepath)
        except OSError as exc:
            sg.popup_error(f"Could not remove existing file:\n{exc}", title="Error")
            return None
        return filepath

    if event == "Rename":
        name, ext = os.path.splitext(filepath)
        counter = 1
        candidate = f"{name}_{counter}{ext}"
        while os.path.exists(candidate):
            counter += 1
            candidate = f"{name}_{counter}{ext}"
        return candidate

    return None  # Cancel


# ── Window layout ────────────────────────────────────────────────────────────

def _build_layout() -> list:
    """Return the FreeSimpleGUI layout definition."""
    formats = list_formats()

    return [
        [sg.Text("🎵 YouTube Audio Master", font=("Arial", 14, "bold"))],
        [sg.Text(
            "High-quality YouTube to AAC / ALAC / MP3 converter",
            font=("Arial", 9),
        )],
        [sg.HSeparator()],

        # URL
        [
            sg.Text("YouTube URL:", size=(15, 1)),
            sg.InputText(key="-URL-", size=(52, 1), focus=True,
                         tooltip="Paste a YouTube video or playlist URL"),
        ],

        # Format & Quality
        [
            sg.Text("Output Format:", size=(15, 1)),
            sg.Combo(
                formats,
                default_value=DEFAULT_FORMAT,
                key="-FORMAT-",
                size=(10, 1),
                readonly=True,
            ),
            sg.Text("  Quality (kbps):"),
            sg.Combo(
                QUALITY_OPTIONS,
                default_value=DEFAULT_QUALITY,
                key="-QUALITY-",
                size=(8, 1),
                readonly=True,
            ),
        ],

        # Download folder
        [
            sg.Text("Download Folder:", size=(15, 1)),
            sg.InputText(
                key="-FOLDER-",
                size=(40, 1),
                default_text=str(Path.home() / "Downloads"),
            ),
            sg.FolderBrowse(button_text="Browse", size=(9, 1)),
        ],

        [sg.HSeparator()],

        # Action buttons
        [
            sg.Button(
                "▶  Convert & Download",
                key="-START-",
                size=(22, 1),
                button_color=("white", "#2e7d32"),
                font=("Arial", 10, "bold"),
            ),
            sg.Button("Clear Log", size=(12, 1)),
            sg.Button("Open Folder", size=(13, 1)),
            sg.Button("Exit", size=(9, 1)),
        ],

        [sg.HSeparator()],

        # Progress
        [
            sg.ProgressBar(
                100,
                orientation="h",
                size=(60, 18),
                key="-PROGRESS-",
                bar_color=("#43a047", "lightgray"),
            )
        ],
        [sg.Text("Status: Ready", key="-STATUS-", size=(70, 1), font=("Arial", 9))],

        # Log
        [
            sg.Multiline(
                size=(82, 16),
                key="-LOG-",
                disabled=True,
                autoscroll=True,
                background_color="#1a1a1a",
                text_color="#00FF00",
                font=("Courier", 9),
            )
        ],
    ]


# ── Download worker ──────────────────────────────────────────────────────────

class _DownloadState:
    """Shared state between the GUI thread and the download worker thread."""

    def __init__(self) -> None:
        self.running = False
        self.percent: float = 0.0
        self.status_msg: str = ""


def _make_progress_hook(state: _DownloadState, window: sg.Window):
    """Return a yt-dlp progress hook that updates *state*."""

    def hook(d: Dict[str, Any]) -> None:
        status = d.get("status", "")
        if status == "downloading":
            raw = d.get("_percent_str", "0%").strip().rstrip("%")
            try:
                state.percent = float(raw)
            except ValueError:
                state.percent = 0.0
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            state.status_msg = (
                f"Downloading… {state.percent:.1f}% | Speed: {speed} | ETA: {eta}"
            )
        elif status == "finished":
            state.percent = 100.0
            state.status_msg = "Converting audio…"
            _log(window, "📦 Download finished, converting audio…")
        elif status == "error":
            state.status_msg = "Error during download"

    return hook


def _worker(
    url: str,
    folder: str,
    codec: str,
    quality: str,
    state: _DownloadState,
    window: sg.Window,
) -> None:
    """Background thread: download + convert, then signal the GUI."""
    try:
        _log(window, f"📥 Starting download: {url}")
        hook = _make_progress_hook(state, window)
        result = download_audio(url, folder, codec, quality, progress_hook=hook)

        if result is None:
            _log(window, "❌ Download failed. Check the URL and try again.")
            window.write_event_value("-DONE-", False)
            return

        # Handle file conflicts on the already-downloaded file.
        resolved = _resolve_conflict(result)
        if resolved is None:
            # User cancelled — remove the downloaded file to avoid orphans.
            try:
                if os.path.exists(result):
                    os.remove(result)
            except OSError:
                pass
            _log(window, "⚠️  Operation cancelled by user.")
            window.write_event_value("-DONE-", False)
            return

        # If the user chose to rename, move the file to the new path.
        if resolved != result and os.path.exists(result):
            try:
                os.rename(result, resolved)
            except OSError as exc:
                _log(window, f"❌ Could not rename file: {exc}")
                window.write_event_value("-DONE-", False)
                return

        _log(window, "✅ Conversion complete!")
        _log(window, f"📁 Saved to: {resolved}")
        window.write_event_value("-DONE-", True)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Worker thread error: %s", exc)
        _log(window, f"❌ Unexpected error: {exc}")
        window.write_event_value("-DONE-", False)
    finally:
        state.running = False


# ── Main application loop ────────────────────────────────────────────────────

def run_app() -> None:
    """Create the window and run the event loop."""

    if not is_ffmpeg_available():
        sg.popup_error(
            "FFmpeg is not installed or not found on PATH.\n\n"
            "Please install FFmpeg and restart the application.\n"
            "See INSTALLATION.md for instructions.",
            title="FFmpeg Missing",
        )
        return

    window = sg.Window(
        "YouTube Audio Master",
        _build_layout(),
        finalize=True,
        size=(860, 680),
        resizable=True,
    )

    state = _DownloadState()

    _log(window, "🚀 YouTube Audio Master started.")
    _log(window, "Paste a YouTube URL and click '▶  Convert & Download'.")
    _log(window, "Supports: individual videos, playlists, Shorts.")

    while True:
        event, values = window.read(timeout=150)

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # ── Progress animation while downloading ─────────────────────────
        if state.running:
            window["-PROGRESS-"].update_bar(int(state.percent))
            if state.status_msg:
                window["-STATUS-"].update(f"Status: {state.status_msg}")

        # ── Start download ───────────────────────────────────────────────
        if event == "-START-" and not state.running:
            url = values["-URL-"].strip()
            folder = values["-FOLDER-"].strip()
            fmt = values["-FORMAT-"]
            quality = values["-QUALITY-"]

            if not url:
                sg.popup_error("Please enter a YouTube URL.", title="Input Required")
                continue

            if not validate_url(url):
                sg.popup_error(
                    "The URL does not appear to be a valid YouTube URL.\n\n"
                    "Accepted formats:\n"
                    "  https://www.youtube.com/watch?v=...\n"
                    "  https://youtu.be/...\n"
                    "  https://www.youtube.com/playlist?list=...",
                    title="Invalid URL",
                )
                continue

            if not folder:
                sg.popup_error("Please select a download folder.", title="Input Required")
                continue

            codec = get_codec(fmt)
            if codec is None:
                sg.popup_error(f"Unknown format: {fmt}", title="Error")
                continue

            state.running = True
            state.percent = 0.0
            state.status_msg = "Starting…"

            window["-START-"].update(disabled=True)
            window["-STATUS-"].update("Status: Downloading…")

            thread = threading.Thread(
                target=_worker,
                args=(url, folder, codec, quality, state, window),
                daemon=True,
            )
            thread.start()

        # ── Download finished signal ─────────────────────────────────────
        elif event == "-DONE-":
            window["-START-"].update(disabled=False)
            window["-PROGRESS-"].update_bar(0)
            window["-STATUS-"].update("Status: Ready")
            _log(window, "=" * 60)

        # ── Clear log ────────────────────────────────────────────────────
        elif event == "Clear Log":
            window["-LOG-"].update("")
            _log(window, "Log cleared.")

        # ── Open folder ──────────────────────────────────────────────────
        elif event == "Open Folder":
            folder = values["-FOLDER-"].strip()
            if folder and os.path.isdir(folder):
                _open_folder(folder)
                _log(window, f"📂 Opened folder: {folder}")
            else:
                sg.popup_error(
                    f"Folder not found:\n{folder}",
                    title="Folder Not Found",
                )

    window.close()
