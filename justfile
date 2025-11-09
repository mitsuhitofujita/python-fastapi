# Default task: show available tasks
default:
    @just --list

# Run Ruff auto-format and fix linting issues
lint:
    cd app/api && uv run ruff format .
    cd app/api && uv run ruff check --fix .

# Run type checking and linting without auto-fix (for CI/CD)
check:
    cd app/api && uv run ruff check .
    cd app/api && uv run mypy .

# Run tests with coverage (as configured in pyproject.toml)
test:
    cd app/api && uv run pytest tests/

# Run tests without coverage (fast mode for development)
test-fast:
    cd app/api && uv run pytest tests/ --no-cov

# Show coverage report in terminal
cov:
    cd app/api && uv run pytest tests/ --cov-report=term-missing

# Generate HTML coverage report
cov-html:
    cd app/api && uv run pytest tests/ --cov-report=html

# Start development server with hot reload
serve:
    cd app/api && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start development server (alias for serve)
dev:
    just serve

# Run Alembic migrations to latest version
migrate:
    cd app/api && uv run alembic upgrade head

# Rollback all migrations to base (empty database)
migrate-reset:
    cd app/api && uv run alembic downgrade base

# Downgrade migration by one step
migrate-down:
    cd app/api && uv run alembic downgrade -1

# Create new Alembic migration with auto-detection
migration-create MESSAGE:
    cd app/api && uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# Reset test database (drop all tables and re-run migrations)
db-reset-test:
    cd app/api && uv run python scripts/reset_test_db.py

# Run a script from the scripts directory
script SCRIPT_NAME:
    cd app/api && uv run python scripts/{{SCRIPT_NAME}}.py

# Run all CI/CD checks (type check, lint check, tests)
ci:
    just check
    just test

# Run all pre-commit checks (lint, type check, tests)
ready:
    just lint
    just test
