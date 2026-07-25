.DEFAULT_GOAL := help

.PHONY: help setup run format lint typecheck test test-integration eval check clean

help: ## Display available commands
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ \
	{printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install development dependencies
	./scripts/bootstrap.sh

run: ## Run the application locally
	./scripts/run.sh

format: ## Format source files
	./scripts/format.sh

lint: ## Run static analysis
	./scripts/lint.sh

typecheck: ## Run type checking
	./scripts/typecheck.sh

test: ## Run deterministic unit tests
	./scripts/test.sh unit

test-integration: ## Run integration tests
	./scripts/test.sh integration

eval: ## Run agent behavior evaluations
	./scripts/eval.sh

check: format lint typecheck test test-integration ## Run required local checks
	@echo "All checks passed."

clean: ## Remove generated local artifacts
	./scripts/clean.sh
