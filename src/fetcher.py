import httpx
import json
from pathlib import Path
from typing import List, Dict
from config import BUILDER_API_URL, BUILDER_BASE_URL
from src.database import add_article


def fetch_feed() -> List[Dict]:
    """Fetch articles from AWS Builder feed API."""
    # TODO: Add cookie authentication when available
    # For now, use cached feed.json
    feed_path = Path(__file__).parent.parent / "tmp" / "feed.json"
    
    if feed_path.exists():
        with open(feed_path) as f:
            data = json.load(f)
            return data.get("feedContents", [])
    
    # Fallback to API (will fail without auth for now)
    payload = {
        "contentType": "ARTICLE",
        "sort": {"article": {"sortOrder": "NEWEST"}}
    }
    
    headers = {
        "content-type": "application/json",
        "accept": "*/*"
    }
    
    response = httpx.post(BUILDER_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return data.get("feedContents", [])


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
    
    for raw in articles:
        article = parse_article(raw)
        if add_article(article):
            added += 1
        else:
            skipped += 1
    
    return {
        "fetched": len(articles),
        "added": added,
        "skipped": skipped
    }
