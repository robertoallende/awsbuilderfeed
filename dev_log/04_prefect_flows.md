# Unit 04: Prefect Flows & Scheduling

## Objective

Orchestrate the pipeline with Prefect:
- Create fetch flow (periodically fetches new articles)
- Create tweet flow (posts one article every hour)
- Set up scheduling with `.serve()`
- Add logging and error handling
- Test flows locally

## Implementation

### Flows Module (src/flows.py)

**Fetch Flow:**
- Task: fetch_articles_task() - calls process_articles()
- Schedule: Every 6 hours (check for new articles)
- Logs: articles fetched, added, skipped

**Tweet Flow:**
- Task: post_tweet_task() - calls post_tweet()
- Schedule: Every hour (post one article)
- Logs: article posted or queue empty
- Handles empty queue gracefully

**Deployment:**
```python
if __name__ == "__main__":
    # Serve both flows with schedules
    fetch_flow.serve(
        name="fetch-articles",
        cron="0 */6 * * *"  # Every 6 hours
    )
    
    tweet_flow.serve(
        name="post-tweets",
        cron="0 * * * *"  # Every hour
    )
```

### Prefect Features Used

- `@flow` decorator for flows
- `@task` decorator for tasks
- `get_run_logger()` for logging
- `.serve()` for scheduling
- Cron schedules

## AI Interactions

Use AI to:
1. Create clean Prefect flow structure
2. Add proper logging with get_run_logger()
3. Handle edge cases (empty queue, API errors)

## Files Modified

- `src/flows.py` (new)

## Status: Complete

**Implemented:**
- ✅ fetch_flow: Prefect flow to fetch articles periodically
- ✅ tweet_flow: Prefect flow to post one tweet per hour
- ✅ Tasks with retries and logging (fetch_articles_task, post_tweet_task)
- ✅ deploy.py: Deployment script with cron schedules
- ✅ README.md: Complete usage documentation
- ✅ Virtual environment setup

**Schedules:**
- Fetch: Every 6 hours (`0 */6 * * *`)
- Tweet: Every hour (`0 * * * *`)

**Validation:**
- Flows tested successfully
- Fetch flow: 10 fetched, 0 added, 10 skipped (duplicates working)
- Tweet flow: Posted 1 tweet, queue 6 pending, 4 posted
- Logging working with get_run_logger()
- Prefect temporary server started automatically

**Usage:**
```bash
# Test manually
PYTHONPATH=. python src/flows.py

# Deploy with scheduling
prefect server start  # Terminal 1
PYTHONPATH=. python deploy.py  # Terminal 2
```

Next: Unit 05 - Twitter API Integration (replace mock with real API)
