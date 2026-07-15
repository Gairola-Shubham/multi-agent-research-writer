import uuid
from typing import Any, Dict

from backend.core.logger import logger
from backend.memory.memory_service import MemoryService
from backend.search.search_service import SearchService
from backend.services.ai_service import ai_service


class ResearchWriterAgent:
    def __init__(
        self,
        ai_service_instance: Any = None,
        search_service_instance: Any = None,
        memory_service_instance: Any = None,
    ):
        self.ai_service = ai_service_instance or ai_service
        self.search_service = search_service_instance or SearchService()
        try:
            self.memory_service = memory_service_instance or MemoryService()
        except Exception as e:
            logger.error(
                f"ResearchWriterAgent failed to initialize MemoryService: {e}. "
                "Running without memory."
            )
            self.memory_service = None

    def write_report(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conducts research and writes the report section-by-section.
        """
        if not isinstance(plan, dict):
            raise ValueError("Input plan must be a dictionary")

        topic = plan.get("topic")
        if not topic:
            raise ValueError("Input plan is missing 'topic'")

        sections = plan.get("sections")
        if not isinstance(sections, list) or not sections:
            raise ValueError("Input plan must contain a non-empty list of 'sections'")

        logger.info(
            f"ResearchWriterAgent starting research and writing for topic='{topic}' "
            f"across {len(sections)} sections."
        )

        section_contents = []

        for section in sections:
            logger.info(f"Researching & Writing {section}...")

            query = f"{topic} {section}"

            # 1. Search Web
            search_results = []
            try:
                if self.search_service:
                    search_results = self.search_service.search(
                        query=query, max_results=3
                    )
            except Exception as e:
                logger.warning(f"Search failed for section '{section}': {e}")

            # 2. Search Memory
            memory_results = []
            if self.memory_service:
                try:
                    memory_results = self.memory_service.search(query=query, top_k=3)
                except Exception as e:
                    logger.warning(f"Memory search failed for section '{section}': {e}")

            # Format Contexts
            search_context = ""
            if search_results:
                search_context = "\n\n".join(
                    [
                        f"Title: {r.get('title')}\n"
                        f"URL: {r.get('url')}\n"
                        f"Snippet: {r.get('snippet')}"
                        for r in search_results
                    ]
                )
            else:
                search_context = "No web search results available."

            memory_context = ""
            if memory_results:
                memory_context = "\n\n".join(
                    [
                        f"Memory Text: {r.get('text')}\nDistance: {r.get('distance')}"
                        for r in memory_results
                    ]
                )
            else:
                memory_context = "No memory results available."

            # 3. Produce markdown for this section
            prompt = (
                f"Topic:\n{topic}\n\n"
                f"Section:\n{section}\n\n"
                f"Web Search Results:\n{search_context}\n\n"
                f"Memory Results:\n{memory_context}\n\n"
                f"Write a 150-250 word markdown section.\n\n"
                f"Start with:\n## {section}\n\n"
                f"Return ONLY markdown."
            )

            response_data = self.ai_service.generate_response(prompt=prompt)
            section_markdown = response_data.get("response", "").strip()

            # 4. Save section content to memory
            if self.memory_service:
                try:
                    doc_id = f"section_{uuid.uuid4().hex}"
                    doc_text = f"Section: {section}\nContent: {section_markdown}"
                    doc_meta = {
                        "topic": str(topic),
                        "section": str(section),
                    }
                    self.memory_service.add_document(
                        document_id=doc_id, text=doc_text, metadata=doc_meta
                    )
                except Exception as e:
                    logger.warning(f"Failed to save section '{section}' to memory: {e}")

            section_contents.append(section_markdown)

        # Combine all sections into a single markdown report
        compiled_markdown = "\n\n".join(section_contents)

        # Generate a Title heading for the final markdown if not present
        title = f"Research Report: {topic}"
        if not compiled_markdown.startswith("# "):
            compiled_markdown = f"# {title}\n\n{compiled_markdown}"

        logger.info(
            f"ResearchWriterAgent successfully completed report for topic='{topic}'"
        )
        return {
            "topic": topic,
            "title": title,
            "markdown": compiled_markdown,
        }
