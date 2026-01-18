from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import httpx
from config import MOCK_TWEETS_FILE, TWEETS_QUEUE_FILE, MAKECOM_WEBHOOK_URL
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


def post_tweet_webhook(tweet_text: str, article: dict) -> str:
    """Send tweet to Make.com webhook. Returns tweet_id."""
    tweet_id = f"tweet_{int(datetime.now().timestamp())}"
    
    payload = {
        "id": tweet_id,
        "content_id": article['content_id'],
        "text": tweet_text,
        "url": article['url'],
        "title": article['title'],
        "posted_at": int(datetime.now().timestamp()),
        "status": "pending"
    }
    
    response = httpx.post(MAKECOM_WEBHOOK_URL, json=payload, timeout=30)
    response.raise_for_status()
    
    return tweet_id


def post_tweet_json(tweet_text: str, article: dict) -> str:
    """Write tweet to JSON queue for Make.com. Returns tweet_id."""
    TWEETS_QUEUE_FILE.parent.mkdir(exist_ok=True)
    
    tweet_id = f"tweet_{int(datetime.now().timestamp())}"
    
    # Read existing queue
    queue = []
    if TWEETS_QUEUE_FILE.exists():
        with open(TWEETS_QUEUE_FILE, 'r') as f:
            try:
                queue = json.load(f)
            except json.JSONDecodeError:
                queue = []
    
    # Add new tweet
    tweet_entry = {
        "id": tweet_id,
        "content_id": article['content_id'],
        "text": tweet_text,
        "url": article['url'],
        "title": article['title'],
        "posted_at": int(datetime.now().timestamp()),
        "status": "pending"
    }
    queue.append(tweet_entry)
    
    # Write back to file
    with open(TWEETS_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
    
    return tweet_id


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
    
    # Try webhook first, fallback to JSON file, then mock
    mode = "json_queue"
    try:
        if MAKECOM_WEBHOOK_URL:
            tweet_id = post_tweet_webhook(tweet_text, article)
            mode = "webhook"
        else:
            tweet_id = post_tweet_json(tweet_text, article)
            mode = "json_queue"
    except Exception as e:
        print(f"Webhook error: {e}, falling back to JSON file")
        tweet_id = post_tweet_json(tweet_text, article)
        mode = "json_fallback"
    
    # Always write to mock file for backup
    post_tweet_mock(tweet_text, article['content_id'])
    
    mark_posted(article['content_id'], tweet_id)
    
    return {
        "content_id": article['content_id'],
        "title": article['title'],
        "tweet_id": tweet_id,
        "tweet_text": tweet_text,
        "mode": mode
    }
