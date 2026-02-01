# Spam Detection - Production Deployment Guide

## Files to Deploy

### 1. Update Code (via Git)
```bash
# On production server
cd /path/to/builderfeed
git pull origin main
```

**New files in this update:**
- `src/spam_filter.py`
- `scripts/check_spam.py`
- `scripts/mark_spam.py`
- Updated: `src/database.py`, `src/fetcher.py`

### 2. Config Files (IMPORTANT - Not in Git)
```bash
# Copy spam rules to production
scp config/spam_rules.json production:/path/to/builderfeed/config/
scp config/spam_rules.local.json production:/path/to/builderfeed/config/
```

### 3. Database
```bash
# Option A: Copy updated database with is_spam column and flagged spam
scp data/builderfeed.db production:/path/to/builderfeed/data/

# Option B: Manually add column on production (if you want to keep production data)
ssh production
cd /path/to/builderfeed
sqlite3 data/builderfeed.db "ALTER TABLE articles ADD COLUMN is_spam BOOLEAN DEFAULT 0;"
# Then run mark_spam.py to flag existing spam
PYTHONPATH=. python3 scripts/mark_spam.py
```

## Verification Steps

### 1. Test Spam Detection
```bash
cd /path/to/builderfeed
PYTHONPATH=. python3 -c "
from src.spam_filter import check_spam

# Test with spam article
spam = {'title': '¿Cómo llamar a Lufthansa?', 'author_alias': 'test', 'tags': ''}
is_spam, rules = check_spam(spam)
print(f'Spam test: {is_spam} (rules: {rules})')

# Test with clean article
clean = {'title': 'Building with AWS Lambda', 'author_alias': 'builder', 'tags': 'aws-lambda'}
is_spam, rules = check_spam(clean)
print(f'Clean test: {is_spam} (rules: {rules})')
"
```

### 2. Check Database Stats
```bash
PYTHONPATH=. python3 -c "from src.database import get_stats; print(get_stats())"
```

Expected output:
```
{'pending': X, 'posted': Y, 'spam': Z}
```

### 3. Test Fetch Flow
```bash
# Fetch new articles (will auto-detect spam)
PYTHONPATH=. python3 -c "from src.fetcher import process_articles; print(process_articles())"
```

Should show:
```
fetched: X, added: Y, skipped: Z, spam_detected: N
```

### 4. Restart Services
```bash
sudo systemctl restart builderfeed
sudo systemctl status builderfeed
```

## Monitoring

### Check Recent Spam
```bash
# Last 7 days
PYTHONPATH=. python3 scripts/check_spam.py

# Last 24 hours
PYTHONPATH=. python3 scripts/check_spam.py --days 1
```

### Check Spam Detection Logs
```bash
journalctl -u builderfeed -f | grep "SPAM detected"
```

### View Stats
```bash
PYTHONPATH=. python3 -c "from src.database import get_stats; s = get_stats(); print(f'Pending: {s[\"pending\"]}, Posted: {s[\"posted\"]}, Spam: {s[\"spam\"]}')"
```

**See [docs/spam-monitoring.md](spam-monitoring.md) for complete monitoring guide.**

## Updating Spam Rules

### Add New Spam Pattern
Edit `config/spam_rules.local.json`:
```json
{
  "rules": [
    {
      "id": "new_spam_author",
      "type": "author",
      "field": "author_alias",
      "patterns": ["spammer123"],
      "enabled": true
    }
  ]
}
```

No restart needed - rules are loaded on each fetch.

### Mark Existing Articles as Spam
```bash
# Run mark_spam.py script
PYTHONPATH=. python3 scripts/mark_spam.py
```

## Rollback (If Needed)

### Remove Spam Detection
```bash
# Revert database changes
sqlite3 data/builderfeed.db "UPDATE articles SET is_spam = 0;"

# Remove spam filter import from fetcher.py
# Comment out spam detection in src/fetcher.py
```

## Success Indicators

✅ Spam articles flagged with `is_spam = 1`
✅ Only clean articles in tweet queue
✅ No airline/travel spam posted to Twitter
✅ Logs show "🚫 SPAM detected" messages
✅ Stats show spam count increasing
