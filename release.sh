#!/usr/bin/env bash

RELEASE_LEVEL=$1

if ! git remote -v | grep "^upstream.*github\.com.jfly\/shtuff\.git" &> /dev/null; then
    echo "A remote named upstream must be configured to point to https://github.com/jfly/shtuff.git to be able to make a release"
    exit 1
fi

if ! git fetch upstream &> /dev/null; then
    echo "Fetch did not perform successfully, make sure you have permission to pull from this repository."
    exit 2
fi

CURRENT_VERSION=$(git tag | sort -V | tail -n 1)
NEW_VERSION=$(./bump_version.py "$CURRENT_VERSION" "$RELEASE_LEVEL")

git tag $NEW_VERSION
git push --tags upstream

if [[ $? -gt 0 ]]; then
    echo "Push did not perform successfully, make sure you have permission to push to this repository."
    exit 2
fi

echo "New version released: $NEW_VERSION"
