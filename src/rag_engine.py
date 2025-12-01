import os

import chromadb
from docx import Document
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

load_dotenv()

class RagEngine:
    def __init__(self):
        # Initialize persistent ChromaDB client (creates 'chroma_db' folder for storage)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="private_docs"
        )

        # Load embedding model from environment or use default
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)

        # Initialize text splitter (1000 char chunks with 200 char overlap for context preservation)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", ",", " "],  # hierarchy
        )

    def _read_file(self, file_path):
        """Extract text content from file based on extension"""
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                return " ".join([page.extract_text() for page in reader.pages])
            elif ext == ".docx":
                doc = Document(file_path)
                return " ".join([para.text for para in doc.paragraphs])
            elif ext in [".txt", ".md", ".py", ".json"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return None
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def index_files(self, directory_path):
        print(f"Scanning directory: {directory_path}")
        count = 0
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Extract text content from file
                text = self._read_file(file_path)
                if not text or len(text) < 50:
                    continue

                # Split text into chunks for vector embedding
                chunks = self.text_splitter.split_text(text)

                print(f"Processing {file}: {len(chunks)} chunks found.")

                # Generate embeddings for each chunk
                ids = []
                metadatas = []
                embeddings = []

                for i, chunk in enumerate(chunks):
                    # Create unique identifier for this chunk
                    chunk_id = f"{file_path}_{i}"

                    ids.append(chunk_id)
                    embeddings.append(self.model.encode(chunk).tolist())
                    metadatas.append({"source": file_path, "chunk_index": i})

                # Persist chunks with embeddings to ChromaDB
                if ids:
                    self.collection.upsert(
                        ids=ids,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        documents=chunks,
                    )
                    count += 1

        print(f"Finished! Processed {count} files.")

    def search(self, query, n_results=3):
        """Search for relevant documents using vector similarity"""
        # Convert query text to embedding vector
        query_embedding = self.model.encode(query).tolist()

        # Execute similarity search in vector database
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )
        return results
