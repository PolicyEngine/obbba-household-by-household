# Makefile for OBBBA Scatter project

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make dev          Start development server"
	@echo "  make build        Build for production"
	@echo "  make test         Run tests"
	@echo "  make data         Generate optimized data files"
	@echo "  make data-copy    Copy generated data to static directory"
	@echo "  make clean        Clean generated files"

# Install dependencies
.PHONY: install
install:
	npm install

# Development server
.PHONY: dev
dev:
	npm run dev

# Production build
.PHONY: build
build:
	npm run build

# Run tests
.PHONY: test
test:
	npm test

# Generate data files (both formats)
.PHONY: data
data:
	@echo "Generating data files..."
	@echo "Note: This requires Python 3 with numpy, pandas, and policyengine_us installed"
	@echo "To install: pip install numpy pandas policyengine_us"
	@echo ""
	cd data && python3 generate_data.py

# Clean generated files
.PHONY: clean
clean:
	rm -f data/households_*.csv
	rm -f data/provisions_*.csv
	rm -rf build/
	rm -rf .svelte-kit/