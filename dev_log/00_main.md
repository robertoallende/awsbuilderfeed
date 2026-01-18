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
80% - Units 01-04 complete

### Completed Features
- SQLite database with FIFO queue and duplicate prevention
- Database operations (add, get_next, mark_posted, stats)
- AWS Builder API fetching with duplicate detection
- Article parsing and URL generation
- Mock tweet posting with character limit handling
- Tweet logging and tracking
- Prefect orchestration with fetch and tweet flows
- Scheduled deployments (6 hours fetch, 1 hour tweet)

## Units Implemented

### Completed Units
* **01**: Project Setup & Database Schema - SQLite FIFO queue, database operations, project structure
* **02**: Fetch Articles Task - AWS Builder API integration, duplicate detection, article parsing
* **03**: Tweet Task (Mocked) - Tweet formatting, mock posting to file, character limit handling
* **04**: Prefect Flows & Scheduling - Orchestration with fetch/tweet flows, cron schedules, deployment

### Units In Progress

None

### Planned Units

* **05**: Twitter API Integration - Replace mock with real Twitter API calls (optional enhancement)

### Planned Units

* **01**: Project Setup & Database Schema - Initialize project structure, SQLite schema, dependencies
* **02**: Fetch Articles Task - Implement AWS Builder API fetching with duplicate detection
* **03**: Tweet Task (Mocked) - Create tweet posting logic with file output
* **04**: Prefect Flows & Scheduling - Orchestrate fetch and tweet flows with hourly schedule
* **05**: Twitter API Integration - Replace mock with real Twitter API calls
