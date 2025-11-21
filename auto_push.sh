#!/bin/bash
# Add all, commit and push
# usage: `source auto_push.sh` > no argument --> commit message will be automatically generated
# usage 2: `source auto_push.sh <commit message> --> will commit and push <commit message>

# 1/ compile CSV into .py
# --------------------------
# Activate python
source .tox/dice_manager/Scripts/activate

# Create `enemy.py` from data/enemy.csv > permits to avoid using pandas (heavy lib) to handle CSV
cd src/common
python build_enemy.py

cd ../..

# 2/ Commit message
# --------------------------
if [ "$#" -eq 0 ]; then
  # No argument provided: build commit message

  # Last commit containing char "fix buildozer spec"
  LAST_AUTO_COMMIT=$(git log -10 --pretty=format:"%s" | grep "fix buildozer spec" | tail -n 1)
  # ex: "fix buildozer spec 9"

  # Get the last commit message and increment last digit by 1 (awk ... +1)
  NEW_COMMIT_MESSAGE=$(echo $LAST_AUTO_COMMIT | awk '/fix buildozer spec/ {print "fix buildozer spec", $NF+1}')
  # ex: "fix buildozer spec 10"

else
  # Commit is provided by user
  NEW_COMMIT_MESSAGE="$1"
fi

# 3/ Update version
# --------------------------
# Path to your version file
VERSION_FILE="src/__version__.py"
SPEC_FILE="buildozer.spec"

# Read the current version from the file
current_version=$(grep "VERSION = " "$VERSION_FILE" | cut -d= -f2 | tr -d ' ')


# Extract the major and minor version numbers
major=$(echo $current_version | cut -d. -f1)
minor=$(echo $current_version | cut -d. -f2)

# Increment the minor version
new_minor=$((minor + 1))

# Construct the new version string
new_version="$major.$new_minor"

echo "Version updated from $current_version to $new_version"

echo "Update the version file"
sed -i "s/VERSION = .*/VERSION = $new_version/" "$VERSION_FILE"


# Update the version in the buildozer.spec file and convert "version = " to lowercase
sed -i "s/^version = .*/version = $new_version/" "$SPEC_FILE"
sed -i 's/^VERSION = /version = /' "$SPEC_FILE"
# Same in README.md (badge)
sed -i "s|version-[0-9.]*-blue.svg|version-${new_version}-blue.svg|" README.md

# 4/ Commit and push
# --------------------------
git add .
git commit -m "$NEW_COMMIT_MESSAGE"

# Ask user if they want to deploy (create and push a tag)
read -p "Deploy new release (${new_version})? (yes/no) " DEPLOY_ANSWER

if [ "$DEPLOY_ANSWER" = "yes" ]; then
  git tag "$new_version"
  git push origin "$new_version"
fi


git push

deactivate