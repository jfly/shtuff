# shtuff  [![Deploy to PyPI](https://github.com/jfly/shtuff/actions/workflows/ci.yml/badge.svg)](https://github.com/jfly/shtuff/actions/workflows/ci.yml)

Shell stuff will stuff commands into a shell à la `tmux send-keys` or `screen
stuff`.

## Installation

If your environment is configured to use Python 3 by default:
```
$ pip install shtuff
```

Otherwise:
```
$ pip3 install shtuff
```

Please note: `shtuff` only works on Python 3.7+!

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
$ pip3 install -e .
```

Unless you know what you are doing, we highly recommend running tests inside a virtual environment.
Here is how you can create and activate a virtual environment:

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

You can leave the virtual environment via `deactivate`:

```bash
$ deactivate
```

Run tests:

```bash
$ make test
```

## Releasing

We release using Makefile, choose the relevant target:

```bash
$ make release-major
$ make release-minor
$ make release-patch
```

and wait for the automated deploy to [PyPi](https://pypi.org/project/shtuff/)!
