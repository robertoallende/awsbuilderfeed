# BuilderFeed Twitter Bot

Automated pipeline to fetch AWS Builder articles and post them to Twitter/X.

## Setup

1. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
PYTHONPATH=. python -c "from src.database import init_db; init_db()"
```

## Usage

### Test Flows Manually
```bash
PYTHONPATH=. python src/flows.py
```

### Deploy with Scheduling

1. Start Prefect server (in separate terminal):
```bash
prefect server start
```

2. Deploy flows:
```bash
PYTHONPATH=. python deploy.py
```

This will:
- Fetch articles every 6 hours
- Post one tweet every hour
- Run continuously until stopped (Ctrl+C)

### Monitor

Open http://localhost:4200 to view:
- Flow runs
- Task logs
- Schedules
- Queue statistics

## Project Structure

```
builderfeed/
├── src/
│   ├── database.py    # SQLite operations
│   ├── fetcher.py     # AWS Builder API
│   ├── twitter.py     # Tweet posting (mocked)
│   └── flows.py       # Prefect flows
├── data/
│   ├── builderfeed.db      # SQLite database
│   └── mock_tweets.txt     # Mock tweet output
├── deploy.py          # Deployment with schedules
└── config.py          # Configuration
```

## Schedules

- **Fetch Flow**: Every 6 hours (`0 */6 * * *`)
- **Tweet Flow**: Every hour (`0 * * * *`)
