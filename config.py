"""
Configuration file for StoryWeaver Speech Therapy
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ENABLE_GOOGLE_GENAI = os.getenv("ENABLE_GOOGLE_GENAI", "true").lower() in ("1", "true", "yes")

# Model Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# File Paths
PICTURE_FOLDER = os.getenv("PICTURE_FOLDER", "pictures")
PROGRESS_FILE = os.getenv("PROGRESS_FILE", "progress_data.json")

# Performance Settings
ACCURACY_THRESHOLD = int(os.getenv("ACCURACY_THRESHOLD", "80"))

# Validation
if ENABLE_GOOGLE_GENAI and not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is required when ENABLE_GOOGLE_GENAI is true")