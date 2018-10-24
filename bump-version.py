#!/usr/bin/env python3

import sys
import subprocess

def bump_version(version, level):
    semver = {'major': 0, 'minor': 1, 'patch': 2}
    version_pieces = version.lstrip('v').split('.')
    version_pieces[semver[level]] = str(int(version_pieces[semver[level]]) + 1)

    return "v" + ".".join(version_pieces)

version = subprocess.run("git tag | sort -V | tail -n 1", shell=True, capture_output=True) \
    .stdout.decode().strip()

print(bump_version(version, sys.argv[1]))
