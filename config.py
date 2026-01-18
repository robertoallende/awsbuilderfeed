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

# Make.com Webhook
MAKECOM_WEBHOOK_URL = os.getenv("MAKECOM_WEBHOOK_URL", "")

# Output files
MOCK_TWEETS_FILE = DATA_DIR / "mock_tweets.txt"
TWEETS_QUEUE_FILE = DATA_DIR / "tweets_queue.json"
