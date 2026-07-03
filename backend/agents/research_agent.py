import json
import uuid
from typing import Any, Dict, List

from backend.core.logger import logger
from backend.memory.memory_service import MemoryService
from backend.search.search_service import SearchService
from backend.services.ai_service import ai_service


class ResearchAgent:
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
                f"ResearchAgent failed to initialize MemoryService: {e}. "
                "Running without memory."
            )
            self.memory_service = None

    def conduct_research(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conducts research for each section in the provided plan.
        Returns a structured research JSON dictionary.
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
            f"ResearchAgent starting research workflow for topic='{topic}' "
            f"across {len(sections)} sections."
        )

        research_results = []

        for section in sections:
            logger.info(f"ResearchAgent conducting research for section='{section}'")
            query = f"{topic} {section}"

            # Execute web search
            search_results = []
            try:
                if self.search_service:
                    logger.info(f"ResearchAgent executing search with query='{query}'")
                    search_results = self.search_service.search(
                        query=query, max_results=3
                    )
                else:
                    logger.warning(
                        "ResearchAgent has no SearchService configured. "
                        "Skipping web search."
                    )
            except Exception as e:
                logger.warning(
                    f"ResearchAgent search failed for query='{query}': {e}. "
                    "Continuing with memory and LLM."
                )

            # Execute memory search
            memory_results = []
            if self.memory_service:
                try:
                    logger.info(
                        f"ResearchAgent executing memory search with query='{query}'"
                    )
                    memory_results = self.memory_service.search(query=query, top_k=3)
                except Exception as e:
                    logger.warning(
                        f"ResearchAgent memory search failed for query='{query}': "
                        f"{e}. Continuing with search and LLM."
                    )
            else:
                logger.info(
                    "ResearchAgent has no MemoryService configured or "
                    "initialized. Skipping memory retrieval."
                )

            section_data = self._research_section(
                topic, section, search_results, memory_results
            )

            # Save section research to memory database if available
            if self.memory_service:
                try:
                    doc_id = f"research_{uuid.uuid4().hex}"
                    doc_text = (
                        f"Topic: {topic}\n"
                        f"Section: {section}\n"
                        f"Summary: {section_data.get('summary', '')}\n"
                        f"Key Points: {', '.join(section_data.get('key_points', []))}"
                    )
                    doc_meta = {
                        "topic": str(topic),
                        "section": str(section),
                        "summary": str(section_data.get("summary", "")),
                        "key_points": json.dumps(section_data.get("key_points", [])),
                        "suggested_subtopics": json.dumps(
                            section_data.get("suggested_subtopics", [])
                        ),
                        "sources": json.dumps(section_data.get("sources", [])),
                    }
                    logger.info(
                        "ResearchAgent saving research output to memory with "
                        f"doc_id='{doc_id}'"
                    )
                    self.memory_service.add_document(
                        document_id=doc_id, text=doc_text, metadata=doc_meta
                    )
                except Exception as e:
                    logger.warning(
                        "ResearchAgent failed to save research output to memory: "
                        f"{e}. Continuing."
                    )

            research_results.append(section_data)

        logger.info(
            "ResearchAgent successfully completed research workflow for "
            f"topic='{topic}'"
        )
        return {"topic": str(topic), "research": research_results}

    def _research_section(
        self,
        topic: str,
        section: str,
        search_results: List[Dict[str, str]],
        memory_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        search_context = ""
        sources_list = []
        if search_results:
            search_context_items = []
            for r in search_results:
                title = r.get("title", "")
                url = r.get("url", "")
                snippet = r.get("snippet", "")
                search_context_items.append(
                    f"Title: {title}\nURL: {url}\nSnippet: {snippet}"
                )
                if url:
                    sources_list.append({"title": title or url, "url": url})
            search_context = "\n\n".join(search_context_items)
        else:
            search_context = "No web search results available."

        memory_context = ""
        if memory_results:
            memory_context_items = []
            for r in memory_results:
                text = r.get("text", "")
                metadata = r.get("metadata", {})
                distance = r.get("distance", 0.0)

                if isinstance(metadata, dict):
                    doc_topic = metadata.get("topic", "")
                    doc_section = metadata.get("section", "")
                else:
                    doc_topic = ""
                    doc_section = ""

                memory_context_items.append(
                    f"Memory Text: {text}\n"
                    f"Metadata: Topic='{doc_topic}', Section='{doc_section}'\n"
                    f"Distance: {distance}"
                )
            memory_context = "\n\n".join(memory_context_items)
        else:
            memory_context = "No memory results available."

        prompt = (
            "You are a professional research agent. Your task is to conduct deep "
            "research and output a structured research document as a JSON object.\n"
            "You must output ONLY a valid JSON object. Do not include any "
            "explanation, conversational text, or markdown formatting "
            "(like ```json).\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            f'  "section": "{section}",\n'
            '  "summary": "Detailed, informative synthesis of the topic '
            'findings for this section...",\n'
            '  "key_points": ["First important factual insight", "Second key '
            'finding/data point", "Third core takeaway"],\n'
            '  "suggested_subtopics": ["Subtopic for further exploration 1", '
            '"Subtopic for further exploration 2"]\n'
            "}\n\n"
            f"Topic: {topic}\n\n"
            f"Section: {section}\n\n"
            "Web Search Results:\n"
            "=======\n"
            f"{search_context}\n"
            "=======\n\n"
            "Memory Results:\n"
            "=======\n"
            f"{memory_context}\n"
            "=======\n\n"
            "Synthesize the research section now by combining both web search "
            "results and memory results (prioritizing factual synthesis) to "
            "create the final structured research."
        )

        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    "ResearchAgent calling AIService for section="
                    f"'{section}' (attempt {attempt}/{max_attempts})"
                )
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()

                cleaned_text = self._clean_json_response(raw_text)
                section_json = json.loads(cleaned_text)

                validated_section = self._validate_and_sanitize_section_research(
                    section_json, section, sources_list
                )
                logger.info(
                    "ResearchAgent successfully generated and validated research "
                    f"for section='{section}'"
                )
                return validated_section

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"ResearchAgent failed to parse/validate JSON on attempt "
                    f"{attempt} for section='{section}': {e}. Raw response: {raw_text}"
                )
                if attempt == max_attempts:
                    logger.error(
                        "ResearchAgent failed to generate valid research for "
                        f"section='{section}' after {max_attempts} attempts."
                    )
                    raise ValueError(
                        f"Failed to generate valid research JSON for section "
                        f"'{section}': {e}"
                    ) from e

        raise ValueError(f"Failed to research section '{section}'")

    def _clean_json_response(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline:]
            else:
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()

    def _validate_and_sanitize_section_research(
        self, data: Any, expected_section: str, sources_list: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")

        section = data.get("section") or expected_section

        summary = data.get("summary")
        if not summary or not isinstance(summary, str):
            raise ValueError("Key 'summary' is missing or not a string")

        key_points = data.get("key_points")
        if not isinstance(key_points, list):
            raise ValueError("Key 'key_points' must be a list")
        key_points = [str(kp) for kp in key_points]

        suggested_subtopics = data.get("suggested_subtopics")
        if not isinstance(suggested_subtopics, list):
            raise ValueError("Key 'suggested_subtopics' must be a list")
        suggested_subtopics = [str(st) for st in suggested_subtopics]

        sources = data.get("sources")
        if sources is None:
            sources = sources_list
        else:
            if not isinstance(sources, list):
                raise ValueError("Key 'sources' must be a list")
            cleaned_sources = []
            for src in sources:
                if isinstance(src, dict):
                    cleaned_sources.append(
                        {
                            "title": str(src.get("title", "")),
                            "url": str(src.get("url", "")),
                        }
                    )
            sources = cleaned_sources

        return {
            "section": str(section),
            "summary": str(summary),
            "key_points": key_points,
            "suggested_subtopics": suggested_subtopics,
            "sources": sources,
        }
