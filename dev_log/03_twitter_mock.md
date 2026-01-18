# Unit 03: Tweet Task (Mocked)

## Objective

Implement tweet posting logic with:
- Format tweet text (title + URL, max 280 chars)
- Mock posting (write to file instead of Twitter API)
- Mark article as posted in database
- Handle edge cases (empty queue, long titles)

## Implementation

### Twitter Module (src/twitter.py)

**Key functions:**
- `format_tweet(article)`: Create tweet text from article (title + URL)
- `post_tweet_mock(article)`: Write tweet to mock_tweets.txt file
- `post_tweet(article)`: Main function that posts and marks as posted

**Tweet Format:**
```
{title}

{url}
```

**Character limit:** 280 chars total
- If title too long, truncate with "..."

### Mock Output

Append to `data/mock_tweets.txt`:
```
[2026-01-18 20:15:30] Posted:
How can learning advanced prompt engineering benefit students?

https://builder.aws.com/content/38N2jqfhtSccHsRGkQWyjeflLLO
---
```

## AI Interactions

Use AI to:
1. Create clean tweet formatting logic
2. Handle character limits properly
3. Write mock output with timestamps

## Files Modified

- `src/twitter.py` (new)
- `data/mock_tweets.txt` (created)

## Status: Complete

**Implemented:**
- ✅ format_tweet(): Creates tweet text with title + URL (max 280 chars)
- ✅ post_tweet_mock(): Writes tweets to data/mock_tweets.txt with timestamps
- ✅ post_tweet(): Main function that gets next article, posts, and marks as posted
- ✅ Character limit handling (truncates long titles with "...")
- ✅ Database integration (marks articles as posted, logs to tweet_log)

**Validation:**
- Posted 3 test tweets successfully
- Mock file created with proper format and timestamps
- Queue stats: 7 pending, 3 posted
- Duplicate prevention working (fetch returns 0 added, 10 skipped)
- Tweet character counts within limits (123 chars for first tweet)

**Mock Output Format:**
```
[2026-01-18 20:12:14] Posted (ID: mock_1768720334):
How can learning advanced prompt engineering benefit students?

https://builder.aws.com/content/38N2jqfhtSccHsRGkQWyjeflLLO
---
```

Next: Unit 04 - Prefect Flows & Scheduling
