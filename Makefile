.DEFAULT_GOAL := help

.PHONY: run
run: ## Runs agent
	poetry run streamlit run ava/main.py --server.address 0.0.0.0

.PHONY: install
install: ## Install dependencies
	poetry install

.PHONY: lint
lint: ## Run linter
	poetry run pylint ava

.PHONY: format
format: ## Format source code
	poetry run isort ava
	poetry run black ava

.PHONY: clean
clean: ## Clear __pycache__ and .pyc files
	find . | grep -E "(__pycache__|\.pyc$)" | find -v .venv | xargs rm -rf

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
