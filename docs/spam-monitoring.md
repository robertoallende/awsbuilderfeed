# Spam Monitoring Guide

## Overview

The BuilderFeed bot includes spam detection to prevent posting airline/travel customer service spam. This guide covers how to monitor spam detection in production.

## Monitoring Tools

### check_spam.py - View Recent Spam

Shows spam articles detected in the last N days.

**Location:** `scripts/check_spam.py`

**Usage:**

```bash
# View spam from last 7 days (default)
cd /path/to/builderfeed
PYTHONPATH=. python3 scripts/check_spam.py

# View spam from last 24 hours
PYTHONPATH=. python3 scripts/check_spam.py --days 1

# View spam from last 30 days
PYTHONPATH=. python3 scripts/check_spam.py --days 30
```

**Output:**

```
=== SPAM DETECTED (Last 7 Days) ===

2026-02-01 11:30 - ¿Cómo puedo cambiar mi vuelo de Wingo?
  Author: dddds

2026-02-01 10:30 - ✈️ Comment joindre KLM par téléphone ?
  Author: jhasas

2026-02-01 09:30 - How do I contact Netflix customer care
  Author: jamessmithstr

---
Total: 163 spam articles in last 7 days

📊 Overall Stats:
  Total spam blocked: 163
  Clean articles pending: 8
```

### mark_spam.py - Retroactive Spam Marking

Scans existing articles and marks spam based on current rules.

**Location:** `scripts/mark_spam.py`

**Usage:**

```bash
cd /path/to/builderfeed
PYTHONPATH=. python3 scripts/mark_spam.py
```

**When to use:**
- After updating spam rules
- After copying production database locally
- To clean up historical data

## Database Stats

Check overall spam statistics:

```bash
cd /path/to/builderfeed
PYTHONPATH=. python3 -c "from src.database import get_stats; print(get_stats())"
```

**Output:**
```python
{'pending': 8, 'posted': 284, 'spam': 163}
```

- `pending`: Clean articles ready to post
- `posted`: Articles already posted to Twitter
- `spam`: Articles blocked by spam detection

## Spam Detection Logs

View spam detection in real-time from Prefect flows:

```bash
# View builderfeed service logs
journalctl -u builderfeed -f

# Filter for spam detection
journalctl -u builderfeed -f | grep "SPAM detected"
```

**Example log:**
```
🚫 SPAM detected: ¿Cómo llamar a Lufthansa desde México?... (rules: airline_keywords, contact_phrases_spanish)
```

## Common Monitoring Tasks

### Daily Check (Recommended)

Check spam from last 24 hours:

```bash
PYTHONPATH=. python3 scripts/check_spam.py --days 1
```

### Weekly Review

Review spam from last 7 days:

```bash
PYTHONPATH=. python3 scripts/check_spam.py --days 7
```

### After Rule Updates

After updating `config/spam_rules.json` or `config/spam_rules.local.json`:

```bash
# Re-scan existing articles
PYTHONPATH=. python3 scripts/mark_spam.py

# Check stats
PYTHONPATH=. python3 -c "from src.database import get_stats; print(get_stats())"
```

## Updating Spam Rules

### Add New Spam Author

Edit `config/spam_rules.local.json`:

```json
{
  "rules": [
    {
      "id": "spam_authors",
      "type": "author",
      "field": "author_alias",
      "patterns": [
        "existing_spammer",
        "new_spammer_alias"
      ],
      "enabled": true
    }
  ]
}
```

No restart needed - rules are loaded on each fetch.

### Add New Keyword Pattern

Edit `config/spam_rules.json`:

```json
{
  "rules": [
    {
      "id": "new_spam_pattern",
      "type": "keyword",
      "field": "title",
      "patterns": ["spam_keyword"],
      "case_sensitive": false,
      "enabled": true
    }
  ]
}
```

## Troubleshooting

### False Positives (Legitimate Content Blocked)

If legitimate AWS content is marked as spam:

1. Check which rule matched:
   ```bash
   PYTHONPATH=. python3 scripts/check_spam.py --days 1
   ```

2. Review the article in database:
   ```bash
   sqlite3 data/builderfeed.db "SELECT * FROM articles WHERE title LIKE '%article_title%';"
   ```

3. Disable or refine the rule in config files

4. Unmark the article:
   ```bash
   sqlite3 data/builderfeed.db "UPDATE articles SET is_spam = 0 WHERE id = <article_id>;"
   ```

### False Negatives (Spam Not Detected)

If spam articles are getting through:

1. Identify the spam pattern (title, author, keywords)

2. Add rule to `config/spam_rules.local.json`

3. Re-scan existing articles:
   ```bash
   PYTHONPATH=. python3 scripts/mark_spam.py
   ```

### No Spam Detected

If spam detection seems inactive:

1. Check rules are loaded:
   ```bash
   ls -la config/spam_rules*.json
   ```

2. Test spam detection:
   ```bash
   PYTHONPATH=. python3 -c "
   from src.spam_filter import check_spam
   test = {'title': '¿Cómo llamar a Lufthansa?', 'author_alias': 'test', 'tags': ''}
   print(check_spam(test))
   "
   ```

3. Check database has is_spam column:
   ```bash
   sqlite3 data/builderfeed.db "PRAGMA table_info(articles);" | grep is_spam
   ```

## Files Reference

- `scripts/check_spam.py` - View recent spam
- `scripts/mark_spam.py` - Retroactive spam marking
- `config/spam_rules.json` - Main spam rules (gitignored)
- `config/spam_rules.local.json` - Production-specific rules (gitignored)
- `config/spam_rules.json.example` - Template for rules
- `docs/spam-detection-deployment.md` - Deployment guide

## Support

For issues or questions about spam detection, check:
- `dev_log/07_spam.md` - Unit overview
- `dev_log/07_spam_001.md` - Analysis and patterns
- `dev_log/07_spam_002.md` - Implementation details
