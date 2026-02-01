# BuilderFeed Twitter Bot - Project Plan and Dev Log

Automated pipeline to fetch AWS Builder articles and post them to Twitter/X using Prefect orchestration.

## Structure

Units are organized in `dev_log/` with naming: `<sequence>_<unitname>[_subunit<number|name>].md`

Files are ordered numerically to allow flexible sequencing.

## About the Project

### What This Is

An automated Twitter bot that:
- Fetches articles from AWS Builder feed API
- Stores new articles in a SQLite FIFO queue
- Posts one article per hour to Twitter/X
- Prevents duplicate posts and respects X platform rules

### Architecture

```
┌─────────────────┐
│  Prefect Flow   │
│   (Scheduler)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐ ┌─▼──────┐
│ Fetch  │ │ Tweet  │
│ Task   │ │ Task   │
└───┬────┘ └─┬──────┘
    │        │
┌───▼────────▼───┐
│  SQLite DB     │
│  - articles    │
│  - tweet_log   │
└────────────────┘
```

**Components:**
1. **Fetch Flow**: Runs periodically, fetches new articles, adds to queue
2. **Tweet Flow**: Runs hourly, posts one article from queue
3. **SQLite Database**: 
   - `articles` table: FIFO queue of unposted articles
   - `tweet_log` table: History of posted articles (duplicate prevention)

### Technical Stack

- **Orchestration**: Prefect 3.x
- **Database**: SQLite3
- **HTTP Client**: httpx (for API calls)
- **Twitter Integration**: Initially mocked (file output), then Twitter API
- **Language**: Python 3.12+

## Project Status

### Overall Completion
100% - All units complete including spam detection! 🎉

### Completed Features
- SQLite database with FIFO queue and duplicate prevention
- Database operations (add, get_next, mark_posted, stats)
- AWS Builder API fetching with duplicate detection
- Article parsing and URL generation
- Tweet formatting with hashtags (first 3 tags)
- Tweet logging and tracking
- Prefect orchestration with fetch and tweet flows
- Scheduled deployments (1 hour fetch, 1 hour tweet)
- JSON queue output for Make.com automation (→ Buffer → Twitter)
- Raspberry Pi deployment with systemd services
- **Spam detection with 95.3% accuracy**

## Units Implemented

### Completed Units
* **01**: Project Setup & Database Schema - SQLite FIFO queue, database operations, project structure
* **02**: Fetch Articles Task - AWS Builder API integration, duplicate detection, article parsing
* **03**: Tweet Task (Mocked) - Tweet formatting, mock posting to file, character limit handling
* **04**: Prefect Flows & Scheduling - Orchestration with fetch/tweet flows, cron schedules, deployment
* **05**: Make.com Integration - JSON queue output for Make.com → Buffer → Twitter automation
* **06**: Raspberry Pi Deployment - Systemd services, nginx reverse proxy, production setup
* **07**: Spam Detection - Rule-based spam filtering (95.3% detection rate, 0% false positives)
* **08**: Prefect Naming Convention - Updated flow names for shared Prefect server visual separation

### Units In Progress

None - All units complete!

### Planned Units

None
