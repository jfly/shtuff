.PHONY: test
test: .shtuff-installed
	python -m unittest

.PHONY: clean
clean:
	find . -name __pycache__ | xargs rm -rf
	rm .shtuff-installed

.PHONY: release-major
release-major:
	./release.sh major

.PHONY: release-minor
release-minor:
	./release.sh minor

.PHONY: release-patch
release-patch:
	./release.sh patch

.shtuff-installed: setup.py shtuff.py
	rm -rf tests/build
	pip install -e .
	touch .shtuff-installed
