all: test lint readme doc

.PHONY: test lint
sudo_test:
	sudo env "PATH=$$PATH" UT_DEBUG=0 PYTHONPATH="$$(cd ..; pwd)" python -m unittest discover -c --failfast -s .

test:
	env "PATH=$$PATH" UT_DEBUG=0 PYTHONPATH="$$(cd ..; pwd)" python -m unittest discover -c --failfast -s .

doc:
	make -C docs html

lint:
	# ruff format: fast Python code formatter (Black-compatible)
	uvx ruff format .
	# ruff check: fast Python linter with auto-fixes
	uvx ruff check --fix .

static_check:
	# mypy: static type checker for Python
	uvx mypy . --ignore-missing-imports

readme:
	python _building/build_readme.py

build_setup_py:
	PYTHONPATH="$$(cd ..; pwd)" python _building/build_setup.py

publish:
	./_building/publish.sh

install:
	./_building/install.sh
