# Unit 02: Fetch Articles Task

## Objective

Implement AWS Builder API fetching with:
- HTTP client to fetch articles from Builder feed API
- Parse JSON response and extract relevant fields
- Add new articles to SQLite queue
- Duplicate detection (skip already posted/queued articles)
- Error handling and logging

## Implementation

### Fetcher Module (src/fetcher.py)

**Key functions:**
- `fetch_feed()`: Call AWS Builder API, return parsed articles
- `process_articles()`: Add new articles to database, return count added
- Build article URL from content_id

**Article fields to extract:**
- content_id (unique identifier)
- title
- author (preferredName, alias)
- description
- tags (joined as string)
- created_at, published_at timestamps
- Build URL: `https://builder.aws.com/content/{content_id}`

### Duplicate Prevention

Check against both:
1. `tweet_log` table (already posted)
2. `articles` table (already queued)

Only add truly new articles.

## AI Interactions

Use AI to:
1. Create clean HTTP client with httpx
2. Parse Builder API JSON response
3. Handle errors gracefully (network, API changes)

## Files Modified

- `src/fetcher.py` (new)

## Status: Complete

**Implemented:**
- ✅ fetch_feed(): Fetches articles from Builder API (using cached feed.json for now)
- ✅ parse_article(): Extracts all relevant fields from API response
- ✅ process_articles(): Main function that fetches and adds new articles
- ✅ Duplicate detection working (checks both tweet_log and articles tables)
- ✅ Builds proper URLs: https://builder.aws.com/content/{content_id}

**Validation:**
- First run: fetched 10, added 10, skipped 0
- Second run: fetched 10, added 0, skipped 10 (duplicate detection works!)
- Queue stats: 10 pending, 0 posted
- Sample article verified with correct title, author, URL, tags

**Note:** Currently using cached feed.json from tmp/. API authentication with cookies will be added in a future enhancement.

Next: Unit 03 - Tweet Task (Mocked)
