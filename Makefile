.PHONY: test
test:
	python -m unittest

.PHONY: release-major
release-major:
	./release.sh major

.PHONY: release-minor
release-minor:
	./release.sh minor

.PHONY: release-patch
release-patch:
	./release.sh patch
