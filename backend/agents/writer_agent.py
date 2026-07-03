import json
from typing import Any, Dict

from backend.core.logger import logger
from backend.services.ai_service import ai_service


class WriterAgent:
    def __init__(self, ai_service_instance=None):
        self.ai_service = ai_service_instance or ai_service

    def write_report(self, research_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a markdown report based on the structured research output.
        Returns a dictionary with topic, title, and markdown text.
        """
        if not isinstance(research_output, dict):
            raise ValueError("Input research_output must be a dictionary")

        topic = research_output.get("topic")
        if not topic:
            raise ValueError("Input research_output is missing 'topic'")

        research_data = research_output.get("research")
        if not isinstance(research_data, list) or not research_data:
            raise ValueError(
                "Input research_output must contain a non-empty list of 'research'"
            )

        logger.info(
            "WriterAgent starting report draft generation for "
            f"topic='{topic}' across {len(research_data)} sections."
        )

        prompt = (
            "You are a professional technical writer and editor. Your task is "
            "to write a comprehensive, publication-ready research report in "
            "Markdown based on the provided research summaries.\n"
            "You must output ONLY a valid JSON object. Do not include any "
            "explanation, conversational text, or markdown formatting "
            "(like ```json).\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            '  "title": "A compelling, academic-grade title for the report",\n'
            '  "markdown": "The complete report content in Markdown format, '
            'following all instructions below."\n'
            "}\n\n"
            "Markdown instructions:\n"
            "- Start directly with the title as an H1 heading (e.g. # Title)\n"
            "- Include an Introduction section (H2: ## Introduction)\n"
            "- For each researched section, include an appropriate H2 heading "
            "(e.g. ## Section Name)\n"
            "- Develop deep paragraphs using the provided summaries and key points\n"
            "- Use bullet lists where appropriate to highlight data/insights\n"
            "- End with a comprehensive Conclusion section (H2: ## Conclusion)\n\n"
            "Make sure that all double-quotes, newlines, and backslashes inside "
            "the 'markdown' field are correctly escaped as required for a JSON "
            "string value.\n\n"
            f"Topic: {topic}\n"
            f"Research Data:\n{json.dumps(research_data, indent=2)}\n"
        )

        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    f"WriterAgent calling AIService (attempt {attempt}/{max_attempts})"
                )
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()

                cleaned_text = self._clean_json_response(raw_text)
                report_json = json.loads(cleaned_text)

                validated_report = self._validate_and_sanitize_report(
                    report_json, topic
                )
                logger.info(
                    "WriterAgent successfully generated and validated markdown "
                    f"report for topic='{topic}'"
                )
                return validated_report

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"WriterAgent failed to parse/validate JSON on attempt "
                    f"{attempt}: {e}. Raw response: {raw_text}"
                )
                if attempt == max_attempts:
                    logger.error(
                        "WriterAgent failed to generate a valid report after "
                        f"{max_attempts} attempts."
                    )
                    raise ValueError(
                        f"Failed to generate a valid report JSON: {e}"
                    ) from e

        raise ValueError("Failed to generate report.")

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

    def _validate_and_sanitize_report(
        self, data: Any, expected_topic: str
    ) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")

        title = data.get("title")
        if not title or not isinstance(title, str):
            title = f"Research Report: {expected_topic}"

        markdown = data.get("markdown")
        if not markdown or not isinstance(markdown, str):
            raise ValueError("Key 'markdown' is missing or not a string")

        return {
            "topic": str(expected_topic),
            "title": str(title),
            "markdown": str(markdown),
        }
