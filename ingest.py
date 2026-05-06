import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can find the src module regardless of how the script is run
sys.path.append(str(Path(__file__).resolve().parent))

from src.rag_engine import RagEngine

def main():
    """
    Main entry point for document ingestion.
    Runs the indexing process to update ChromaDB with new files from the DATA_PATH.
    """
    # Load environment variables
    load_dotenv()

    # 1. Validation: Check if path is configured
    data_path_raw = os.getenv("DATA_PATH")
    if not data_path_raw:
        print("Error: DATA_PATH is not defined in the .env file.")
        print("Please check your .env configuration.")
        return

    # Resolve to an absolute path; handles ~, mixed slashes, and relative paths.
    data_path = Path(data_path_raw).expanduser().resolve()

    if not data_path.exists():
        print(f"Error: The path '{data_path}' does not exist.")
        return

    if not data_path.is_dir():
        print(f"Error: The path '{data_path}' is not a directory.")
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
