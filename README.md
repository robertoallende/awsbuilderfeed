# BuilderFeed Twitter Bot

Automated pipeline to fetch AWS Builder articles and post them to Twitter/X.

**Follow the bot:** [@uAWSBuilderFeed](https://x.com/uAWSBuilderFeed)

## What This Does

This bot automatically:
1. **Fetches** new articles from [AWS Builder](https://builder.aws.com) every hour
2. **Formats** tweets with title, hashtags, and URL
3. **Posts** one article per hour to Twitter via Make.com → Buffer
4. **Prevents** duplicate posts using SQLite database

## Architecture

```
Prefect (Scheduler)
    ↓ Every hour
Fetch Articles → SQLite Queue
    ↓ Every hour
Post Tweet → Make.com Webhook → Buffer → Twitter
```

**Key Features:**
- ✅ LIFO queue ensures articles posted in order
- ✅ Duplicate detection (never posts same article twice)
- ✅ Hashtags from article tags (first 3)
- ✅ Automatic scheduling with Prefect
- ✅ Webhook delivery for instant posting

## Setup

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
PYTHONPATH=. python -c "from src.database import init_db; init_db()"
```

### 3. Configure Make.com Webhook (Optional)

For automated posting to Twitter:

1. Create webhook in [Make.com](https://make.com)
2. Connect to Buffer → Twitter
3. Add to `.env`:
   ```bash
   MAKECOM_WEBHOOK_URL=https://hook.us2.make.com/your_webhook
   MAKECOM_API_KEY=your_api_key
   ```

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) for detailed instructions.

## Usage

### Manual Testing

```bash
# Fetch articles
PYTHONPATH=. python -c "from src.fetcher import process_articles; print(process_articles())"

# Post one tweet
PYTHONPATH=. python -c "from src.twitter import post_tweet; result = post_tweet(); print(f'Mode: {result[\"mode\"]}')"
```

### Run with Prefect

**Terminal 1 - Start Prefect Server:**
```bash
prefect server start
```

**Terminal 2 - Deploy Flows:**
```bash
source .venv/bin/activate
PYTHONPATH=. python deploy.py
```

**Monitor:** Open http://localhost:4200

### Utility Scripts

```bash
./scripts/reset_db.sh   # Reset database and fetch articles
./scripts/delete_db.sh  # Delete database only
```

## Project Structure

```
builderfeed/
├── src/
│   ├── database.py    # SQLite operations
│   ├── fetcher.py     # AWS Builder API
│   ├── twitter.py     # Tweet formatting & webhook
│   └── flows.py       # Prefect flows
├── data/
│   ├── builderfeed.db      # SQLite database
│   ├── tweets_queue.json   # JSON backup
│   └── mock_tweets.txt     # Human-readable log
├── scripts/
│   ├── reset_db.sh         # Reset database
│   └── delete_db.sh        # Delete database
├── deploy.py          # Prefect deployment
├── config.py          # Configuration
└── dev_log/           # MMDD development log
```

## Schedules

- **Fetch Flow**: Every hour (`0 * * * *`)
- **Tweet Flow**: Every hour (`0 * * * *`)

## Tweet Format

```
Article Title

#hashtag1 #hashtag2 #hashtag3

https://builder.aws.com/content/...
```

## Cost

**Free Tier:**
- Make.com: 1,000 operations/month
- Buffer: 10 scheduled posts
- **Total: $0**

**Unlimited:**
- Buffer Essentials: $6/month
- **Total: $6/month**

vs Twitter API: $100/month ❌

## Development

Built using **MMDD (Micromanaged Driven Development)** methodology.

See `dev_log/` for complete development history:
- Unit 01: Database setup
- Unit 02: Article fetching
- Unit 03: Tweet formatting
- Unit 04: Prefect orchestration
- Unit 05: Make.com integration

## Tech Stack

- **Python 3.12+**
- **Prefect 3.x** - Workflow orchestration
- **SQLite** - Article queue and duplicate tracking
- **httpx** - HTTP client for API calls
- **Make.com** - Webhook automation
- **Buffer** - Social media scheduling

## Links

- **Twitter Bot:** [@uAWSBuilderFeed](https://x.com/uAWSBuilderFeed)
- **AWS Builder:** https://builder.aws.com
- **Make.com:** https://make.com
- **Buffer:** https://buffer.com
- **Prefect:** https://prefect.io

## License

MIT License - See [LICENSE](LICENSE) file
