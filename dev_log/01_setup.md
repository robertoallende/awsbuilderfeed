# Unit 01: Project Setup & Database Schema

## Objective

Set up the project foundation with:
- Python dependencies (Prefect, httpx, sqlite3)
- SQLite database schema for articles queue and tweet log
- Basic project structure (src/, data/)
- Configuration management

## Implementation

### Database Schema

**articles table** (FIFO queue):
```sql
CREATE TABLE articles (
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
);
```

**tweet_log table** (duplicate prevention):
```sql
CREATE TABLE tweet_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    tweeted_at INTEGER NOT NULL,
    tweet_id TEXT
);
```

### Project Structure
```
builderfeed/
├── src/
│   ├── __init__.py
│   ├── database.py      # DB operations
│   ├── fetcher.py       # AWS Builder API
│   ├── twitter.py       # Twitter/mock posting
│   └── flows.py         # Prefect flows
├── data/
│   └── builderfeed.db   # SQLite database
├── config.py            # Configuration
├── requirements.txt
└── dev_log/
```

### Dependencies
- prefect>=3.0.0
- httpx
- python-dotenv (for config)

## AI Interactions

Will use AI to:
1. Generate clean database initialization code
2. Create minimal database operations (add, get_next, mark_posted)
3. Set up project structure

## Files Modified

- `requirements.txt` (new)
- `src/database.py` (new)
- `src/__init__.py` (new)
- `config.py` (new)
- `data/builderfeed.db` (created)

## Status: Not Started

Next: Implement database schema and basic operations
