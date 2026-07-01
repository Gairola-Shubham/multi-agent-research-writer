import logging
from typing import Dict, Any, List
from duckduckgo_search import DDGS
from backend.core.logger import logger
from backend.core.config import settings

class SearchError(Exception):
    """Base exception for search service errors."""
    pass

class SearchTimeoutError(SearchError):
    """Raised when the search operation times out."""
    pass

class SearchConnectionError(SearchError):
    """Raised when the search service experiences network failures."""
    pass

class SearchService:
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Performs a web search using DuckDuckGo.
        Returns a standardized list of search results.
        """
        if not query or not query.strip():
            logger.warning("SearchService received an empty query.")
            return []

        query = query.strip()
        max_results = max_results or settings.MAX_SEARCH_RESULTS

        logger.info(f"SearchService starting search for query='{query}' with max_results={max_results}")

        try:
            results = []
            with DDGS() as ddgs:
                # ddgs.text returns an iterator of dicts containing: title, href, body
                ddgs_generator = ddgs.text(query, max_results=max_results)
                if ddgs_generator:
                    for r in ddgs_generator:
                        results.append({
                            "title": str(r.get("title", "")),
                            "url": str(r.get("href", "")),
                            "snippet": str(r.get("body", ""))
                        })
            
            logger.info(f"SearchService completed search for query='{query}'. Found {len(results)} results.")
            return results

        except Exception as e:
            err_msg = str(e).lower()
            if "timeout" in err_msg or "time out" in err_msg:
                logger.error(f"SearchService timeout error searching for query='{query}': {e}")
                raise SearchTimeoutError(f"Search timed out: {e}") from e
            elif "connection" in err_msg or "http" in err_msg or "urllib" in err_msg or "request" in err_msg or "unreachable" in err_msg:
                logger.error(f"SearchService connection error searching for query='{query}': {e}")
                raise SearchConnectionError(f"Search connection failed: {e}") from e
            else:
                logger.error(f"SearchService unexpected error searching for query='{query}': {e}")
                raise SearchError(f"Search failed: {e}") from e
