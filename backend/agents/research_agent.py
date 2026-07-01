import json
from typing import Dict, Any, List, Optional
from backend.services.ai_service import ai_service
from backend.core.logger import logger

class ResearchAgent:
    def __init__(self, ai_service_instance=None):
        self.ai_service = ai_service_instance or ai_service

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

        logger.info(f"ResearchAgent starting research workflow for topic='{topic}' across {len(sections)} sections.")
        
        research_results = []
        
        for section in sections:
            logger.info(f"ResearchAgent conducting research for section='{section}'")
            section_data = self._research_section(topic, section)
            research_results.append(section_data)
            
        logger.info(f"ResearchAgent successfully completed research workflow for topic='{topic}'")
        return {
            "topic": str(topic),
            "research": research_results
        }

    def _research_section(self, topic: str, section: str) -> Dict[str, Any]:
        prompt = (
            "You are a professional research agent. Your task is to conduct deep research and output a structured research document as a JSON object.\n"
            "You must output ONLY a valid JSON object. Do not include any explanation, conversational text, or markdown formatting (like ```json).\n\n"
            "The JSON object must strictly match this structure:\n"
            "{\n"
            f'  "section": "{section}",\n'
            '  "summary": "Detailed, informative synthesis of the topic findings for this section...",\n'
            '  "key_points": ["First important factual insight", "Second key finding/data point", "Third core takeaway"],\n'
            '  "suggested_subtopics": ["Subtopic for further exploration 1", "Subtopic for further exploration 2"]\n'
            "}\n\n"
            f"Topic: {topic}\n"
            f"Section: {section}\n"
        )
        
        max_attempts = 3
        raw_text = ""
        for attempt in range(1, max_attempts + 1):
            try:
                logger.debug(f"ResearchAgent calling AIService for section='{section}' (attempt {attempt}/{max_attempts})")
                response_data = self.ai_service.generate_response(prompt=prompt)
                raw_text = response_data.get("response", "").strip()
                
                cleaned_text = self._clean_json_response(raw_text)
                section_json = json.loads(cleaned_text)
                
                validated_section = self._validate_and_sanitize_section_research(section_json, section)
                logger.info(f"ResearchAgent successfully generated and validated research for section='{section}'")
                return validated_section
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"ResearchAgent failed to parse/validate JSON on attempt {attempt} for section='{section}': {e}. Raw response: {raw_text}")
                if attempt == max_attempts:
                    logger.error(f"ResearchAgent failed to generate valid research for section='{section}' after {max_attempts} attempts.")
                    raise ValueError(f"Failed to generate valid research JSON for section '{section}': {e}") from e
                    
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

    def _validate_and_sanitize_section_research(self, data: Any, expected_section: str) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")
            
        # If section is missing or empty, use expected_section
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
        
        return {
            "section": str(section),
            "summary": str(summary),
            "key_points": key_points,
            "suggested_subtopics": suggested_subtopics
        }
