#!/usr/bin/env python3
"""Script to retroactively mark spam in existing database articles."""

import sqlite3
from pathlib import Path
from src.spam_filter import check_spam

DB_PATH = Path(__file__).parent.parent / "data" / "builderfeed.db"

def mark_existing_spam():
    """Check all existing articles and mark spam."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all articles
    cursor.execute("SELECT * FROM articles WHERE is_spam = 0")
    articles = cursor.fetchall()
    
    spam_count = 0
    for row in articles:
        article = dict(row)
        is_spam, matched_rules = check_spam(article)
        
        if is_spam:
            cursor.execute("UPDATE articles SET is_spam = 1 WHERE id = ?", (article['id'],))
            spam_count += 1
            print(f"🚫 Marked as spam: {article['title'][:60]}... (rules: {', '.join(matched_rules)})")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Marked {spam_count} articles as spam")
    
    # Show updated stats
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles WHERE is_spam = 1")
    total_spam = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM articles WHERE posted = 0 AND is_spam = 0")
    pending = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Stats: {total_spam} spam articles, {pending} pending clean articles")

if __name__ == "__main__":
    mark_existing_spam()
