import json
from typing import Any, Dict

from backend.core.logger import logger
from backend.services.ai_service import ai_service


class ReviewerAgent:
    def __init__(self, ai_service_instance=None):
        self.ai_service = ai_service_instance or ai_service

    def review_report(self, report_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews the generated markdown report.
        Returns a dictionary with review score, strengths, issues,
        suggestions, and ready_for_editing flag.
        """
        if not isinstance(report_output, dict):
            raise ValueError("Input report_output must be a dictionary")

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
            "ReviewerAgent starting review process for report "
            f"title='{title}' under topic='{topic}'"
        )

        prompt = (
            "You are a professional peer reviewer and academic editor. "
            "Your task is to review the following report and output a "
            "structured review document as a JSON object.\n"
            "You must output ONLY a valid JSON object. Do not include "
            "any explanation, conversational text, or markdown "
            "formatting (like ```json).\n\n"
            "Evaluate the report based on:\n"
            "- Factual consistency\n"
            "- Completeness\n"
            "- Logical flow\n"
            "- Grammar and spelling\n"
            "- Readability\n"
            "- Missing sections/details\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            '  "score": 85,\n'
            '  "strengths": ["Clear introduction", "Structured arguments"],\n'
            '  "issues": ["Grammar typo in section 2", '
            '"Missing core concepts in section 3"],\n'
            '  "suggestions": ["Elaborate more on qubits in section 2", '
            '"Fix typo in paragraph 4"],\n'
            '  "ready_for_editing": true\n'
            "}\n\n"
            f"Topic: {topic}\n"
            f"Title: {title}\n"
            f"Report content:\n{markdown}\n"
        )

        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    "ReviewerAgent calling AIService "
                    f"(attempt {attempt}/{max_attempts})"
                )
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()

                cleaned_text = self._clean_json_response(raw_text)
                review_json = json.loads(cleaned_text)

                validated_review = self._validate_and_sanitize_review(review_json)
                logger.info(
                    "ReviewerAgent successfully generated and validated review "
                    f"for title='{title}' with score={validated_review['score']}"
                )
                return validated_review

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"ReviewerAgent failed to parse/validate JSON on attempt "
                    f"{attempt}: {e}. Raw response: {raw_text}"
                )
                if attempt == max_attempts:
                    logger.error(
                        "ReviewerAgent failed to generate a valid review "
                        f"after {max_attempts} attempts."
                    )
                    raise ValueError(
                        f"Failed to generate a valid review JSON: {e}"
                    ) from e

        raise ValueError("Failed to generate review.")

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

    def _validate_and_sanitize_review(self, data: Any) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")

        required_keys = [
            "score",
            "strengths",
            "issues",
            "suggestions",
            "ready_for_editing",
        ]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key '{key}' in review JSON")

        try:
            score = int(data.get("score"))
        except (TypeError, ValueError) as e:
            raise ValueError("Key 'score' must be a valid integer") from e

        if score < 0 or score > 100:
            raise ValueError("Key 'score' must be between 0 and 100")

        strengths = data.get("strengths")
        if not isinstance(strengths, list):
            raise ValueError("Key 'strengths' must be a list")
        strengths = [str(s) for s in strengths]

        issues = data.get("issues")
        if not isinstance(issues, list):
            raise ValueError("Key 'issues' must be a list")
        issues = [str(i) for i in issues]

        suggestions = data.get("suggestions")
        if not isinstance(suggestions, list):
            raise ValueError("Key 'suggestions' must be a list")
        suggestions = [str(s) for s in suggestions]

        ready_for_editing = bool(data.get("ready_for_editing"))

        return {
            "score": score,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "ready_for_editing": ready_for_editing,
        }
