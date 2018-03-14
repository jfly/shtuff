# shtuff  [![Build Status](https://travis-ci.org/jfly/shtuff.svg?branch=master)](https://travis-ci.org/jfly/shtuff)

Shell stuffer

## Development

```bash
$ pip install -e .
```

## Releasing

First, bump version number in `VERSION` file and commit. Then:

```bash
$ git tag v$(cat VERSION)
$ git push --tags
```

and wait for Travis to deploy to PyPi!
