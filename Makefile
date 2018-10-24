.PHONY: test
test: .shtuff-installed
	python -m unittest

.PHONY: clean
clean:
	find . -name __pycache__ | xargs rm -rf
	rm .shtuff-installed

.PHONY: release-major
release-major:
	make release version=$$(./bump-version.py major)

.PHONY: release-minor
release-minor:
	make release version=$$(./bump-version.py minor)

.PHONY: release-patch
release-patch:
	make release version=$$(./bump-version.py patch)

.PHONY: release
release:
	git tag $(version)
	git push --tags

.shtuff-installed: setup.py shtuff.py
	rm -rf tests/build
	pip install -e .
	touch .shtuff-installed
