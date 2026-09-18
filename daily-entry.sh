#!/bin/bash
# Daily Human Nature Entry Validator & Committer
# Called by OpenClaw automation or agent

set -e
REPO_DIR="/home/itsaddyon/.openclaw/workspace/main/human-nature"
cd "$REPO_DIR"

DATE=$(date +%Y-%m-%d)

# 1. Run syntax & health verification first
echo "🔍 Verifying journal syntax..."
if ! python3 daily-append.py --check; then
  echo "❌ Verification failed! Aborting commit to prevent pushing broken site."
  exit 1
fi

# 2. Stage index.html
git add index.html

# 3. Check if there are staged changes
if git diff --staged --quiet; then
  echo "ℹ️ No changes staged to commit."
  exit 0
fi

# 4. Calculate true day count from unique dates in index.html
DAY_COUNT=$(python3 -c "
import re
from pathlib import Path
html = Path('index.html').read_text(encoding='utf-8')
dates = set(re.findall(r'[\'\"]date[\'\"]\s*:\s*[\'\"](\d{4}-\d{2}-\d{2})[\'\"]', html))
print(len(dates))
")

COMMIT_MSG="Day ${DAY_COUNT}: Daily entry — ${DATE}"

git commit -m "$COMMIT_MSG"
git push origin master

echo "✅ Successfully committed and pushed: $COMMIT_MSG"
