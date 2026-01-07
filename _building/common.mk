all: test lint readme doc

.PHONY: test lint cov
sudo_test:
	sudo env "PATH=$$PATH" UT_DEBUG=0 pytest -v

test:
	env UT_DEBUG=0 pytest -v

cov:
	coverage run --source=. -m pytest
	coverage html
	open htmlcov/index.html

doc:
	mkdocs build

lint:
	# ruff format: fast Python code formatter (Black-compatible)
	uvx ruff format .
	# ruff check: fast Python linter with auto-fixes
	uvx ruff check --fix .

static_check:
	# mypy: static type checker for Python
	uvx mypy . --ignore-missing-imports

readme:
	pk3 readme

release:
	pk3 tag

publish:
	pk3 publish

install:
	pip install -e .
