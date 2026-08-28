.PHONY: help install test lint check run clean

help:
	@echo "Targets:"
	@echo "  install  Install pinned, hash-verified dependencies from requirements.lock.txt"
	@echo "  test     Run the pytest suite"
	@echo "  lint     Run ruff (dead-code checks only, see ruff.toml)"
	@echo "  check    lint + test — what CI runs"
	@echo "  run      Run github_search.py with the default fallback query"
	@echo "  clean    Remove local test/lint caches"
	@echo ""
	@echo "No 'make' available (e.g. plain Windows PowerShell)? Run the commands"
	@echo "inside each target directly — none of them depend on this Makefile."

install:
	pip install --require-hashes -r requirements.lock.txt

test:
	pytest

lint:
	ruff check .

check: lint test

run:
	python github_search.py

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ tests/__pycache__
