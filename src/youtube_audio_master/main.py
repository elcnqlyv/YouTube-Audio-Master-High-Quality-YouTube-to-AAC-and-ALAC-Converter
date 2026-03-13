"""
YouTube Audio Master - Entry Point

Launches the desktop GUI application.
"""

import sys
import logging


def setup_logging() -> None:
    """Configure application-level logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """Application entry point."""
    setup_logging()

    try:
        from youtube_audio_master.ui.app import run_app
        run_app()
    except ImportError as exc:
        print(f"[ERROR] Missing dependency: {exc}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as exc:  # pylint: disable=broad-except
        logging.getLogger(__name__).exception("Unhandled error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
