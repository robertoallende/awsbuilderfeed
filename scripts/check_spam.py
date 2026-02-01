#!/usr/bin/env python3
"""Check spam articles detected in the last N days."""

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / "data" / "builderfeed.db"


def check_spam(days=7):
    """Show spam articles from last N days."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Calculate timestamp for N days ago
    cutoff = datetime.now() - timedelta(days=days)
    cutoff_ts = int(cutoff.timestamp())
    
    # Get spam articles from last N days
    cursor.execute("""
        SELECT id, title, author_name, author_alias, fetched_at
        FROM articles
        WHERE is_spam = 1 AND fetched_at >= ?
        ORDER BY fetched_at DESC
    """, (cutoff_ts,))
    
    spam_articles = cursor.fetchall()
    
    print(f"\n=== SPAM DETECTED (Last {days} Day{'s' if days != 1 else ''}) ===\n")
    
    if not spam_articles:
        print(f"✅ No spam detected in the last {days} day{'s' if days != 1 else ''}")
        conn.close()
        return
    
    for article in spam_articles:
        fetched_dt = datetime.fromtimestamp(article['fetched_at'])
        print(f"{fetched_dt.strftime('%Y-%m-%d %H:%M')} - {article['title'][:70]}")
        print(f"  Author: {article['author_alias'] or article['author_name'] or 'Unknown'}")
        print()
    
    print("---")
    print(f"Total: {len(spam_articles)} spam article{'s' if len(spam_articles) != 1 else ''} in last {days} day{'s' if days != 1 else ''}")
    
    # Overall stats
    cursor.execute("SELECT COUNT(*) FROM articles WHERE is_spam = 1")
    total_spam = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM articles WHERE is_spam = 0 AND posted = 0")
    pending = cursor.fetchone()[0]
    
    print(f"\n📊 Overall Stats:")
    print(f"  Total spam blocked: {total_spam}")
    print(f"  Clean articles pending: {pending}")
    
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check spam articles detected in the last N days")
    parser.add_argument("--days", type=int, default=7, help="Number of days to check (default: 7)")
    
    args = parser.parse_args()
    
    if args.days < 1:
        print("Error: --days must be at least 1")
        exit(1)
    
    check_spam(args.days)
