.DEFAULT_GOAL := list
VENV := .venv
PYTHON := $(VENV)/bin/python
SHELL := /bin/sh

.PHONY: list
list: ## Lists help commands
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-36s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: | $(VENV) ## Install project (editable + dev deps)
	$(PYTHON) -m pip install -e ".[dev]"

.PHONY: fmt
fmt: ## Format all python files
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

.PHONY: lint
lint: ## Lint all python files
	$(PYTHON) -m black --check .
	$(PYTHON) -m ruff check .

.PHONY: typecheck
typecheck: ## Run mypy
	$(PYTHON) -m mypy

.PHONY: test
test: ## Run unit tests
	$(PYTHON) -m pytest -x

.PHONY: coverage
coverage: ## Run tests with coverage and ensure it does not decrease
	@$(PYTHON) -m pytest --cov=src --cov-report=term --cov-report=json:.coverage.json
	@$(PYTHON) scripts/check_coverage.py $(if $(UPDATE),--update,)

.PHONY: ci
ci: lint typecheck coverage ## Run CI validation locally

.PHONY: ready
ready: fmt typecheck test ## Prepare to commit - Format, typecheck, and run tests

.PHONY: clean
clean: ## Remove venv and artifacts
	rm -rf $(VENV) .pytest_cache .mypy_cache build dist *.egg-info

$(VENV):
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
