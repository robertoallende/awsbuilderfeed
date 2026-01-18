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

# Twitter/X (to be configured later)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

# Mock output
MOCK_TWEETS_FILE = DATA_DIR / "mock_tweets.txt"
