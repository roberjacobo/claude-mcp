# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides Claude with RAG (Retrieval-Augmented Generation) capabilities for private documents. It uses local embeddings and vector search to query personal documents stored on your machine without sending data to external APIs.

**Key Technologies:**
- **Package Manager:** `uv` (fast Python package installer)
- **Embeddings:** `sentence-transformers` (local, no API costs)
- **Vector Database:** `chromadb` (persistent local storage)
- **Protocol:** `mcp` (FastMCP for server implementation)
- **Document Processing:** `pypdf`, `python-docx`, `langchain-text-splitters`

## Common Commands

```bash
# Setup and Dependencies
uv sync                          # Install/update all dependencies
make setup                       # Same as above, using Makefile

# Knowledge Base Ingestion
uv run ingest.py                 # Index files from DATA_PATH (run after adding new documents)
make ingest                      # Same as above

# Running the MCP Server
uv run src/main.py               # Start MCP server manually (for debugging)
make server                      # Same as above

# Connect to Claude
make connect                     # Register MCP server with Claude Code CLI
# Manual registration:
claude mcp add private-kb -- uv --directory $(pwd) run src/main.py

# Maintenance
make clean                       # Remove Python cache files only (safe)
make clean-all                   # Remove cache + database (requires re-ingestion)
make help                        # Show available Makefile commands
```

## Architecture

This project separates **data ingestion** (write) from **querying** (read):

### 1. Ingestion Pipeline (`ingest.py`)
- Reads environment variable `DATA_PATH` from `.env`
- Recursively scans directory for supported files (.pdf, .docx, .txt, .md, .py, .json)
- Uses `RecursiveCharacterTextSplitter` to chunk documents (1000 chars, 200 overlap)
- Generates embeddings using `sentence-transformers` model (default: all-MiniLM-L6-v2)
- Stores chunks with embeddings in ChromaDB collection `onedrive_docs`
- Each chunk has metadata: `source` (file path) and `chunk_index`

### 2. Query Pipeline (`src/main.py` + `src/rag_engine.py`)
- **MCP Server** (`main.py`): Exposes `ask_onedrive(question)` tool via FastMCP
- **RAG Engine** (`rag_engine.py`): Handles embedding generation and vector search
- Query flow:
  1. Convert question to embedding vector
  2. Search ChromaDB collection for top N similar chunks (default: 5)
  3. Return concatenated chunks as context

### 3. Key Components

**RagEngine Class** (`src/rag_engine.py`):
- `__init__()`: Initializes ChromaDB client, SentenceTransformer model, text splitter
- `_read_file(file_path)`: Extracts text from different file formats
- `index_files(directory_path)`: Recursive file scanning and indexing
- `search(query, n_results)`: Vector similarity search

**MCP Tool** (`src/main.py`):
- `ask_knowledge_base(question)`: The single MCP tool exposed to Claude
- Returns formatted context from top matching document chunks

## Important Path Handling

Both `ingest.py` and `src/main.py` include `sys.path` manipulation to allow imports to work regardless of execution context:

```python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

Always use `uv run <script>` to ensure the virtual environment is activated and imports work correctly.

## Environment Configuration

Required `.env` file in project root:

```ini
# Embedding model (from HuggingFace sentence-transformers)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Path to documents directory (WSL2, Mac, or Linux path)
DATA_PATH=/path/to/your/documents
```

**Note:** On WSL2, Windows paths are mounted at `/mnt/c/Users/...`

## Database Storage

- Location: `./chroma_db/` (gitignored)
- Persistent storage: ChromaDB uses SQLite internally
- Collection name: `private_docs`
- Chunk IDs format: `{file_path}_{chunk_index}`

## Workflow

1. **Initial Setup:**
   ```bash
   uv sync
   # Create .env with DATA_PATH
   uv run ingest.py
   make connect
   ```

2. **Adding New Documents:**
   ```bash
   # Add files to DATA_PATH directory
   uv run ingest.py  # Re-index (upserts existing, adds new)
   ```

3. **Querying via Claude:**
   Ask Claude questions like: "What's the status of the project?" or "Search my documents for X"
   Claude will automatically use the `ask_knowledge_base` tool.

## Development Notes

- The text splitter uses hierarchical separators: `["\n\n", "\n", ".", ",", " "]`
- Chunk size of 1000 chars balances context vs. precision
- 200-char overlap prevents information loss at chunk boundaries
- `upsert()` is used instead of `add()` to allow re-ingestion without duplicates
- Files under 50 chars are skipped during indexing
- The MCP server runs with `transport='stdio'` for Claude integration
