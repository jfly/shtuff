#!/usr/bin/env bash

set -euo pipefail

RELEASE_LEVEL=$1

if ! git remote -v | grep "^upstream.*github\.com.jfly\/shtuff\.git" &>/dev/null; then
  echo "A remote named upstream must be configured to point to https://github.com/jfly/shtuff.git to be able to make a release"
  exit 1
fi

if ! git fetch upstream &>/dev/null; then
  echo "Fetch did not perform successfully, make sure you have permission to pull from this repository."
  exit 2
fi

CURRENT_VERSION=$(tr -d '\n' <VERSION)
NEW_VERSION=$(./bump_version.py "$CURRENT_VERSION" "$RELEASE_LEVEL")

echo "$NEW_VERSION" >VERSION
git add VERSION
git commit -m "Bumping version to $NEW_VERSION"

git tag "$NEW_VERSION"
git push upstream HEAD:main
git push upstream "$NEW_VERSION"

echo "New version released in GitHub: $NEW_VERSION"
echo "Check the $NEW_VERSION build: https://github.com/jfly/shtuff/actions/workflows/ci.yaml"
echo "If the build is successful, the workflow will push the release to PyPI"
