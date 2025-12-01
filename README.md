# Claude MCP: Local RAG with OneDrive Support

## What is this for?

This project lets Claude search and answer questions about your personal documents (like PDFs, Word files, text files, etc.) stored on your computer or OneDrive.

**How it works:**
1. Point it at a folder with your documents
2. It reads and indexes them locally on your machine (no data sent to external servers)
3. When you ask Claude a question, it can search through your documents and give you answers based on what's in your files

**Example use case:**
- You have project reports, meeting notes, and documentation scattered across files
- Instead of manually searching through them, you just ask Claude: "What's the status of the project?" or "Find information about the budget in my documents"
- Claude searches your indexed documents and gives you the answer

It's essentially giving Claude a "memory" of your personal documents, keeping everything private and local to your machine.

---

This Model Context Protocol (MCP) server allows Claude to access, index, and retrieve information from your private documents (Local files and OneDrive).

It uses a **RAG (Retrieval-Augmented Generation)** architecture with local embeddings, ensuring your data remains private and is processed efficiently on your machine.

## 🏗 Architecture

- **Manager:** `uv` (Fast Python package installer and resolver)
- **Embeddings:** `sentence-transformers` (Local execution, no API costs)
- **Vector Database:** `chromadb` (Local storage for semantic search)
- **Protocol:** `mcp` (Model Context Protocol Python SDK)

## 🚀 Prerequisites

1. **Python 3.11+**
2. **uv** (Python package manager)
3. **Claude Code** (CLI) or **Claude Desktop App**

## 🛠️ Installation

1. **Clone and Setup**
   ```bash
   git clone <repo-url>
   cd claude-mcp
   uv sync
````

2.  **Configuration**
    Create a `.env` file in the root directory:
    ```ini
    # MODEL CONFIGURATION
    EMBEDDING_MODEL=all-MiniLM-L6-v2

    # DATA SOURCES
    # WSL2 Example: /mnt/c/Users/YourUser/OneDrive/Documents
    # Mac/Linux Example: /home/user/documents
    DATA_PATH=/path/to/your/documents
    ```

-----

## 🔄 Workflow

This project separates **Ingestion** (Writing to memory) from **Querying** (Reading from memory).

### 1\. Ingest Data (Update Memory)

Run this command whenever you add new files to your folder. It reads the files, chunks them, and updates the local vector database.

```bash
uv run ingest.py
```

### 2\. Connect to Claude

#### Option A: Claude Code (CLI) - Recommended

Run this command once to register the tool in your local Claude configuration:

```bash
claude mcp add onedrive-rag -- uv --directory $(pwd) run src/main.py
```

Then, simply ask Claude:

> "Check my documents for the status of the project."

#### Option B: Claude Desktop (GUI)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "onedrive-rag": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/claude-mcp",
        "run",
        "src/main.py"
      ]
    }
  }
}
```

-----

## 📦 Project Structure

```text
claude-mcp/
├── .venv/               # Virtual environment
├── chroma_db/           # Local Vector Database (Ignored in Git)
├── src/                 # Source code
│   ├── main.py          # MCP Server Entry Point
│   └── rag_engine.py    # Logic for embeddings and retrieval
├── .env                 # Secrets and config
├── ingest.py            # Script to update the database
├── pyproject.toml       # Dependencies
└── README.md            # Documentation
```

## 🔧 Troubleshooting

**"ModuleNotFoundError: No module named 'src'"**
If you run the server manually, ensure you use `uv run src/main.py`. The code includes a `sys.path` fix to ensure imports work correctly regardless of the execution context.
