import os
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document
from dotenv import load_dotenv

load_dotenv()

class RagEngine:
    def __init__(self):
        # Initialize Database
        # This creates a folder 'chroma_db' to save data
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")

        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(name="onedrive_docs")

        # Load Embedding Model
        # Uses the model defined in .env
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def _read_file(self, file_path):
        """Reads content based on file extensionn"""
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                reader = PdfReader(file_path)
                return " ".join([page.extract_text() for page in reader.pages])
            elif ext == '.docx':
                doc = Document(file_path)
                return " ".join([para.text for para in doc.paragraphs])
            elif ext in ['.txt', '.md', '.py', '.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return None # Unsupported file
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def index_files(self, directory_path):
        """Reads files and saves vectors to DB"""
        print(f"Scanning directory: {directory_path}")

        count = 0
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)

                # 1. Read Text
                text = self._read_file(file_path)
                if not text or len(text) < 50: # Skip empty/short files
                    continue

                # 2. Convert to Vector (Embedding)
                # We turn text into a list of number
                embedding = self.model.encode(text).tolist()

                # 3. Save to ChromaDB
                self.collection.upsert(
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[{"source": file_path}],
                    ids=[file_path] # Use path as unique ID
                )
                print(f"Indexed: {file}")
                count += 1

        print(f"Finished! Indexed {count} documents.")

    def search(self, query, n_results=3):
        """Search for relevant documents"""
        # 1. Convert query to vector
        query_embedding = self.model.encode(query).tolist()

        # 2. Search in DB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
