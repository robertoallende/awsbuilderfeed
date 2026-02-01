# Unit 07: Spam Detection

## Objective

Add spam filtering to prevent posting spam articles from AWS Builder feed:
- Analyze production database to identify spam patterns
- Implement rule-based spam detection
- Add `is_spam` column to articles table
- Config-based rules (generic + local overrides)
- Integrate into fetch pipeline

## Problem

AWS Builder feed is being hit with spam articles. Currently manually deleting spam posts on social media. Need automated filtering before articles reach the queue.

## Solution Architecture

```
Fetch Articles → Parse → Spam Detection → Add to Queue
                            ↓
                    Flag as spam in DB
                    (never posted)
```

## Implementation Plan

### Subunit 7.1: Database Analysis & Rule Extraction
- Copy production database
- Analyze articles to identify spam patterns
- Document spam characteristics
- Create initial rule set

### Subunit 7.2: Spam Filter Implementation
- Add `is_spam` column to articles table
- Create `src/spam_filter.py` with rule engine
- Create config files (generic + local)
- Integrate into `fetcher.py`
- Add spam stats tracking

### Subunit 7.3: Testing & Validation
- Test against historical data
- Verify accuracy
- Adjust rules
- Document results

## Database Changes

**ALTER TABLE articles:**
```sql
ALTER TABLE articles ADD COLUMN is_spam BOOLEAN DEFAULT 0;
```

No migration script needed - manual update on production.

## Config Files

- `config/spam_rules.json` - Main spam rules (gitignored, not committed)
- `config/spam_rules.local.json` - Optional local overrides (gitignored)
- `config/spam_rules.json.example` - Template (committed to repo)

**Security:** Spam rules are not committed to prevent spammers from adapting.

## Files Modified

- `dev_log/07_spam.md` (this file)
- `dev_log/07_spam_001.md` (analysis)
- `dev_log/07_spam_002.md` (implementation)
- `dev_log/07_spam_003.md` (testing)
- `src/spam_filter.py` (new)
- `src/fetcher.py` (modify)
- `src/database.py` (modify)
- `config/spam_rules.json` (new)
- `config/spam_rules.local.json` (new, gitignored)
- `.gitignore` (update)

## Status: Complete ✅

**All subunits complete!**

- ✅ Subunit 7.1: Database Analysis & Rule Extraction
- ✅ Subunit 7.2: Spam Filter Implementation
- ✅ Subunit 7.3: Testing & Validation
- ✅ Subunit 7.4: Spam Monitoring Tools

**Final Results:**
- 95.3% spam detection rate
- 163 spam articles blocked
- 8 clean articles ready to post
- 0% false positive rate
- Monitoring tool for production

**Production Tools:**
- `scripts/check_spam.py` - View spam from last N days
- `scripts/mark_spam.py` - Retroactively mark spam
- Config-based rules (easy to update)

**Next Steps:**
1. Copy updated database to production
2. Deploy spam filter code to production
3. Copy spam rules config files to production
4. Monitor spam detection in production
