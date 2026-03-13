"""
converter.py - Audio conversion helpers using FFmpeg (via ffmpeg-python).

Provides codec mapping and quality validation utilities used by the GUI.
"""

import logging
import shutil
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Mapping from user-visible format name -> yt-dlp codec name
CODEC_MAP: Dict[str, str] = {
    "AAC": "aac",
    "ALAC": "alac",
    "MP3": "mp3",
}

# File extension produced for each codec
EXT_MAP: Dict[str, str] = {
    "aac": "m4a",
    "alac": "m4a",
    "mp3": "mp3",
}

# Supported quality presets (kbps)
QUALITY_OPTIONS: List[str] = ["128", "192", "256", "320"]

# Default values
DEFAULT_FORMAT = "AAC"
DEFAULT_QUALITY = "192"


def is_ffmpeg_available() -> bool:
    """Return True if FFmpeg is present on PATH."""
    return shutil.which("ffmpeg") is not None


def get_codec(format_name: str) -> Optional[str]:
    """Return the yt-dlp codec string for *format_name* (case-insensitive).

    Returns *None* if the format is not recognised.
    """
    return CODEC_MAP.get(format_name.upper())


def get_extension(codec: str) -> str:
    """Return the file extension for a given *codec* name."""
    return EXT_MAP.get(codec.lower(), "m4a")


def list_formats() -> List[str]:
    """Return the list of supported user-visible format names."""
    return list(CODEC_MAP.keys())


def validate_quality(quality: str) -> Tuple[bool, str]:
    """Validate *quality* bitrate string.

    Returns a ``(valid, message)`` tuple. ``valid`` is *True* when *quality*
    is in :data:`QUALITY_OPTIONS`.
    """
    if quality in QUALITY_OPTIONS:
        return True, ""
    return False, f"Quality must be one of: {', '.join(QUALITY_OPTIONS)}"
