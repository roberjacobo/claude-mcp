import os
from dotenv import load_dotenv
from src.rag_engine import RagEngine

# Load variables from the .env file
load_dotenv()

# Instantiate the engine
rag = RagEngine()

# 1. Index (Read your files)
# This will read the path you defined in DATA_PATH in your .env
data_path = os.getenv("DATA_PATH")
print(f"--- Starting indexing from: {data_path} ---")

if data_path:
    rag.index_files(data_path)
else:
    print("Error: DATA_PATH is not defined in the .env file")

# 2. Test a search
print("\n--- Testing search ---")
question = "status"  # You can change this to something you know is in your docs
results = rag.search(question)

# Display the first result found
if results['documents'] and results['documents'][0]:
    print("\nFound answer:")
    print(results['documents'][0][0])
else:
    print("No results found.")
