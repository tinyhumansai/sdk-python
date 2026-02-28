.PHONY: install test build publish

install:
	uv sync

test:
	uv run pytest

build:
	uv build

publish: build
	uv publish
