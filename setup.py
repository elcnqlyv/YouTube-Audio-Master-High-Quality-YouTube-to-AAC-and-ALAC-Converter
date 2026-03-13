"""
setup.py - Package configuration for YouTube Audio Master.

Install with:
    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="youtube-audio-master",
    version="1.0.0",
    description="High-quality YouTube to AAC and ALAC desktop converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YouTube Audio Master",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "youtube-audio-master=youtube_audio_master.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
)
