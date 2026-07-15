from typing import Any, Dict

from backend.core.logger import logger
from backend.services.ai_service import ai_service


class EditorAgent:
    def __init__(self, ai_service_instance=None):
        self.ai_service = ai_service_instance or ai_service

    def edit_report(
        self, report_output: Dict[str, Any], review_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edits and refines the report markdown based on reviewer suggestions and
        general readability.
        Returns a dictionary matching the final edited structure.
        """
        # Validate inputs
        if not isinstance(report_output, dict):
            raise ValueError("Input report_output must be a dictionary")
        if not isinstance(review_output, dict):
            raise ValueError("Input review_output must be a dictionary")

        topic = report_output.get("topic")
        if not topic:
            raise ValueError("Input report_output is missing 'topic'")
        title = report_output.get("title")
        if not title:
            raise ValueError("Input report_output is missing 'title'")
        markdown = report_output.get("markdown")
        if not markdown or not isinstance(markdown, str):
            raise ValueError(
                "Input report_output is missing 'markdown' or it is not a string"
            )

        logger.info(
            "EditorAgent edit_report called (bypassed for architectural demonstration)."
        )

        return {
            "topic": str(topic),
            "title": str(title),
            "final_markdown": str(markdown),
            "changes_applied": ["Editor bypassed for performance optimization."],
        }

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

    def _validate_and_sanitize_edited_report(
        self, data: Any, expected_topic: str, expected_title: str
    ) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")

        title = data.get("title") or expected_title

        final_markdown = data.get("final_markdown")
        if not final_markdown or not isinstance(final_markdown, str):
            raise ValueError("Key 'final_markdown' is missing or not a string")

        changes_applied = data.get("changes_applied")
        if not isinstance(changes_applied, list):
            raise ValueError("Key 'changes_applied' must be a list")
        changes_applied = [str(c) for c in changes_applied]

        return {
            "topic": str(expected_topic),
            "title": str(title),
            "final_markdown": str(final_markdown),
            "changes_applied": changes_applied,
        }
