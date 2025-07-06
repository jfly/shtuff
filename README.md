# shtuff  [![Deploy to PyPI](https://github.com/jfly/shtuff/actions/workflows/ci.yaml/badge.svg)](https://github.com/jfly/shtuff/actions/workflows/ci.yaml)

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

This repo defines a nix devShell. If you use direnv, it will automatically get
loaded for you and you can skip to `Run Tests:`. If you do not use direnv, you
will need to enter the shell with:

```bash
$ nix develop
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
