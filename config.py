import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# AWS Builder API
BUILDER_API_URL = "https://api.builder.aws.com/cs/content/feed"
BUILDER_BASE_URL = "https://builder.aws.com"

# Buffer API
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN", "")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID", "")

# Mock output
MOCK_TWEETS_FILE = DATA_DIR / "mock_tweets.txt"
