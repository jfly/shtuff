.PHONY: test
test: .shtuff-installed
	python -m unittest

.PHONY: clean
clean:
	find . -name __pycache__ | xargs rm -rf
	rm .shtuff-installed

.shtuff-installed: setup.py shtuff.py
	rm -rf tests/build
	pip install -e .
	touch .shtuff-installed
