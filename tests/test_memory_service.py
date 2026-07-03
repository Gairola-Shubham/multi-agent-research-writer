import shutil
import tempfile

import pytest

from backend.memory.memory_service import MemoryService, MemoryServiceInitError


@pytest.fixture
def temp_db_dir():
    # Setup temporary directory for isolated database tests
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_memory_service_init_and_paths(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")
    assert service.db_path == temp_db_dir
    assert service.collection_name == "test_collection"
    assert service.collection is not None


def test_memory_service_add_and_search(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")

    # Add a document
    doc_id = "doc1"
    doc_text = "Quantum computing relies on qubits which exist in superposition states."
    doc_meta = {"author": "Dr. Smith", "year": 2026, "valid": True}

    service.add_document(document_id=doc_id, text=doc_text, metadata=doc_meta)

    # Search for it
    results = service.search(query="superposition states", top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["text"] == doc_text
    assert results[0]["metadata"] == doc_meta
    assert "distance" in results[0]


def test_memory_service_duplicate_id_error(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")

    service.add_document(document_id="doc1", text="some text", metadata={"key": "val"})

    with pytest.raises(ValueError, match="already exists"):
        service.add_document(
            document_id="doc1", text="different text", metadata={"key": "val"}
        )


def test_memory_service_invalid_inputs(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")

    # Invalid IDs
    with pytest.raises(ValueError, match="document_id must be a non-empty string"):
        service.add_document(document_id="", text="text", metadata={})
    with pytest.raises(ValueError, match="document_id must be a non-empty string"):
        service.add_document(document_id=None, text="text", metadata={})

    # Invalid texts
    with pytest.raises(ValueError, match="text must be a non-empty string"):
        service.add_document(document_id="id1", text="", metadata={})
    with pytest.raises(ValueError, match="text must be a non-empty string"):
        service.add_document(document_id="id1", text=None, metadata={})

    # Invalid metadatas
    with pytest.raises(ValueError, match="metadata must be a dictionary"):
        service.add_document(document_id="id1", text="text", metadata=None)
    with pytest.raises(ValueError, match="metadata must be a dictionary"):
        service.add_document(document_id="id1", text="text", metadata="not a dict")

    # Invalid metadata value types
    with pytest.raises(ValueError, match="must be str, int, float, or bool"):
        service.add_document(
            document_id="id1", text="text", metadata={"nested": {"a": 1}}
        )
    with pytest.raises(ValueError, match="must be str, int, float, or bool"):
        service.add_document(document_id="id1", text="text", metadata={"list": [1, 2]})


def test_memory_service_delete_document(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")

    service.add_document(
        document_id="doc_to_del", text="text block", metadata={"temp": True}
    )

    # Verify it exists
    res1 = service.search("text block", top_k=1)
    assert len(res1) == 1
    assert res1[0]["id"] == "doc_to_del"

    # Delete it
    service.delete_document("doc_to_del")

    # Verify missing check raises KeyError
    with pytest.raises(KeyError, match="not found"):
        service.delete_document("doc_to_del")

    # Verify search returns empty or doesn't find it
    res2 = service.search("text block", top_k=1)
    assert len(res2) == 0


def test_memory_service_delete_missing_document_error(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")
    with pytest.raises(KeyError, match="not found"):
        service.delete_document("missing_doc")


def test_memory_service_clear(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")

    service.add_document(document_id="doc1", text="first text", metadata={"num": 1})
    service.add_document(document_id="doc2", text="second text", metadata={"num": 2})

    # Clear collection
    service.clear()

    # Search should find nothing
    res = service.search("text", top_k=5)
    assert len(res) == 0


def test_memory_service_empty_queries(temp_db_dir):
    service = MemoryService(db_path=temp_db_dir, collection_name="test_collection")
    service.add_document(document_id="doc1", text="first text", metadata={"num": 1})

    assert service.search("") == []
    assert service.search("   ") == []
    assert service.search(None) == []


def test_memory_service_init_failure():
    # Filepath as db_path directory triggers initialization or path creation failure.
    with tempfile.NamedTemporaryFile() as tmp_file:
        with pytest.raises(MemoryServiceInitError):
            MemoryService(db_path=tmp_file.name)
