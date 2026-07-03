import json
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
            "EditorAgent starting refinement process for report "
            f"title='{title}' under topic='{topic}'"
        )

        prompt = (
            "You are a professional editor. Your task is to edit, refine, and "
            "polish the provided Markdown report based on peer review feedback, "
            "and output a structured response as a JSON object.\n"
            "You must output ONLY a valid JSON object. Do not include any "
            "explanation, conversational text, or markdown formatting "
            "(like ```json).\n\n"
            "Editing goals:\n"
            "- Fix spelling, typos, and grammar errors.\n"
            "- Improve readability and overall flow/transitions between sections.\n"
            "- Remove unnecessary redundancy and repetition.\n"
            "- Directly address issues and suggestions highlighted by the reviewer.\n"
            "- Strict constraint: Preserve all factual details; do not invent new "
            "facts.\n"
            "- Strict constraint: Retain standard Markdown formatting tags.\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            f'  "title": "{title}",\n'
            '  "final_markdown": "The refined and improved Markdown report '
            'content...",\n'
            '  "changes_applied": ["First improvement/change description", '
            '"Second improvement/change description"]\n'
            "}\n\n"
            "Make sure that all double-quotes, newlines, and backslashes inside "
            "the JSON fields are correctly escaped.\n\n"
            f"Topic: {topic}\n"
            f"Review Feedback:\n{json.dumps(review_output, indent=2)}\n"
            f"Original Markdown Content:\n{markdown}\n"
        )

        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    f"EditorAgent calling AIService (attempt {attempt}/{max_attempts})"
                )
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()

                cleaned_text = self._clean_json_response(raw_text)
                edited_json = json.loads(cleaned_text)

                validated_report = self._validate_and_sanitize_edited_report(
                    edited_json, topic, title
                )
                logger.info(
                    "EditorAgent successfully refined and validated report "
                    f"for topic='{topic}'"
                )
                return validated_report

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"EditorAgent failed to parse/validate JSON on attempt "
                    f"{attempt}: {e}. Raw response: {raw_text}"
                )
                if attempt == max_attempts:
                    logger.error(
                        "EditorAgent failed to generate a valid edited report "
                        f"after {max_attempts} attempts."
                    )
                    raise ValueError(
                        f"Failed to generate a valid editor JSON: {e}"
                    ) from e

        raise ValueError("Failed to refine report.")

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
