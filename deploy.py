#!/usr/bin/env python3
"""Deploy BuilderFeed flows with scheduling."""

from prefect import serve
from src.flows import fetch_flow, tweet_flow

if __name__ == "__main__":
    # Deploy both flows with schedules
    fetch_deployment = fetch_flow.to_deployment(
        name="fetch-articles-deployment",
        cron="0 * * * *",  # Every hour
        tags=["builderfeed", "fetch"]
    )
    
    tweet_deployment = tweet_flow.to_deployment(
        name="post-tweets-deployment",
        cron="0 * * * *",  # Every hour
        tags=["builderfeed", "tweet"]
    )
    
    # Serve both deployments
    serve(fetch_deployment, tweet_deployment)
