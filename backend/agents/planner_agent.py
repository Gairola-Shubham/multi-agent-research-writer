import json
from typing import Any, Dict

from backend.core.logger import logger
from backend.services.ai_service import ai_service


class PlannerAgent:
    def __init__(self, ai_service_instance=None):
        self.ai_service = ai_service_instance or ai_service

    def create_plan(self, topic: str, style: str, depth: str) -> Dict[str, Any]:
        """
        Creates a structured research plan for a given topic, style, and depth.
        Returns a validated dictionary matching the requested schema.
        """
        logger.info(
            "PlannerAgent creating research plan for "
            f"topic='{topic}', style='{style}', depth='{depth}'"
        )

        prompt = (
            "You are a research planning assistant. Your task is to output a "
            "structured research plan as a JSON object.\n"
            "You must output ONLY a valid JSON object. Do not include any "
            "explanation, conversational text, or markdown formatting "
            "(like ```json).\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            '  "topic": "The exact topic of research",\n'
            '  "difficulty": "Estimated difficulty level (e.g., Easy, Medium, '
            'Hard)",\n'
            '  "estimated_sources": 5,\n'
            '  "sections": ["Introduction", "Core Concepts", "Applications", '
            '"Challenges", "Conclusion"],\n'
            '  "execution_order": ["Introduction", "Core Concepts", '
            '"Applications", "Challenges", "Conclusion"]\n'
            "}\n\n"
            f"Topic: {topic}\n"
            f"Style: {style}\n"
            f"Depth: {depth}\n"
        )

        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(
                    f"PlannerAgent calling AIService (attempt {attempt}/{max_attempts})"
                )
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()

                cleaned_text = self._clean_json_response(raw_text)
                plan = json.loads(cleaned_text)

                # Validate schema
                validated_plan = self._validate_and_sanitize_plan(plan, topic)
                logger.info(
                    "PlannerAgent successfully created and validated plan "
                    f"for topic='{topic}'"
                )
                return validated_plan

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"PlannerAgent failed to parse/validate JSON on attempt "
                    f"{attempt}: {e}. Raw response: {raw_text}"
                )
                if attempt == max_attempts:
                    logger.error(
                        "PlannerAgent failed to generate a valid plan after "
                        f"{max_attempts} attempts."
                    )
                    raise ValueError(
                        f"Failed to generate a valid research plan JSON: {e}"
                    ) from e

        raise ValueError("Failed to generate research plan.")

    def _clean_json_response(self, text: str) -> str:
        text = text.strip()
        # Remove markdown code block delimiters if present
        if text.startswith("```"):
            # find first newline
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline:]
            else:
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()

    def _validate_and_sanitize_plan(
        self, data: Any, expected_topic: str
    ) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object (dictionary)")

        required_keys = [
            "topic",
            "difficulty",
            "estimated_sources",
            "sections",
            "execution_order",
        ]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key '{key}' in plan JSON")

        # Basic validation of types
        topic = data.get("topic") or expected_topic
        difficulty = data.get("difficulty") or "Medium"

        try:
            estimated_sources = int(data.get("estimated_sources", 5))
        except (TypeError, ValueError):
            estimated_sources = 5

        sections = data.get("sections")
        if not isinstance(sections, list):
            raise ValueError("Key 'sections' must be a list")
        sections = [str(s) for s in sections]

        execution_order = data.get("execution_order")
        if not isinstance(execution_order, list):
            raise ValueError("Key 'execution_order' must be a list")
        execution_order = [str(e) for e in execution_order]

        return {
            "topic": str(topic),
            "difficulty": str(difficulty),
            "estimated_sources": estimated_sources,
            "sections": sections,
            "execution_order": execution_order,
        }
