# Make.com Setup Guide

Complete guide to automate posting tweets from BuilderFeed to Twitter via Buffer.

## Prerequisites

1. **Buffer account** with Twitter connected
   - Go to https://buffer.com
   - Sign up (free tier: 10 posts)
   - Connect your Twitter account

2. **Make.com account**
   - Go to https://make.com
   - Sign up (free tier: 1,000 operations/month)

## Step 1: Set Up File Access

### Option A: Use Dropbox (Recommended)
1. Create Dropbox account (free)
2. Install Dropbox on your computer
3. Move `builderfeed/data/tweets_queue.json` to Dropbox folder
4. Update symlink:
   ```bash
   cd /Users/robertoallende/code/builderfeed/data
   rm tweets_queue.json
   ln -s ~/Dropbox/builderfeed/tweets_queue.json tweets_queue.json
   ```

### Option B: Use Google Drive
1. Upload `tweets_queue.json` to Google Drive
2. Share with Make.com
3. Update path in config.py

### Option C: Use Webhook (Advanced)
- Pipeline sends HTTP POST to Make.com webhook
- No file sync needed

## Step 2: Create Make.com Scenario

1. **Go to Make.com dashboard**
   - Click "Create a new scenario"

2. **Add Trigger: Watch File**
   - Search for "Dropbox" (or "Google Drive")
   - Select "Watch Files"
   - Connect your Dropbox account
   - Set folder: `/builderfeed/`
   - Set file: `tweets_queue.json`
   - Schedule: Every 15 minutes

3. **Add Module: Parse JSON**
   - Search for "JSON"
   - Select "Parse JSON"
   - Map: File content from previous step
   - Data structure: (Make.com will auto-detect)

4. **Add Module: Iterator**
   - Search for "Iterator"
   - Array: Select the parsed JSON array
   - This processes each tweet one by one

5. **Add Module: Filter**
   - Add filter between Iterator and next step
   - Condition: `status` = `pending`
   - This only processes unposted tweets

6. **Add Module: Buffer - Create Post**
   - Search for "Buffer"
   - Select "Create a Post"
   - Connect your Buffer account
   - Map fields:
     - Text: `{{text}}`
     - Profile IDs: Select your Twitter profile
     - Now: `false` (schedule for optimal time)

7. **Add Module: Update JSON (Optional)**
   - To mark tweets as posted
   - Or just let them accumulate

8. **Save and Activate**
   - Click "Save"
   - Toggle "ON"

## Step 3: Test the Scenario

1. **Run the pipeline manually:**
   ```bash
   cd /Users/robertoallende/code/builderfeed
   source .venv/bin/activate
   PYTHONPATH=. python -c "from src.twitter import post_tweet; post_tweet()"
   ```

2. **Check tweets_queue.json:**
   - Should have a new entry with status="pending"

3. **Run Make.com scenario manually:**
   - Click "Run once" in Make.com
   - Watch the execution
   - Check Buffer - tweet should be scheduled

4. **Check Twitter:**
   - Go to Buffer dashboard
   - See scheduled tweet
   - Wait for Buffer to post (or post now)

## Step 4: Monitor

**Make.com Dashboard:**
- View execution history
- See errors if any
- Check operation count (stay under 1,000/month)

**Buffer Dashboard:**
- See scheduled tweets
- Manually adjust timing if needed
- View analytics

## Troubleshooting

### Scenario not triggering
- Check file path in Dropbox/Drive
- Verify schedule is active
- Check Make.com operation limit

### Tweets not posting
- Verify Buffer connection
- Check Twitter profile is selected
- Ensure Buffer has posting permissions

### JSON parse errors
- Validate JSON format in tweets_queue.json
- Check file encoding (should be UTF-8)

## Cost Breakdown

**Free Tier (Limited):**
- Make.com: 1,000 operations/month
- Buffer: 10 scheduled posts
- Cost: $0

**Paid (Unlimited):**
- Make.com: $9/month for 10,000 operations
- Buffer: $6/month for unlimited posts
- Cost: $15/month

**vs Twitter API:** $100/month ❌

## Alternative: Webhook Method

If you don't want to use Dropbox/Drive:

1. **Create webhook in Make.com:**
   - Add "Webhooks" → "Custom webhook"
   - Copy webhook URL

2. **Update pipeline to POST to webhook:**
   ```python
   import httpx
   httpx.post(webhook_url, json=tweet_entry)
   ```

3. **No file sync needed!**

---

**Ready to set up?** Start with Step 1 (Dropbox is easiest) and let me know when you're ready for Step 2!
