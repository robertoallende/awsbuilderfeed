# Unit 08: Webhook Failure Handling

## Objective

Fix webhook failure handling to properly fail the flow and NOT mark articles as posted when the webhook returns an error.

## Problem

Current behavior when webhook fails (410 Gone):
1. ✅ Logs webhook error
2. ❌ Falls back to JSON file
3. ❌ Marks article as posted in database
4. ❌ Flow completes successfully

**This is incorrect.** If the webhook fails, the article should NOT be marked as posted, and the flow should fail.

## Current Code Issue

**src/twitter.py** - `post_tweet()`:
```python
# Tries webhook
# If webhook fails, falls back to JSON
# Marks article as posted regardless
# Returns success
```

## Desired Behavior

When webhook fails:
1. ✅ Log webhook error
2. ✅ Raise exception (fail the flow)
3. ✅ Do NOT mark article as posted
4. ✅ Article remains in queue for retry
5. ✅ Flow shows as Failed in Prefect UI

## Implementation Plan

### Changes to src/twitter.py

**Option 1: Remove fallback entirely**
```python
def post_tweet():
    article = get_next_article()
    if not article:
        return None
    
    tweet_text = format_tweet(article)
    
    # Try webhook - if it fails, raise exception
    try:
        post_tweet_webhook(tweet_text, article)
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        raise  # Re-raise to fail the flow
    
    # Only mark as posted if webhook succeeded
    mark_posted(article['content_id'])
    return result
```

**Option 2: Remove JSON fallback from post_tweet()**
- Keep JSON file functionality for manual/testing use
- But don't use it as automatic fallback in production flow

## Files to Modify

1. **src/twitter.py**
   - Remove JSON fallback from `post_tweet()`
   - Ensure exceptions propagate up
   - Only call `mark_posted()` after successful webhook

2. **src/flows.py** (if needed)
   - Ensure task failures are properly logged
   - May need to adjust retry logic

## Testing

1. Simulate webhook failure
2. Verify flow fails (not completes)
3. Verify article NOT marked as posted
4. Verify article remains in queue
5. Check Prefect UI shows failed run

## Success Criteria

- [ ] Webhook failure causes flow to fail
- [ ] Article NOT marked as posted on webhook failure
- [ ] Article remains in queue for retry
- [ ] Prefect UI shows failed run
- [ ] Error is clearly logged

## Status: Complete ✅

**Implemented:**
- ✅ Removed JSON fallback from `post_tweet()`
- ✅ Webhook failures now propagate as exceptions
- ✅ Article NOT marked as posted on webhook failure
- ✅ Article remains in queue for retry
- ✅ Flow will fail in Prefect UI on webhook error

**Changes:**
- Modified `post_tweet()` to raise exception if webhook fails
- Removed try/except fallback logic
- Added check for missing MAKECOM_WEBHOOK_URL
- Only calls `mark_posted()` after successful webhook

**Behavior:**
- Webhook success → article marked as posted, flow succeeds
- Webhook failure → exception raised, article stays in queue, flow fails
- Empty queue → returns None, flow succeeds (no work to do)

Next: Test with production to verify proper failure handling.
