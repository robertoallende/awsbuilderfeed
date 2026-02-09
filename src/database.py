import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "builderfeed.db"


def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author_name TEXT,
            author_alias TEXT,
            description TEXT,
            url TEXT NOT NULL,
            tags TEXT,
            created_at INTEGER,
            published_at INTEGER,
            fetched_at INTEGER NOT NULL,
            posted BOOLEAN DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweet_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            tweeted_at INTEGER NOT NULL,
            tweet_id TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def add_article(article: dict, is_spam: bool = False) -> bool:
    """Add article to queue if not already posted. Returns True if added."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if already posted
    cursor.execute("SELECT 1 FROM tweet_log WHERE content_id = ?", (article['content_id'],))
    if cursor.fetchone():
        conn.close()
        return False
    
    # Check if already in queue
    cursor.execute("SELECT 1 FROM articles WHERE content_id = ?", (article['content_id'],))
    if cursor.fetchone():
        conn.close()
        return False
    
    # Add to queue
    cursor.execute("""
        INSERT INTO articles (content_id, title, author_name, author_alias, 
                            description, url, tags, created_at, published_at, fetched_at, is_spam)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article['content_id'],
        article['title'],
        article.get('author_name'),
        article.get('author_alias'),
        article.get('description'),
        article['url'],
        article.get('tags'),
        article.get('created_at'),
        article.get('published_at'),
        int(datetime.now().timestamp()),
        1 if is_spam else 0
    ))
    
    conn.commit()
    conn.close()
    return True


def get_next_article() -> Optional[dict]:
    """Get next unposted, non-spam article - oldest published first.
    Only returns articles 12+ hours old with valid URLs (200 status from API)."""
    import httpx
    import time
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get articles 12+ hours old
    twelve_hours_ago = int(time.time() * 1000) - (12 * 60 * 60 * 1000)
    
    cursor.execute("""
        SELECT * FROM articles 
        WHERE posted = 0 AND is_spam = 0 AND fetched_at <= ?
        ORDER BY published_at ASC 
        LIMIT 10
    """, (twelve_hours_ago,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Check each article's URL via API until we find a valid one
    headers = {
        'accept': '*/*',
        'builder-session-token': 'dummy',
        'origin': 'https://builder.aws.com',
        'referer': 'https://builder.aws.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    for row in rows:
        article = dict(row)
        content_id = article['content_id'].replace('/content/', '')
        api_url = f'https://api.builder.aws.com/cs/content?cid=%2Fcontent%2F{content_id}&commentSort=NEWEST&type=ARTICLE'
        
        try:
            response = httpx.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return article
            else:
                print(f"Article removed (status {response.status_code}), marking as spam: {article['title'][:50]}")
                mark_article_spam(article['content_id'])
        except Exception as e:
            print(f"Error checking article {article['title'][:50]}: {e}")
            mark_article_spam(article['content_id'])
    
    return None


def mark_article_spam(content_id: str):
    """Mark an article as spam (e.g., when API validation fails)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE articles 
        SET is_spam = 1 
        WHERE content_id = ?
    """, (content_id,))
    
    conn.commit()
    conn.close()


def mark_posted(content_id: str, tweet_id: Optional[str] = None):
    """Mark article as posted and log to tweet_log."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get article details
    cursor.execute("SELECT title, url FROM articles WHERE content_id = ?", (content_id,))
    row = cursor.fetchone()
    
    if row:
        title, url = row
        
        # Mark as posted
        cursor.execute("UPDATE articles SET posted = 1 WHERE content_id = ?", (content_id,))
        
        # Add to tweet log
        cursor.execute("""
            INSERT INTO tweet_log (content_id, title, url, tweeted_at, tweet_id)
            VALUES (?, ?, ?, ?, ?)
        """, (content_id, title, url, int(datetime.now().timestamp()), tweet_id))
        
        conn.commit()
    
    conn.close()


def get_stats() -> dict:
    """Get queue statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM articles WHERE posted = 0 AND is_spam = 0")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM articles WHERE is_spam = 1")
    spam = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tweet_log")
    posted = cursor.fetchone()[0]
    
    conn.close()
    
    return {"pending": pending, "posted": posted, "spam": spam}
