from prefect import flow, task, get_run_logger
from src.fetcher import process_articles
from src.twitter import post_tweet
from src.database import get_stats


@task(retries=2, retry_delay_seconds=60)
def fetch_articles_task():
    """Fetch new articles from AWS Builder."""
    logger = get_run_logger()
    
    logger.info("Fetching articles from AWS Builder...")
    result = process_articles()
    
    logger.info(f"Fetched: {result['fetched']}, Added: {result['added']}, Skipped: {result['skipped']}")
    return result


@task(retries=1)
def post_tweet_task():
    """Post one article from queue."""
    logger = get_run_logger()
    
    result = post_tweet()
    
    if result:
        logger.info(f"Posted tweet: {result['title'][:50]}...")
        logger.info(f"Tweet ID: {result['tweet_id']}")
        return result
    else:
        logger.warning("Queue is empty, no tweet posted")
        return None


@flow(name="builderfeed: fetch-articles", log_prints=True)
def fetch_flow():
    """Flow to fetch new articles periodically."""
    logger = get_run_logger()
    
    logger.info("Starting fetch flow...")
    result = fetch_articles_task()
    
    stats = get_stats()
    logger.info(f"Queue stats - Pending: {stats['pending']}, Posted: {stats['posted']}")
    
    return result


@flow(name="builderfeed: post-tweets", log_prints=True)
def tweet_flow():
    """Flow to post one tweet per hour."""
    logger = get_run_logger()
    
    logger.info("Starting tweet flow...")
    
    stats_before = get_stats()
    logger.info(f"Queue before - Pending: {stats_before['pending']}, Posted: {stats_before['posted']}")
    
    result = post_tweet_task()
    
    stats_after = get_stats()
    logger.info(f"Queue after - Pending: {stats_after['pending']}, Posted: {stats_after['posted']}")
    
    return result


if __name__ == "__main__":
    # For testing, run flows once
    print("Testing fetch flow...")
    fetch_flow()
    
    print("\nTesting tweet flow...")
    tweet_flow()
