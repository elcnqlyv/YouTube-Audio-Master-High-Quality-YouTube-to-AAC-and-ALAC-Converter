"""
downloader.py - YouTube downloading logic using yt-dlp.

Supports individual videos and playlists with configurable output options.
"""

import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse

import yt_dlp

logger = logging.getLogger(__name__)

# Supported audio formats and their file extensions
FORMAT_EXT: Dict[str, str] = {
    "aac": "m4a",
    "alac": "m4a",
    "mp3": "mp3",
}

# Accepted YouTube host names (exact match against netloc)
_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "music.youtube.com",
}


def validate_url(url: str) -> bool:
    """Return True if *url* is a recognised YouTube URL.

    Parses the URL and compares the host against a fixed allowlist so that
    substrings such as ``evil.com/?q=youtube.com`` are rejected.
    """
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and parsed.netloc in _YOUTUBE_HOSTS
    except ValueError:
        return False


def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """Fetch metadata for *url* without downloading the media.

    Returns the info dict on success, or *None* on failure.
    """
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as exc:
        logger.error("Could not fetch video info: %s", exc)
        return None


def download_audio(
    url: str,
    output_folder: str,
    codec: str,
    quality: str,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Optional[str]:
    """Download and convert YouTube audio to *codec* at *quality* kbps.

    Parameters
    ----------
    url:
        YouTube video or playlist URL.
    output_folder:
        Directory where the final file(s) will be saved.
    codec:
        One of ``"aac"``, ``"alac"``, or ``"mp3"``.
    quality:
        Bitrate string such as ``"192"``.
    progress_hook:
        Optional callable that receives yt-dlp progress dicts.

    Returns
    -------
    str or None
        Path of the downloaded file on success, or *None* on failure.
    """
    if not validate_url(url):
        logger.error("Invalid YouTube URL: %s", url)
        return None

    output_folder_path = Path(output_folder)
    if not output_folder_path.exists():
        try:
            output_folder_path.mkdir(parents=True, exist_ok=True)
            logger.info("Created output folder: %s", output_folder_path)
        except OSError as exc:
            logger.error("Cannot create output folder %s: %s", output_folder_path, exc)
            return None

    output_template = str(output_folder_path / "%(title)s.%(ext)s")

    hooks = [progress_hook] if progress_hook else []

    ydl_opts: Dict[str, Any] = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": quality,
                "nopostoverwrites": False,
            }
        ],
        "outtmpl": output_template,
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": True,
        "progress_hooks": hooks,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting info and downloading: %s", url)
            info = ydl.extract_info(url, download=True)

            if info is None:
                logger.error("Could not extract info for: %s", url)
                return None

            # For playlists yt-dlp returns a dict with an "entries" key.
            if "entries" in info:
                entries = list(info["entries"])
                skipped = sum(1 for e in entries if e is None)
                if skipped:
                    logger.warning(
                        "Skipped %d unavailable/private video(s) in playlist.",
                        skipped,
                    )
                title = info.get("title", "playlist")
            else:
                title = info.get("title", "audio")

            ext = FORMAT_EXT.get(codec, "m4a")
            # Sanitise the title the same way yt-dlp does for filenames.
            safe_title = ydl.prepare_filename(info)
            # prepare_filename includes the raw extension; replace it.
            base, _ = os.path.splitext(safe_title)
            final_path = f"{base}.{ext}"
            logger.info("Download complete: %s", final_path)
            return final_path
    except yt_dlp.utils.DownloadError as exc:
        logger.error("Download error: %s", exc)
        return None
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected error during download: %s", exc)
        return None
