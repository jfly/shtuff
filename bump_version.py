#!/usr/bin/env python3

import sys

def bump_version(version, level):
    major, minor, patch = map(int, version.lstrip('v').split('.'))

    semver = {
        'major': (major + 1, 0, 0),
        'minor': (major, minor + 1, 0),
        'patch': (major, minor, patch + 1),
    }

    return "v%d.%d.%d" % semver[level]

def main():
    print(bump_version(sys.argv[1], sys.argv[2]))

if __name__ == "__main__":
    main()
