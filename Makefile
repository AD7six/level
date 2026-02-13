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
	$(PYTHON) -m mypy src

.PHONY: test
test: ## Run unit tests
	$(PYTHON) -m pytest -q

.PHONY: clean
clean: ## Remove venv and artifacts
	rm -rf $(VENV) .pytest_cache .mypy_cache build dist *.egg-info

$(VENV):
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
