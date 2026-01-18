from datetime import datetime
from pathlib import Path
from typing import Optional
import httpx
from config import MOCK_TWEETS_FILE, BUFFER_ACCESS_TOKEN, BUFFER_PROFILE_ID
from src.database import get_next_article, mark_posted


def format_tweet(article: dict) -> str:
    """Format article as tweet (max 280 chars)."""
    title = article['title']
    url = article['url']
    tags = article.get('tags', '')
    
    # Convert tags to hashtags (limit to first 3)
    hashtags = ""
    if tags:
        tag_list = [f"#{tag.strip().replace('-', '').replace(' ', '')}" 
                    for tag in tags.split(',')[:3]]
        hashtags = " " + " ".join(tag_list)
    
    # Twitter URL takes ~23 chars after shortening
    # Calculate available space: 280 - url(23) - newlines(2) - hashtags - spaces
    available_for_title = 280 - 23 - 2 - len(hashtags) - 1
    
    if len(title) > available_for_title:
        title = title[:available_for_title-3] + "..."
    
    return f"{title}\n\n{url}{hashtags}"


def post_tweet_buffer(tweet_text: str, content_id: str) -> str:
    """Post tweet to Buffer API. Returns update_id."""
    url = "https://api.bufferapp.com/1/updates/create.json"
    
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"
    }
    
    data = {
        "text": tweet_text,
        "profile_ids[]": BUFFER_PROFILE_ID,
        "now": False  # Schedule for optimal time
    }
    
    response = httpx.post(url, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result['updates'][0]['id']


def get_buffer_profiles() -> list:
    """Get list of Buffer profiles (connected social accounts)."""
    url = "https://api.bufferapp.com/1/profiles.json"
    
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"
    }
    
    response = httpx.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response.json()


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


def has_buffer_credentials() -> bool:
    """Check if Buffer API credentials are configured."""
    return all([
        BUFFER_ACCESS_TOKEN and BUFFER_ACCESS_TOKEN != "",
        BUFFER_PROFILE_ID and BUFFER_PROFILE_ID != ""
    ])


def post_tweet() -> Optional[dict]:
    """Get next article and post tweet. Returns result or None if queue empty."""
    article = get_next_article()
    
    if not article:
        return None
    
    tweet_text = format_tweet(article)
    
    # Try Buffer API if credentials available, otherwise use mock
    try:
        if has_buffer_credentials():
            tweet_id = post_tweet_buffer(tweet_text, article['content_id'])
            mode = "buffer"
        else:
            tweet_id = post_tweet_mock(tweet_text, article['content_id'])
            mode = "mock"
    except Exception as e:
        # Fallback to mock on any error
        print(f"Buffer API error: {e}, falling back to mock")
        tweet_id = post_tweet_mock(tweet_text, article['content_id'])
        mode = "mock_fallback"
    
    mark_posted(article['content_id'], tweet_id)
    
    return {
        "content_id": article['content_id'],
        "title": article['title'],
        "tweet_id": tweet_id,
        "tweet_text": tweet_text,
        "mode": mode
    }
