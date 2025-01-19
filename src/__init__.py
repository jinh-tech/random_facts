import os

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define data directory structure
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
VIDEOS_DIR = os.path.join(DATA_DIR, "videos")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Create directories if they don't exist
for directory in [DATA_DIR, IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Test directories structure
TEST_DIRS = {
    "images": os.path.join(IMAGES_DIR, "test_images"),
    "videos": os.path.join(VIDEOS_DIR, "test_videos"),
    "audio": os.path.join(AUDIO_DIR, "test_audio"),
}

# Create test directories
for test_dir in TEST_DIRS.values():
    os.makedirs(test_dir, exist_ok=True)

import sys
from loguru import logger
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")