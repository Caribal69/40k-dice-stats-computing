#!/bin/bash
# Add all, commit and push

# 1/ compile CSV into .py
# --------------------------
# Create `enemy.py` from data/enemy.csv > permits to avoid using pandas (heavy lib) to handle CSV
cd src/common
python build_enemy.py
cd ../..

# 2/ Commit message
# --------------------------
# Last commit containing char "fix buildozer spec"
LAST_AUTO_COMMIT=$(git log -10 --pretty=format:"%s" | grep "fix buildozer spec" | tail -n 1)
# ex: "fix buildozer spec 9"

# Get the last commit message and increment last digit by 1 (awk ... +1)
NEW_COMMIT_MESSAGE=$(echo $LAST_AUTO_COMMIT | awk '/fix buildozer spec/ {print "fix buildozer spec", $NF+1}')
# ex: "fix buildozer spec 10"

# 3/ Commit and push
# --------------------------
git add .
git commit -m "$NEW_COMMIT_MESSAGE"
git push