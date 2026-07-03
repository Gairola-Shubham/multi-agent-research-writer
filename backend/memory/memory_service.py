import os
from typing import Any, Dict, List, Optional

import chromadb

from backend.core.config import settings
from backend.core.logger import logger


class MemoryServiceError(Exception):
    """Base exception for memory service errors."""

    pass


class MemoryServiceInitError(MemoryServiceError):
    """Raised when memory database initialization fails."""

    pass


class MemoryService:
    def __init__(
        self, db_path: Optional[str] = None, collection_name: str = "research_memory"
    ):
        self.db_path = db_path or settings.CHROMA_DB_PATH
        self.collection_name = collection_name

        # Ensure parent directory of db_path exists
        try:
            os.makedirs(self.db_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create database directory {self.db_path}: {e}")
            raise MemoryServiceInitError(
                f"Failed to create database directory: {e}"
            ) from e

        logger.info(
            "Initializing MemoryService with db_path="
            f"'{self.db_path}' and collection='{self.collection_name}'"
        )
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info("ChromaDB memory service database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB persistent client: {e}")
            raise MemoryServiceInitError(f"ChromaDB initialization failed: {e}") from e

    def add_document(self, document_id: str, text: str, metadata: dict) -> None:
        """
        Adds a document to the ChromaDB database.
        """
        if (
            not document_id
            or not isinstance(document_id, str)
            or not document_id.strip()
        ):
            raise ValueError("document_id must be a non-empty string.")
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string.")
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary.")

        # Validate metadata values (Chroma requires primitive types:
        # str, int, float, bool)
        for k, v in metadata.items():
            if not isinstance(k, str):
                raise ValueError(f"Metadata key must be a string: {k}")
            if v is not None and not isinstance(v, (str, int, float, bool)):
                raise ValueError(
                    f"Metadata value for key '{k}' must be str, int, float, "
                    f"or bool. Got {type(v)}."
                )

        # Check for duplicate ID
        try:
            existing = self.collection.get(ids=[document_id])
            if existing and existing.get("ids"):
                raise ValueError(f"Document with ID '{document_id}' already exists.")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            raise MemoryServiceError(f"Failed to verify document existence: {e}") from e

        logger.info(f"Adding document to database: document_id='{document_id}'")
        try:
            # None metadata values are not supported by some ChromaDB queries,
            # so we clean them
            cleaned_metadata = {k: v for k, v in metadata.items() if v is not None}
            self.collection.add(
                ids=[document_id], documents=[text], metadatas=[cleaned_metadata]
            )
            logger.info(f"Document successfully added: document_id='{document_id}'")
        except Exception as e:
            logger.error(f"Failed to add document '{document_id}' to ChromaDB: {e}")
            raise MemoryServiceError(f"Failed to add document: {e}") from e

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches ChromaDB for the most relevant documents.
        """
        logger.info(f"Search started with query='{query}', top_k={top_k}")
        if not query or not isinstance(query, str) or not query.strip():
            logger.warning("Empty search query received. Returning empty list.")
            return []

        try:
            res = self.collection.query(query_texts=[query], n_results=top_k)

            results = []
            if res and res.get("ids") and len(res["ids"][0]) > 0:
                for idx in range(len(res["ids"][0])):
                    results.append(
                        {
                            "id": res["ids"][0][idx],
                            "text": res["documents"][0][idx]
                            if res.get("documents")
                            else "",
                            "metadata": res["metadatas"][0][idx]
                            if res.get("metadatas")
                            else {},
                            "distance": res["distances"][0][idx]
                            if res.get("distances")
                            else 0.0,
                        }
                    )
            logger.info(f"Search completed successfully. Found {len(results)} matches.")
            return results
        except Exception as e:
            logger.error(f"Search failed for query='{query}': {e}")
            raise MemoryServiceError(f"Search failed: {e}") from e

    def delete_document(self, document_id: str) -> None:
        """
        Deletes a single document by ID from ChromaDB.
        """
        if (
            not document_id
            or not isinstance(document_id, str)
            or not document_id.strip()
        ):
            raise ValueError("document_id must be a non-empty string.")

        # Check for missing document
        try:
            existing = self.collection.get(ids=[document_id])
            if not existing or not existing.get("ids"):
                raise KeyError(f"Document with ID '{document_id}' not found.")
        except KeyError:
            raise
        except Exception as e:
            logger.error(f"Error checking document existence for deletion: {e}")
            raise MemoryServiceError(f"Failed to verify document existence: {e}") from e

        logger.info(f"Deleting document: document_id='{document_id}'")
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Document successfully deleted: document_id='{document_id}'")
        except Exception as e:
            logger.error(
                f"Failed to delete document '{document_id}' from ChromaDB: {e}"
            )
            raise MemoryServiceError(f"Failed to delete document: {e}") from e

    def clear(self) -> None:
        """
        Clears the entire database (drops and recreates the collection).
        """
        logger.info(f"Clearing collection='{self.collection_name}' in memory service.")
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info("Memory database cleared successfully.")
        except Exception as e:
            logger.error(f"Failed to clear memory database: {e}")
            raise MemoryServiceError(f"Failed to clear database: {e}") from e
