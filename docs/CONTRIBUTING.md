# Contributing Guide

Thank you for helping improve this beginner-friendly Netflix Data Analysis project!

---

## How to Contribute

1. **Fork & Clone** the repository.
2. **Create a virtual environment** and install dependencies (see [`04_installation_and_setup.md`](04_installation_and_setup.md)).
3. **Create a branch** for your change:
   ```bash
   git checkout -b feat/my-improvement
   ```
4. **Make your changes** following our code quality standards:
   - Add type hints and concise docstrings to new functions.
   - Use `logging` instead of `print()` in `src/`.
   - Never commit `data/raw/netflix_titles.csv`, `.env`, or API keys.
5. **Run tests and linting** before committing:
   ```bash
   pytest --cov=netflix_analysis --cov-report=term-missing
   ruff check src tests app
   ```
6. **Use Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `test:`, `chore:`) and open a Pull Request.
