.PHONY: test
test: tests/build
	python -m unittest

tests/build: setup.py shtuff.py
	rm -rf tests/build
	pip install -t tests/build .
