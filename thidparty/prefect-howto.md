# Prefect Workflow Orchestration How-To Guide

A practical guide for building production-ready data pipelines with Prefect, focusing on workflow orchestration, scheduling, and deployment.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [Creating Flows](#creating-flows)
4. [Working with Tasks](#working-with-tasks)
5. [Scheduling & Deployments](#scheduling--deployments)
6. [State Management & Retries](#state-management--retries)
7. [Caching & Results](#caching--results)
8. [Logging & Observability](#logging--observability)
9. [Blocks & Configuration](#blocks--configuration)
10. [Production Deployment](#production-deployment)

---

## Installation & Setup

```bash
pip install -U prefect
# or
uv add prefect
```

### Start Prefect Server

```bash
# Start local server with UI at http://localhost:4200
prefect server start
```

### Connect to Prefect Cloud (Optional)

```bash
prefect cloud login
```

---

## Core Concepts

### Flows

Flows are the primary container for workflow logic. They define the orchestration structure.

```python
from prefect import flow

@flow(name="my-workflow")
def my_flow():
    """A simple flow."""
    print("Hello from Prefect!")

if __name__ == "__main__":
    my_flow()
```

### Tasks

Tasks are discrete units of work within flows. They enable granular observability and retry logic.

```python
from prefect import flow, task

@task
def extract_data(source: str) -> dict:
    """Extract data from source."""
    return {"data": f"from {source}"}

@task
def transform_data(data: dict) -> dict:
    """Transform the data."""
    return {"transformed": data}

@flow
def etl_pipeline(source: str):
    raw = extract_data(source)
    transformed = transform_data(raw)
    return transformed

if __name__ == "__main__":
    result = etl_pipeline("database")
```

### Flow Runs vs Task Runs

- **Flow Run**: Each execution of a flow
- **Task Run**: Each execution of a task within a flow
- Both are tracked in the Prefect UI with logs, state, and metadata

---

## Creating Flows

### Basic Flow

```python
from prefect import flow

@flow(log_prints=True)
def hello_flow(name: str = "World"):
    print(f"Hello, {name}!")

hello_flow("Prefect")
```

### Flow with Parameters

```python
from prefect import flow, task

@task
def fetch_data(url: str) -> dict:
    import httpx
    return httpx.get(url).json()

@flow
def data_pipeline(api_url: str, limit: int = 10):
    data = fetch_data(api_url)
    print(f"Fetched {len(data)} items, limit: {limit}")
    return data[:limit]

if __name__ == "__main__":
    data_pipeline("https://api.example.com/data", limit=5)
```

### Subflows

```python
from prefect import flow

@flow
def process_batch(batch_id: int):
    print(f"Processing batch {batch_id}")
    return f"batch_{batch_id}_complete"

@flow
def main_pipeline(num_batches: int):
    results = []
    for i in range(num_batches):
        result = process_batch(i)
        results.append(result)
    return results

if __name__ == "__main__":
    main_pipeline(3)
```

### Async Flows

```python
from prefect import flow, task
import asyncio

@task
async def fetch_async(url: str) -> dict:
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@flow
async def async_pipeline(urls: list[str]):
    tasks = [fetch_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    urls = ["https://api.github.com/repos/PrefectHQ/prefect"]
    asyncio.run(async_pipeline(urls))
```

---

## Working with Tasks

### Task Configuration

```python
from prefect import task, flow
from datetime import timedelta

@task(
    name="fetch-data",
    description="Fetch data from API",
    tags=["api", "extract"],
    retries=3,
    retry_delay_seconds=60,
    timeout_seconds=300
)
def fetch_data(endpoint: str):
    # Task logic
    return {"data": "fetched"}

@flow
def pipeline():
    data = fetch_data("/api/data")
```

### Task Dependencies

```python
from prefect import flow, task

@task
def task_a():
    return "A"

@task
def task_b():
    return "B"

@task
def task_c(a_result, b_result):
    return f"{a_result} + {b_result}"

@flow
def dependency_flow():
    a = task_a()
    b = task_b()
    c = task_c(a, b)  # Runs after a and b complete
    return c
```

### Parallel Task Execution

```python
from prefect import flow, task

@task
def process_item(item: int) -> int:
    return item * 2

@flow
def parallel_processing(items: list[int]):
    # Tasks run concurrently
    results = [process_item(item) for item in items]
    return results

if __name__ == "__main__":
    parallel_processing([1, 2, 3, 4, 5])
```

### Task Results

```python
from prefect import flow, task

@task
def compute():
    return {"value": 42}

@flow
def result_flow():
    result = compute()
    # Access result directly
    print(f"Result: {result}")
    return result
```

---

## Scheduling & Deployments

### Simple Deployment with Serve

```python
from prefect import flow

@flow
def scheduled_flow():
    print("Running on schedule!")

if __name__ == "__main__":
    scheduled_flow.serve(
        name="my-deployment",
        cron="0 9 * * *",  # Daily at 9 AM
        tags=["production"]
    )
```

### Multiple Schedules

```python
from prefect import flow
from prefect.client.schemas.schedules import CronSchedule, IntervalSchedule
from datetime import timedelta

@flow
def multi_schedule_flow():
    print("Running on multiple schedules")

if __name__ == "__main__":
    multi_schedule_flow.serve(
        name="multi-schedule",
        schedules=[
            CronSchedule(cron="0 */6 * * *"),  # Every 6 hours
            IntervalSchedule(interval=timedelta(hours=1))  # Every hour
        ]
    )
```

### Deployment with Parameters

```python
from prefect import flow

@flow
def parameterized_flow(env: str, batch_size: int):
    print(f"Running in {env} with batch size {batch_size}")

if __name__ == "__main__":
    parameterized_flow.serve(
        name="prod-deployment",
        cron="0 0 * * *",
        parameters={"env": "production", "batch_size": 1000}
    )
```

### Deploy to Work Pool

```python
from prefect import flow

@flow
def production_flow():
    print("Running in production")

if __name__ == "__main__":
    production_flow.deploy(
        name="prod-deployment",
        work_pool_name="kubernetes-pool",
        cron="0 0 * * *",
        image="my-registry/my-image:latest"
    )
```

---

## State Management & Retries

### Task Retries

```python
from prefect import task, flow

@task(retries=3, retry_delay_seconds=60)
def flaky_task():
    import random
    if random.random() < 0.7:
        raise Exception("Random failure")
    return "Success"

@flow
def retry_flow():
    result = flaky_task()
    return result
```

### Custom Retry Logic

```python
from prefect import task, flow
from prefect.tasks import exponential_backoff

@task(
    retries=5,
    retry_delay_seconds=exponential_backoff(backoff_factor=2)
)
def api_call():
    # Will retry with exponential backoff: 2s, 4s, 8s, 16s, 32s
    pass
```

### Flow State Handlers

```python
from prefect import flow
from prefect.states import Completed, Failed

def on_completion(flow, flow_run, state):
    print(f"Flow {flow.name} completed!")

def on_failure(flow, flow_run, state):
    print(f"Flow {flow.name} failed!")
    # Send alert, log to monitoring system, etc.

@flow(
    on_completion=[on_completion],
    on_failure=[on_failure]
)
def monitored_flow():
    print("Running flow")
```

### Manual State Management

```python
from prefect import flow, task
from prefect.states import Completed, Failed

@task
def conditional_task(should_fail: bool):
    if should_fail:
        return Failed(message="Task failed intentionally")
    return Completed(message="Task succeeded")

@flow
def state_flow():
    result = conditional_task(False)
```

---

## Caching & Results

### Task Result Caching

```python
from prefect import task, flow
from datetime import timedelta

@task(cache_key_fn=lambda *args, **kwargs: "static-key", 
      cache_expiration=timedelta(hours=1))
def expensive_computation():
    print("Computing...")
    return sum(range(1000000))

@flow
def cached_flow():
    # First call computes
    result1 = expensive_computation()
    # Second call uses cache
    result2 = expensive_computation()
    return result1, result2
```

### Input-Based Caching

```python
from prefect import task, flow
from prefect.cache_policies import INPUTS

@task(cache_policy=INPUTS)
def fetch_data(user_id: int):
    print(f"Fetching data for user {user_id}")
    return {"user_id": user_id, "data": "..."}

@flow
def input_cached_flow():
    # Cached per user_id
    user1_data = fetch_data(1)
    user1_again = fetch_data(1)  # Uses cache
    user2_data = fetch_data(2)   # New computation
```

### Result Persistence

```python
from prefect import flow, task
from prefect.filesystems import LocalFileSystem

@task(persist_result=True)
def generate_report():
    return {"report": "data"}

@flow(persist_result=True)
def reporting_flow():
    report = generate_report()
    return report
```

---

## Logging & Observability

### Basic Logging

```python
from prefect import flow, task, get_run_logger

@task
def logged_task():
    logger = get_run_logger()
    logger.info("Task started")
    logger.warning("This is a warning")
    logger.error("This is an error")
    return "done"

@flow(log_prints=True)
def logging_flow():
    print("This will be logged")  # Captured as log
    logged_task()
```

### Structured Logging

```python
from prefect import flow, task, get_run_logger

@task
def structured_logging():
    logger = get_run_logger()
    logger.info(
        "Processing record",
        extra={
            "record_id": 123,
            "status": "success",
            "duration_ms": 45
        }
    )

@flow
def structured_flow():
    structured_logging()
```

### Tags for Organization

```python
from prefect import flow, tags

@flow
def tagged_flow(env: str):
    with tags("data-pipeline", env, "v2"):
        print(f"Running in {env}")

if __name__ == "__main__":
    tagged_flow("production")
```

### Artifacts

```python
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact, create_table_artifact

@task
def create_report():
    create_markdown_artifact(
        key="report",
        markdown="# Daily Report\n\nProcessed 1000 records"
    )
    
    create_table_artifact(
        key="metrics",
        table=[
            {"metric": "records", "value": 1000},
            {"metric": "errors", "value": 5}
        ]
    )

@flow
def artifact_flow():
    create_report()
```

---

## Blocks & Configuration

### Using Blocks for Configuration

```python
from prefect import flow
from prefect.blocks.system import Secret, JSON

@flow
def config_flow():
    # Access secrets
    api_key = Secret.load("api-key")
    
    # Access JSON config
    config = JSON.load("app-config")
    
    print(f"Using config: {config.value}")
```

### Creating Blocks Programmatically

```python
from prefect.blocks.system import Secret

# Create and save a secret
secret = Secret(value="my-secret-value")
secret.save("my-api-key", overwrite=True)
```

### S3 Block Example

```python
from prefect_aws import S3Bucket
from prefect import flow

@flow
def s3_flow():
    s3_block = S3Bucket.load("my-s3-bucket")
    
    # Upload file
    s3_block.upload_from_path("local.txt", "remote.txt")
    
    # Download file
    s3_block.download_object_to_path("remote.txt", "downloaded.txt")
```

### Database Block Example

```python
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect import flow

@flow
def database_flow():
    db = SqlAlchemyConnector.load("postgres-db")
    
    with db.get_connection() as conn:
        result = conn.execute("SELECT * FROM users LIMIT 10")
        for row in result:
            print(row)
```

---

## Production Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flows/ ./flows/

CMD ["python", "flows/main.py"]
```

**requirements.txt:**
```
prefect>=3.0.0
prefect-aws
prefect-docker
```

**flows/main.py:**
```python
from prefect import flow, task

@task
def process_data():
    return "processed"

@flow
def production_flow():
    result = process_data()
    return result

if __name__ == "__main__":
    production_flow.serve(
        name="docker-deployment",
        cron="0 * * * *"
    )
```

### Kubernetes Deployment

```python
from prefect import flow
from prefect_kubernetes import KubernetesJob

@flow
def k8s_flow():
    print("Running on Kubernetes")

if __name__ == "__main__":
    k8s_flow.deploy(
        name="k8s-deployment",
        work_pool_name="kubernetes-pool",
        image="my-registry/prefect-flow:latest",
        job_variables={
            "namespace": "prefect",
            "image_pull_policy": "Always",
            "resources": {
                "requests": {"memory": "512Mi", "cpu": "500m"},
                "limits": {"memory": "1Gi", "cpu": "1000m"}
            }
        }
    )
```

### AWS ECS Deployment

```python
from prefect import flow
from prefect_aws import ECSTask

@flow
def ecs_flow():
    print("Running on ECS")

if __name__ == "__main__":
    ecs_flow.deploy(
        name="ecs-deployment",
        work_pool_name="ecs-pool",
        image="my-ecr-repo/prefect-flow:latest",
        job_variables={
            "task_definition": {
                "cpu": "512",
                "memory": "1024"
            }
        }
    )
```

### Environment Variables

```python
from prefect import flow
import os

@flow
def env_flow():
    env = os.getenv("ENVIRONMENT", "development")
    api_url = os.getenv("API_URL")
    print(f"Running in {env} with API: {api_url}")

if __name__ == "__main__":
    env_flow.serve(
        name="env-deployment",
        cron="0 0 * * *"
    )
```

### Work Pools & Workers

```bash
# Create work pool
prefect work-pool create --type kubernetes my-k8s-pool

# Start worker
prefect worker start --pool my-k8s-pool
```

---

## Example: Twitter Feed Pipeline

```python
from prefect import flow, task, get_run_logger
from datetime import datetime
import httpx

@task(retries=3, retry_delay_seconds=60)
def fetch_tweets(query: str, max_results: int = 10) -> list[dict]:
    """Fetch tweets from API."""
    logger = get_run_logger()
    logger.info(f"Fetching tweets for query: {query}")
    
    # Simulated API call
    tweets = [
        {"id": i, "text": f"Tweet {i} about {query}", "created_at": datetime.now()}
        for i in range(max_results)
    ]
    
    logger.info(f"Fetched {len(tweets)} tweets")
    return tweets

@task
def filter_tweets(tweets: list[dict], min_length: int = 50) -> list[dict]:
    """Filter tweets by length."""
    logger = get_run_logger()
    filtered = [t for t in tweets if len(t["text"]) >= min_length]
    logger.info(f"Filtered to {len(filtered)} tweets")
    return filtered

@task
def transform_tweets(tweets: list[dict]) -> list[dict]:
    """Transform tweets for publishing."""
    logger = get_run_logger()
    transformed = [
        {
            "id": t["id"],
            "content": t["text"].upper(),
            "timestamp": t["created_at"].isoformat()
        }
        for t in tweets
    ]
    logger.info(f"Transformed {len(transformed)} tweets")
    return transformed

@task(retries=2)
def publish_tweets(tweets: list[dict]) -> dict:
    """Publish tweets to destination."""
    logger = get_run_logger()
    
    for tweet in tweets:
        logger.info(f"Publishing tweet {tweet['id']}")
        # Simulated publish
        
    return {"published": len(tweets), "status": "success"}

@flow(name="Twitter Feed Pipeline", log_prints=True)
def twitter_pipeline(
    query: str = "prefect",
    max_results: int = 100,
    min_length: int = 50
):
    """
    Complete pipeline to fetch, filter, transform, and publish tweets.
    """
    logger = get_run_logger()
    logger.info(f"Starting pipeline for query: {query}")
    
    # Extract
    raw_tweets = fetch_tweets(query, max_results)
    
    # Transform
    filtered = filter_tweets(raw_tweets, min_length)
    transformed = transform_tweets(filtered)
    
    # Load
    result = publish_tweets(transformed)
    
    logger.info(f"Pipeline complete: {result}")
    return result

if __name__ == "__main__":
    # Run once
    twitter_pipeline()
    
    # Or deploy with schedule
    # twitter_pipeline.serve(
    #     name="twitter-feed-prod",
    #     cron="*/15 * * * *",  # Every 15 minutes
    #     parameters={
    #         "query": "prefect OR workflow",
    #         "max_results": 100,
    #         "min_length": 50
    #     },
    #     tags=["twitter", "production"]
    # )
```

---

## Best Practices

### Flow Design
- Keep flows focused on orchestration logic
- Use tasks for discrete units of work
- Leverage subflows for reusable components
- Use meaningful names and descriptions

### Error Handling
- Configure retries at the task level
- Use exponential backoff for API calls
- Implement state handlers for monitoring
- Log errors with context

### Performance
- Use async tasks for I/O-bound operations
- Enable caching for expensive computations
- Parallelize independent tasks
- Persist results for long-running tasks

### Observability
- Use structured logging with context
- Create artifacts for reports and metrics
- Tag flows and tasks for organization
- Monitor flow runs in the UI

### Security
- Store secrets in Prefect Blocks
- Use environment variables for configuration
- Implement least-privilege access
- Rotate credentials regularly

---

## Quick Reference

### Flow Creation
```python
@flow(name="my-flow", log_prints=True)
def my_flow(param: str):
    return process(param)
```

### Task Creation
```python
@task(retries=3, cache_policy=INPUTS)
def my_task(input: str):
    return transform(input)
```

### Deployment
```python
my_flow.serve(
    name="deployment",
    cron="0 0 * * *",
    parameters={"param": "value"}
)
```

### Logging
```python
logger = get_run_logger()
logger.info("Message", extra={"key": "value"})
```

### CLI Commands
```bash
prefect server start              # Start local server
prefect deploy                    # Deploy flow
prefect work-pool create          # Create work pool
prefect worker start --pool name  # Start worker
```
