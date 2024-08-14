#!/bin/bash
# Add all, commit and push

# 1/ Get the last commit message (git log -1...) and increment last digit by 1 (awk ... +1)
NEW_COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s" | awk '/fix buildozer spec/ {print "fix buildozer spec", $NF+1}')
# ex: "fix buildozer spec 9"

git add .

git commit -m "$NEW_COMMIT_MESSAGE"

git push