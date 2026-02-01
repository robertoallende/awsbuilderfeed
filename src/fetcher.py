import httpx
import json
from pathlib import Path
from typing import List, Dict
import os
from config import BUILDER_API_URL, BUILDER_BASE_URL
from src.database import add_article
from src.spam_filter import check_spam


def fetch_feed() -> List[Dict]:
    """Fetch articles from AWS Builder feed API."""
    payload = {
        "contentType": "ARTICLE",
        "sort": {"article": {"sortOrder": "NEWEST"}}
    }
    
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "builder-session-token": "dummy",
        "origin": "https://builder.aws.com",
        "referer": "https://builder.aws.com/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
    
    try:
        response = httpx.post(BUILDER_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("feedContents", [])
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Fallback to cached feed
            print("⚠️  API requires authentication, using cached feed")
            feed_path = Path(__file__).parent.parent / "tmp" / "feed.json"
            if feed_path.exists():
                with open(feed_path) as f:
                    data = json.load(f)
                    return data.get("feedContents", [])
            raise Exception("No cached feed available and API requires authentication")
        raise


def parse_article(raw: dict) -> dict:
    """Parse raw API article into database format."""
    author = raw.get("author", {})
    article_data = raw.get("contentTypeSpecificResponse", {}).get("article", {})
    tags = article_data.get("tags", [])
    
    return {
        "content_id": raw["contentId"],
        "title": raw["title"],
        "author_name": author.get("preferredName"),
        "author_alias": author.get("alias"),
        "description": article_data.get("description"),
        "url": f"{BUILDER_BASE_URL}{raw['contentId']}",
        "tags": ",".join(tags) if tags else None,
        "created_at": raw.get("createdAt"),
        "published_at": raw.get("lastPublishedAt")
    }


def process_articles() -> dict:
    """Fetch and add new articles to database. Returns stats."""
    articles = fetch_feed()
    
    added = 0
    skipped = 0
    spam_detected = 0
    
    for raw in articles:
        article = parse_article(raw)
        
        # Check for spam
        is_spam, matched_rules = check_spam(article)
        
        if add_article(article, is_spam=is_spam):
            if is_spam:
                spam_detected += 1
                print(f"🚫 SPAM detected: {article['title'][:60]}... (rules: {', '.join(matched_rules)})")
            else:
                added += 1
        else:
            skipped += 1
    
    return {
        "fetched": len(articles),
        "added": added,
        "skipped": skipped,
        "spam_detected": spam_detected
    }
