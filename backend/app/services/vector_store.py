import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
from config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            ),
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # Collections
        self.products_collection = None
        self.troubleshooting_collection = None

    def initialize_collections(self):
        """Initialize Chroma collections"""
        try:
            # Products collection
            self.products_collection = self.client.get_or_create_collection(
                name="products", metadata={"description": "Product catalog embeddings"}
            )

            # Troubleshooting collection
            self.troubleshooting_collection = self.client.get_or_create_collection(
                name="troubleshooting",
                metadata={"description": "Troubleshooting guides embeddings"},
            )

            logger.info("Vector collections initialized")
        except Exception as e:
            logger.error(f"Error initializing collections: {e}")
            raise

    def add_products(self, products: List[Dict[str, Any]]):
        """Add products to vector store"""
        if not self.products_collection:
            raise ValueError("Products collection not initialized")

        documents = []
        metadatas = []
        ids = []

        for product in products:
            # Create searchable document
            doc = f"{product['name']} {product['description']} {product['part_number']} {product['category']}"
            documents.append(doc)
            metadatas.append(
                {
                    "part_number": product["part_number"],
                    "name": product["name"],
                    "price": product["price"],
                    "category": product["category"],
                    "appliance_type": product["appliance_type"],
                }
            )
            ids.append(product["part_number"])

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to collection
        self.products_collection.add(
            embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
        )
        logger.info(f"Added {len(products)} products to vector store")

    def search_products(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search products using semantic similarity"""
        if not self.products_collection:
            raise ValueError("Products collection not initialized")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()

        # Search
        results = self.products_collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        # Format results
        products = []
        if results["metadatas"] and len(results["metadatas"][0]) > 0:
            for i, metadata in enumerate(results["metadatas"][0]):
                products.append(
                    {
                        **metadata,
                        "relevance_score": 1
                        - results["distances"][0][i],  # Convert distance to similarity
                    }
                )

        return products

    def add_troubleshooting_docs(self, docs: List[Dict[str, str]]):
        """Add troubleshooting documents to vector store"""
        if not self.troubleshooting_collection:
            raise ValueError("Troubleshooting collection not initialized")

        documents = []
        metadatas = []
        ids = []

        for idx, doc in enumerate(docs):
            documents.append(doc["content"])
            metadatas.append(
                {
                    "title": doc["title"],
                    "category": doc.get("category", "general"),
                    "appliance_type": doc.get("appliance_type", "general"),
                }
            )
            ids.append(f"troubleshooting_{idx}")

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to collection
        self.troubleshooting_collection.add(
            embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
        )
        logger.info(f"Added {len(docs)} troubleshooting docs to vector store")

    def search_troubleshooting(
        self, query: str, n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search troubleshooting guides"""
        if not self.troubleshooting_collection:
            raise ValueError("Troubleshooting collection not initialized")

        query_embedding = self.embedding_model.encode([query])[0].tolist()

        results = self.troubleshooting_collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        docs = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                docs.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "relevance_score": 1 - results["distances"][0][i],
                    }
                )

        return docs


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.initialize_collections()
    return _vector_store


def initialize_vector_store():
    """Initialize vector store on startup"""
    get_vector_store()
