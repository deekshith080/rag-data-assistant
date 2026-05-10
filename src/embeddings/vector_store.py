"""
Stores table schemas as embeddings in ChromaDB.
Uses Ollama for free local embeddings — no API key needed.
"""

import sys
sys.path.insert(0, ".")
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from src.database.schema_extractor import SchemaExtractor

CHROMA_PATH = "data/chromadb"
COLLECTION_NAME = "table_schemas"

class VectorStore:
    """
    Manages ChromaDB vector store for table schemas.
    Uses Ollama nomic-embed-text for free local embeddings.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.embedding_fn = OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="nomic-embed-text",
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
        )
        print(f"ChromaDB collection ready: {COLLECTION_NAME}")

    def index_schemas(self, force_reindex=False):
        """Index all table schemas into ChromaDB."""
        if force_reindex:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
            )
            print("Cleared existing collection.")

        existing = self.collection.count()
        if existing > 0 and not force_reindex:
            print(f"Collection already has {existing} schemas. Skipping reindex.")
            return

        extractor = SchemaExtractor()
        schemas = extractor.extract_all_schemas()

        documents = []
        metadatas = []
        ids = []

        for schema in schemas:
            documents.append(schema["schema_text"])
            metadatas.append({"table_name": schema["table_name"]})
            ids.append("schema_" + schema["table_name"])

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"Indexed {len(schemas)} schemas into ChromaDB.")

    def retrieve_relevant_schemas(self, query: str, n_results: int = 3) -> list:
        """Find most relevant table schemas for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        schemas = []
        for i, doc in enumerate(results["documents"][0]):
            table_name = results["metadatas"][0][i]["table_name"]
            distance = results["distances"][0][i]
            schemas.append({
                "table_name": table_name,
                "schema_text": doc,
                "relevance_score": round(1 - distance, 4),
            })
            print(f"Retrieved: {table_name} (relevance: {round(1-distance, 4)})")
        return schemas

    def get_schema_count(self) -> int:
        return self.collection.count()


if __name__ == "__main__":
    print("Step 1: Initializing ChromaDB...")
    store = VectorStore()

    print("Step 2: Indexing schemas...")
    store.index_schemas(force_reindex=True)

    print(f"Total schemas indexed: {store.get_schema_count()}")

    print("Step 3: Testing retrieval...")
    print(chr(10) + "Query: show me revenue by customer")
    store.retrieve_relevant_schemas("show me revenue by customer")

    print(chr(10) + "Query: which customers have open support tickets")
    store.retrieve_relevant_schemas("which customers have open support tickets")