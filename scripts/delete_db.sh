#!/bin/bash
# Delete database and start fresh

cd "$(dirname "$0")/.."

echo "🗑️  Deleting database..."
rm -f data/builderfeed.db

echo "✅ Database deleted!"
echo ""
echo "To recreate and fetch articles, run:"
echo "  ./scripts/reset_db.sh"
