.PHONY: install lint type-check test all-checks clean clean-tool update

install:
	uv sync

lint:
	uv run ruff check .

type-check:
	uv run mypy .

test:
	uv run pytest

all-checks: lint type-check test

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name __pycache__ -delete

clean-tool:
	@if [ -d ".mypy_cache" ]; then rm -rf .mypy_cache; fi
	@if [ -d ".ruff_cache" ]; then rm -rf .ruff_cache; fi

update:
	uv lock --upgrade
	uv sync
