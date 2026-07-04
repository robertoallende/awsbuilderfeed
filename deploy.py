#!/usr/bin/env python3
"""Deploy BuilderFeed flows with scheduling."""

from prefect import serve
from src.flows import fetch_flow, tweet_flow

if __name__ == "__main__":
    # Deploy both flows with schedules
    fetch_deployment = fetch_flow.to_deployment(
        name="fetch-articles-deployment",
        cron="30 * * * *",  # Every hour at minute 30
        tags=["builderfeed"]
    )

    tweet_deployment = tweet_flow.to_deployment(
        name="post-tweets-deployment",
        cron="0 */2 * * *",  # Every 2 hours (Make.com credit budget: 1000/mo at 2 credits/call)
        tags=["builderfeed"]
    )
    
    # Serve both deployments
    serve(fetch_deployment, tweet_deployment)
