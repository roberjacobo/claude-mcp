from mcp.server.fastmcp import FastMCP
from src.rag_engine import RagEngine

# Initialize the MCP Server
# "OneDrive Knowledge Base" is the name Claude will see internally
mcp = FastMCP("OneDrive Knowledge Base")

# Initialize our RAG engine (Database + Models)
# We do this globally so it loads only once when the server starts
rag = RagEngine()

@mcp.tool()
def ask_onedrive(question: str) -> str:
    """
    Search in the user's private OneDrive documents/knowledge base to answer a question.
    Use this tool when the user asks about their own files, reports, projects, or status.

    Args:
        question: The full question or search query related to the documents.
    """
    # 1. Search in the vector database
    # We retrieve 5 chunks to give Claude enough context
    results = rag.search(question, n_results=5)

    documents = results['documents'][0]

    if not documents:
        return "No relevant information found in the documents."

    # 2. Format the context
    # We join the found fragments into a single text block with separators
    context = "\n\n---\n\n".join(documents)

    return f"Here is the relevant information found in the documents:\n\n{context}"

if __name__ == "__main__":
    # Run the server using standard input/output (stdio)
    mcp.run(transport='stdio')
