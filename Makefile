# Makefile for Claude MCP Private Knowledge Base

.PHONY: help setup ingest server connect clean clean-all

# Default target: Display available commands
help:
	@echo "🤖 Claude MCP - Available Commands:"
	@echo "-----------------------------------"
	@echo "make setup    - Install dependencies with uv"
	@echo "make ingest   - Update knowledge base from local documents (Run this after adding files)"
	@echo "make server   - Run the MCP server manually (for debugging)"
	@echo "make connect  - Register this tool with Claude Code (CLI)"
	@echo "make clean    - Remove Python cache files only"
	@echo "make clean-all - Remove cache files AND database (requires re-ingestion)"

setup:
	@echo "Installing dependencies..."
	uv sync

ingest:
	@echo "Updating knowledge base..."
	uv run ingest.py

server:
	@echo "Starting MCP server (Ctrl+C to stop)..."
	uv run src/main.py

connect:
	@echo "Connecting to Claude Code..."
	claude mcp add private-kb -- uv --directory $$(pwd) run src/main.py

clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Cache cleaned!"

clean-all:
	@echo "WARNING: This will remove ALL data including the indexed database!"
	@echo "You will need to run 'make ingest' to rebuild the knowledge base."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Removing database..."
	rm -rf chroma_db
	@echo "All data cleaned! Run 'make ingest' to rebuild."
