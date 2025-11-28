-----

### `README.md`

````markdown
# Claude MCP: Local RAG with OneDrive Support

This Model Context Protocol (MCP) server allows Claude to access, index, and retrieve information from your private documents (Local files and OneDrive).

It uses a **RAG (Retrieval-Augmented Generation)** architecture with local embeddings, ensuring your data remains private and is processed efficiently on your machine.

## Architecture

- **Manager:** `uv` (Fast Python package installer and resolver)
- **Embeddings:** `sentence-transformers` (Local execution, no API costs)
- **Vector Database:** `chromadb` (Local storage for semantic search)
- **Protocol:** `mcp` (Model Context Protocol Python SDK)

## 🚀 Prerequisites

1. **Python 3.11+**
2. **uv** (An extremely fast Python package manager)
   - *MacOS/Linux/WSL2:* `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - *Windows:* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

---

## 🛠️ Installation & Setup

Follow these steps to replicate the environment on your OS.

### 1. Clone or Create Project
```bash
# If cloning
git clone <repository-url>
cd claude-mcp

# If starting from scratch (already done if following the tutorial)
uv init claude-mcp
cd claude-mcp
````

### 2\. Environment Setup

#### 🍎 macOS / 🐧 Linux / 🦖 WSL2

```bash
# Create virtual environment
uv venv --python 3.11

# Activate environment
source .venv/bin/activate

# Install dependencies (will sync from pyproject.toml)
uv sync
```

#### 🪟 Windows (PowerShell)

```powershell
# Create virtual environment
uv venv --python 3.11

# Activate environment
.venv\Scripts\activate

# Install dependencies
uv sync
```

-----

## ⚙️ Configuration

Create a `.env` file in the root directory to manage your configuration and secrets.

```bash
# Copy the example file (if available)
cp .env.example .env
```

**Content of `.env`:**

```ini
# MODEL CONFIGURATION
# Using local model (default)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# DATA SOURCES
# Define the root path where your documents are located
DOCS_PATH=./data
# For OneDrive/SharePoint specific integrations (Future implementation)
ONEDRIVE_FOLDER_ID=your_folder_id
```

-----

## 🏃‍♂️ Usage

To start the MCP server:

```bash
# Using uv to run the entry point
uv run mcp-server
```

Once running, you can configure Claude Desktop to connect to this server by editing your `claude_desktop_config.json`.

## 📦 Project Structure

```text
claude-mcp/
├── .venv/               # Virtual environment
├── data/                # Place your documents here for testing
├── src/                 # Source code
│   ├── main.py          # Entry point
│   └── rag_engine.py    # Logic for embeddings and retrieval
├── .env                 # Secrets and config
├── pyproject.toml       # Dependencies managed by uv
└── README.md            # Documentation
```

```

***

### Siguiente Paso: Hacer realidad el README

El README promete que el proyecto funciona con `uv sync` y que usa `sentence-transformers` y `chromadb`, pero **aún no hemos instalado esas librerías** en tu proyecto real.

Para cumplir con lo que dice tu documentación y preparar el terreno para el código, ¿te parece bien si ejecutamos ahora el comando para instalar las dependencias del motor "Local"?
```
