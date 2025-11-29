import os
import sys
from dotenv import load_dotenv

# Ensure we can find the src module regardless of how the script is run
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.rag_engine import RagEngine

def main():
    """
    Main entry point for document ingestion.
    Runs the indexing process to update ChromaDB with new files from the DATA_PATH.
    """
    # Load environment variables
    load_dotenv()

    # 1. Validation: Check if path is configured
    data_path = os.getenv("DATA_PATH")
    if not data_path:
        print("Error: DATA_PATH is not defined in the .env file.")
        print("Please check your .env configuration.")
        return

    if not os.path.exists(data_path):
        print(f"Error: The path '{data_path}' does not exist.")
        return

    # 2. User Feedback
    print("==================================================")
    print("KNOWLEDGE BASE INGESTION")
    print(f"📂 Target: {data_path}")
    print("==================================================")

    # 3. Execution: Run the indexer
    try:
        rag = RagEngine()
        rag.index_files(data_path)

        print("\n✅ SUCCESS: Knowledge base updated.")
        print("Claude is now ready to answer questions about these files.")

    except Exception as e:
        print(f"\n❌ ERROR during ingestion: {e}")

if __name__ == "__main__":
    main()
