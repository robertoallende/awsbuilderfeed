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
0% - Planning phase

### Completed Features
None yet

## Units Implemented

### Completed Units
None yet

### Units In Progress

#### 01. Project Setup & Database Schema
**Status:** Not started

### Planned Units

* **01**: Project Setup & Database Schema - Initialize project structure, SQLite schema, dependencies
* **02**: Fetch Articles Task - Implement AWS Builder API fetching with duplicate detection
* **03**: Tweet Task (Mocked) - Create tweet posting logic with file output
* **04**: Prefect Flows & Scheduling - Orchestrate fetch and tweet flows with hourly schedule
* **05**: Twitter API Integration - Replace mock with real Twitter API calls
