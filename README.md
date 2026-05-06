# Claude MCP: Private Knowledge Base

## What is this for?

This project lets Claude search and answer questions about your personal documents (like PDFs, Word files, text files, etc.) stored anywhere on your computer.

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

This Model Context Protocol (MCP) server allows Claude to access, index, and retrieve information from your private documents stored locally on your machine.

It uses a **RAG (Retrieval-Augmented Generation)** architecture with local embeddings, ensuring your data remains private and is processed efficiently on your machine.

## 🏗 Architecture

- **Manager:** `uv` (Fast Python package installer and resolver)
- **Embeddings:** `sentence-transformers` (Local execution, no API costs)
- **Vector Database:** `chromadb` (Local storage for semantic search)
- **Protocol:** `mcp` (Model Context Protocol Python SDK)

## 🚀 Prerequisites

1. **Python 3.11+**
2. **uv** (Python package manager) — install with:
   ```powershell
   # Windows PowerShell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   ```bash
   # Linux / macOS / WSL
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   The installer adds `uv` to your `PATH` (`%USERPROFILE%\.local\bin` on Windows, `~/.local/bin` on Linux/macOS). **Restart your terminal** (or run `. $PROFILE` on PowerShell / `source ~/.bashrc` / `source ~/.zshrc`) so the new `PATH` takes effect, then verify with `uv --version`.

   If `uv` still isn't found after restarting, add it to `PATH` manually:
   ```powershell
   # Windows PowerShell — persistent for your user
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\.local\bin", "User")
   ```
   ```bash
   # Linux / macOS / WSL — append to your shell profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc   # or ~/.zshrc
   ```
   Other install options (Homebrew, pipx, winget) at [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).
3. **Claude Code** (CLI) or **Claude Desktop App**

## 🛠️ Installation

1. **Clone and Setup**
   ```bash
   git clone <repo-url>
   cd claude-mcp
   uv sync
   ```

2. **Configuration**
    Copy `.env.example` to `.env` and edit the values:
    ```bash
    cp .env.example .env            # Linux / Mac / WSL
    copy .env.example .env          # Windows CMD
    Copy-Item .env.example .env     # Windows PowerShell
    ```

    Example contents:
    ```ini
    # MODEL CONFIGURATION
    EMBEDDING_MODEL=all-MiniLM-L6-v2

    # DATA SOURCES
    # Windows (native): C:\Users\YourUser\Documents
    # WSL2:             /mnt/c/Users/YourUser/Documents
    # macOS:            /Users/YourUser/Documents
    # Linux:            /home/youruser/documents
    # Works with any local folder (OneDrive, Google Drive, Dropbox, etc.).
    DATA_PATH=C:\Users\YourUser\Documents
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

**Global Installation (Available in ALL projects):**
```bash
make connect-global
# OR manually:
claude mcp add --scope user private-kb -- uv --directory $(pwd) run src/main.py
```

**Local Installation (Current project only):**
```bash
make connect
# OR manually:
claude mcp add private-kb -- uv --directory $(pwd) run src/main.py
```

Then, simply ask Claude from any project (if using global):

> "Check my documents for the status of the project."

#### Option B: Claude Desktop (GUI)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "private-kb": {
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

## 🧹 Maintenance Commands

**Clean cache files:**
```bash
make clean
```
Removes Python cache files (`__pycache__`, `*.pyc`, `*.pyo`) safely without affecting your indexed data.

**Clean everything (including database):**
```bash
make clean-all
```
Removes cache files AND the entire ChromaDB database. **Warning:** This requires re-running `make ingest` to rebuild your knowledge base.

## ❓ FAQ

**How is the embedding model downloaded?**
Automatically. The first time you run `uv run ingest.py` (or the MCP server), `sentence-transformers` downloads the model from the HuggingFace Hub into your local cache (`~/.cache/huggingface/hub/` on Linux/Mac, `C:\Users\<you>\.cache\huggingface\hub\` on Windows). After that, it loads from cache instantly. No account or manual setup required.

**Can I use a different model?**
Yes — just change `EMBEDDING_MODEL` in `.env` to any model from [sentence-transformers on HuggingFace](https://huggingface.co/sentence-transformers). For example, `BAAI/bge-base-en-v1.5` or `intfloat/e5-base-v2` are more accurate (~440 MB), and `BAAI/bge-large-en-v1.5` is even better (~1.3 GB). The default `all-MiniLM-L6-v2` is the smallest and fastest (~90 MB). After switching, run `make clean-all` and re-ingest, since embeddings from different models aren't compatible.

**What happens to the old model when I switch?**
Nothing — it stays in the HuggingFace cache (shared across all your projects) and keeps taking disk space until you delete it manually. The vectors stored in `chroma_db/` from the old model become unusable, which is why `make clean-all` + re-ingest is required after switching. To free space, delete the old model's folder from the cache:
```powershell
# Windows PowerShell — example deleting the default MiniLM model
Remove-Item -Recurse "$env:USERPROFILE\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2"
```
```bash
# Linux / macOS / WSL
rm -rf ~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2
```
If a project needs it again later, it'll just re-download.

---

## 🔧 Troubleshooting

**"ModuleNotFoundError: No module named 'src'"**
If you run the server manually, ensure you use `uv run src/main.py`. The code includes a `sys.path` fix to ensure imports work correctly regardless of the execution context.
