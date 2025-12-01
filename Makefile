# Makefile for Claude MCP OneDrive RAG

.PHONY: help setup ingest server connect clean

# Default target: Display available commands
help:
	@echo "🤖 Claude MCP - Available Commands:"
	@echo "-----------------------------------"
	@echo "make setup    - Install dependencies with uv"
	@echo "make ingest   - Update knowledge base from OneDrive (Run this after adding files)"
	@echo "make server   - Run the MCP server manually (for debugging)"
	@echo "make connect  - Register this tool with Claude Code (CLI)"
	@echo "make clean    - Remove cache files"

setup:
	@echo "Installing dependencies..."
	uv sync

ingest:
	@echo "Updating memory..."
	uv run ingest.py

server:
	@echo "Starting MCP server (Ctrl+C to stop)..."
	uv run src/main.py

connect:
	@echo "Connecting to Claude Code..."
	claude mcp add onedrive-rag -- uv --directory $$(pwd) run src/main.py

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf src/__pycache__
