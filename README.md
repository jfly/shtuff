# shtuff  [![Build Status](https://travis-ci.org/jfly/shtuff.svg?branch=master)](https://travis-ci.org/jfly/shtuff)

Shell stuff will stuff commands into a shell à la `tmux send-keys` or `screen
stuff`.

## Examples
In shell A, run:
```
$ shtuff as shell-a
```

In shell B, run:
```
$ shtuff into shell-a "git status"
```

Observe how shell A ran `git status`.

An example use case for `shtuff new` might be a setup script to open a couple
shells automatically. Consider this script:

```sh
#!/usr/bin/env bash
termite -e "shtuff new vim" &
termite -e "shtuff new 'tail -f /var/log/somelog.log'" &
```

This script will open two terminals, one running vim, and one
running tail.

## Development

Install your local copy:

```bash
$ pip install -e .
```

Run tests:

```bash
$ rm -rf tests/build && pip install -t tests/build .
$ python -m unittest
```

## Releasing

Simply:

```bash
$ git tag vX.Y.Z && git push --tags
```

and wait for Travis to deploy to PyPi!
