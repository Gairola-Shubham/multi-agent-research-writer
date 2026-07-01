import pytest
from unittest.mock import patch, MagicMock
from backend.search.search_service import (
    SearchService,
    SearchError,
    SearchTimeoutError,
    SearchConnectionError
)

def test_search_service_import():
    """Verify SearchService can be imported."""
    service = SearchService()
    assert service is not None

@patch("backend.search.search_service.DDGS")
def test_search_success(mock_ddgs):
    """Verify search returns formatted results successfully."""
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.return_value = [
        {"title": "Quantum Computing Intro", "href": "http://quantum.com", "body": "A guide to qubits."}
    ]

    service = SearchService()
    results = service.search("Quantum Computing", max_results=1)

    assert len(results) == 1
    assert results[0]["title"] == "Quantum Computing Intro"
    assert results[0]["url"] == "http://quantum.com"
    assert results[0]["snippet"] == "A guide to qubits."
    mock_instance.text.assert_called_once_with("Quantum Computing", max_results=1)

def test_search_empty_query():
    """Verify search returns empty list for empty/whitespace queries."""
    service = SearchService()
    assert service.search("") == []
    assert service.search("   ") == []

@patch("backend.search.search_service.DDGS")
def test_search_empty_results(mock_ddgs):
    """Verify search returns empty list when no results are found."""
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.return_value = []

    service = SearchService()
    results = service.search("noresultsquery")
    assert results == []

@patch("backend.search.search_service.DDGS")
def test_search_timeout_handling(mock_ddgs):
    """Verify search raises SearchTimeoutError on timeout."""
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.side_effect = Exception("Timeout error occurred")

    service = SearchService()
    with pytest.raises(SearchTimeoutError, match="Search timed out"):
        service.search("Quantum")

@patch("backend.search.search_service.DDGS")
def test_search_connection_handling(mock_ddgs):
    """Verify search raises SearchConnectionError on connection issues."""
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.side_effect = Exception("HTTPConnectionPool failed or Request error")

    service = SearchService()
    with pytest.raises(SearchConnectionError, match="Search connection failed"):
        service.search("Quantum")

@patch("backend.search.search_service.DDGS")
def test_search_generic_exception_handling(mock_ddgs):
    """Verify search raises generic SearchError on unexpected errors."""
    mock_instance = MagicMock()
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    mock_instance.text.side_effect = Exception("Unknown internal error")

    service = SearchService()
    with pytest.raises(SearchError, match="Search failed"):
        service.search("Quantum")
