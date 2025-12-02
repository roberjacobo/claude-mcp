import sys
import os

# Add project root to Python path to enable imports from src module
# This allows the script to locate the 'src' module regardless of execution context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP
from src.rag_engine import RagEngine

# Initialize MCP server for private document search
mcp = FastMCP("Private Knowledge Base")

# Initialize RAG engine globally for document retrieval
rag = RagEngine()

@mcp.tool()
def ask_knowledge_base(question: str) -> str:
    """
    Search in the user's private knowledge base to answer a question.
    Use this tool when the user asks about their own files, reports, projects, or status.

    This knowledge base contains indexed documents including:
    - Project documentation and overviews
    - User manuals and technical guides
    - Reports and status updates
    - Meeting notes and personal files

    Use this tool proactively when the user asks questions about:
    - How something works in their projects
    - Project specifications or requirements
    - Status, progress, or timelines from their documents
    - Technical details from manuals or guides
    - Any information that might be in their personal documents

    Args:
        question: The full question or search query related to the documents.
    """
    # Search vector database for relevant document chunks
    results = rag.search(question, n_results=5)

    # Check if results is None or doesn't contain expected structure
    if not results or 'documents' not in results or not results['documents']:
        return "No relevant information found in the documents."

    documents = results['documents'][0]

    if not documents:
        return "No relevant information found in the documents."

    # Format retrieved chunks into cohesive response
    context = "\n\n---\n\n".join(documents)

    return f"Here is the relevant information found in the documents:\n\n{context}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
