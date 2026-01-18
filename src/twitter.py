from datetime import datetime
from pathlib import Path
from typing import Optional
from config import MOCK_TWEETS_FILE
from src.database import get_next_article, mark_posted


def format_tweet(article: dict) -> str:
    """Format article as tweet (max 280 chars)."""
    title = article['title']
    url = article['url']
    
    # Twitter URL takes ~23 chars after shortening, newlines = 2 chars
    # So we have: 280 - 23 - 2 = 255 chars for title
    max_title_length = 255
    
    if len(title) > max_title_length:
        title = title[:max_title_length-3] + "..."
    
    return f"{title}\n\n{url}"


def post_tweet_mock(tweet_text: str, content_id: str) -> str:
    """Write tweet to mock file. Returns mock tweet_id."""
    MOCK_TWEETS_FILE.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mock_tweet_id = f"mock_{int(datetime.now().timestamp())}"
    
    with open(MOCK_TWEETS_FILE, "a") as f:
        f.write(f"[{timestamp}] Posted (ID: {mock_tweet_id}):\n")
        f.write(f"{tweet_text}\n")
        f.write("---\n\n")
    
    return mock_tweet_id


def post_tweet() -> Optional[dict]:
    """Get next article and post tweet. Returns result or None if queue empty."""
    article = get_next_article()
    
    if not article:
        return None
    
    tweet_text = format_tweet(article)
    tweet_id = post_tweet_mock(tweet_text, article['content_id'])
    
    mark_posted(article['content_id'], tweet_id)
    
    return {
        "content_id": article['content_id'],
        "title": article['title'],
        "tweet_id": tweet_id,
        "tweet_text": tweet_text
    }
