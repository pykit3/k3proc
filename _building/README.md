# _building

Shared build configuration for pykit3 packages.

## Commands

All commands use the `pk3` package:

```bash
make test      # Run tests with pytest
make lint      # Format and lint with ruff
make cov       # Generate coverage report
make doc       # Build documentation with mkdocs
make readme    # Generate README.md from docstrings
make release   # Create git tag from version in pyproject.toml
make publish   # Build and upload to PyPI
```

## Release Process

1. Update version in `pyproject.toml`
2. Run `make release` to create git tag
3. Run `git push --tags` to trigger GitHub Actions
4. GitHub Actions automatically publishes to PyPI
