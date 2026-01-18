#!/bin/bash
# Reset database and fetch fresh articles

cd "$(dirname "$0")/.."

echo "🗑️  Deleting old database..."
rm -f data/builderfeed.db

echo "🔧 Creating fresh database..."
source .venv/bin/activate
PYTHONPATH=. python -c "from src.database import init_db; init_db()"

#echo "📥 Fetching articles..."
#PYTHONPATH=. python -c "from src.fetcher import process_articles; result = process_articles(); print(f'✅ Fetched: {result[\"fetched\"]}, Added: {result[\"added\"]}, Skipped: {result[\"skipped\"]}')"

echo "📊 Queue stats:"
PYTHONPATH=. python -c "from src.database import get_stats; stats = get_stats(); print(f'   Pending: {stats[\"pending\"]}, Posted: {stats[\"posted\"]}')"

echo ""
echo "✅ Database reset complete!"
