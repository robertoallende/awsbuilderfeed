# Unit 09: Likes-Based Article Ranking

## Objective

Replace FIFO ordering with likes-based ranking to publish the most popular articles first. With posting frequency reduced to every 2 hours, we need to be more selective about what gets published.

## Context

- The individual article API (`/cs/content`) returns `likesCount` and `commentsCount`
- Articles already wait 12 hours before publishing (gives time to accumulate likes)
- The fetch flow runs every hour — ideal time to refresh likes for pending articles
- URL validation (checking if article still exists) can move from publish time to fetch time

## Implementation

### Database Changes

Add `likes_count` column to articles table:
```sql
ALTER TABLE articles ADD COLUMN likes_count INTEGER DEFAULT 0;
```

### Fetch Flow Changes

After fetching new articles, update likes for all pending articles:

```
Fetch Flow (every hour):
  1. Fetch new articles from feed → add to DB (existing)
  2. Update likes for all pending articles:
     - Hit individual article API for each pending article
     - Update likes_count in DB
     - If article returns 404 → mark as spam (replaces publish-time validation)
```

### Publish Flow Changes

Sort by likes instead of publish date:
```sql
SELECT * FROM articles
WHERE posted = 0 AND is_spam = 0 AND fetched_at <= ?
ORDER BY likes_count DESC, published_at ASC
LIMIT 1
```

No more API validation at publish time — already done during fetch.

### API Response (available fields)

```json
{
  "likesCount": 1,
  "commentsCount": 0,
  "isFlagged": false,
  "locale": "en"
}
```

## Files Modified

- `src/database.py` — Add likes_count column, update get_next_article() ordering, add update_likes_count()
- `src/fetcher.py` — Add update_likes() function to refresh likes for pending articles
- `src/flows.py` — Integrate update_likes into fetch flow

## Status: Complete ✅

**Implemented:**
- ✅ Added `likes_count` column to articles table
- ✅ `get_pending_articles()` and `update_likes_count()` in database.py
- ✅ `update_likes()` in fetcher.py — refreshes likes for all pending articles each fetch cycle
- ✅ `update_likes_task` in flows.py — integrated into fetch_flow
- ✅ `get_next_article()` now sorts by `likes_count DESC, published_at ASC`
- ✅ Removed redundant per-article API validation at publish time (now done during fetch)

**Test Results:**
- update_likes() updated 21 pending articles, caught 8 removed articles (auto-marked spam)
- Likes range: 0-5 for pending articles
- get_next_article() correctly picks highest-liked article (5 likes, "Getting started with Amazon Quick Suite")
- Flows import and run cleanly

**Production Deployment:**
1. `ALTER TABLE articles ADD COLUMN likes_count INTEGER DEFAULT 0;` on production DB
2. Copy updated src/ files to production
3. Restart builderfeed service

## Deployment

### 1. Update database schema on production

```bash
ssh rover@192.168.4.200
sqlite3 /home/rover/prefect/awsbuilderfeed/data/builderfeed.db "ALTER TABLE articles ADD COLUMN likes_count INTEGER DEFAULT 0;"
```

### 2. Copy updated files to production

```bash
scp src/database.py src/fetcher.py src/flows.py rover@192.168.4.200:/home/rover/prefect/awsbuilderfeed/src/
```

### 3. Update tweet schedule to every 2 hours

Update `deploy.py` cron from `0 * * * *` to `0 */2 * * *` for the tweet flow, then copy:
```bash
scp deploy.py rover@192.168.4.200:/home/rover/prefect/awsbuilderfeed/
```

### 4. Restart service

```bash
ssh rover@192.168.4.200 "sudo systemctl restart builderfeed"
```

### 5. Verify

```bash
ssh rover@192.168.4.200 "sudo systemctl status builderfeed"
ssh rover@192.168.4.200 "journalctl -u builderfeed -f"
```
