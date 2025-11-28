import sys
import os

# --- FIX: Agregamos la raíz del proyecto al Path de Python ---
# Esto permite que el script encuentre el módulo 'src' aunque esté dentro de él
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# -------------------------------------------------------------

from mcp.server.fastmcp import FastMCP
from src.rag_engine import RagEngine

# Inicializamos el servidor MCP
mcp = FastMCP("OneDrive Knowledge Base")

# Inicializamos el motor RAG globalmente
rag = RagEngine()

@mcp.tool()
def ask_onedrive(question: str) -> str:
    """
    Search in the user's private OneDrive documents/knowledge base to answer a question.
    Use this tool when the user asks about their own files, reports, projects, or status.

    Args:
        question: The full question or search query related to the documents.
    """
    # 1. Buscar en la base de datos
    results = rag.search(question, n_results=5)

    # Check if results is None or doesn't contain expected structure
    if not results or 'documents' not in results or not results['documents']:
        return "No relevant information found in the documents."

    documents = results['documents'][0]

    if not documents:
        return "No relevant information found in the documents."

    # 2. Formatear la respuesta
    context = "\n\n---\n\n".join(documents)

    return f"Here is the relevant information found in the documents:\n\n{context}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
