import re
from typing import Any, Dict

from backend.core.logger import logger


class ReviewerAgent:
    def __init__(self, ai_service_instance=None):
        # Kept for interface compatibility but no longer used
        pass

    def review_report(self, report_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews the generated markdown report deterministically using rules.
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
            "ReviewerAgent starting deterministic rule-based review for report "
            f"title='{title}' under topic='{topic}'"
        )

        # 1. Parse headings from the markdown
        h2_headings = re.findall(r"^##\s+(.+)$", markdown, flags=re.MULTILINE)
        h2_headings = [h.strip() for h in h2_headings]

        # 2. Identify planned sections
        planned_sections = report_output.get("sections")
        if not planned_sections and "plan" in report_output:
            plan = report_output.get("plan")
            if isinstance(plan, dict):
                planned_sections = plan.get("sections")

        if planned_sections is None:
            # Fallback if no sections list is provided: assume sections present
            # in markdown are the planned ones, or default to standard sections
            # if markdown is empty of H2s.
            if h2_headings:
                planned_sections = h2_headings
            else:
                planned_sections = [
                    "Introduction",
                    "Core Concepts",
                    "Applications",
                    "Challenges",
                    "Conclusion",
                ]

        # 3. Check rule conditions
        has_title = bool(title or "# " in markdown)
        is_not_empty = bool(markdown.strip())
        report_len = len(markdown)

        # Check missing sections
        missing_sections = []
        for sec in planned_sections:
            if not any(sec.lower() == h.lower() for h in h2_headings):
                missing_sections.append(sec)
        all_planned_sections_exist = len(missing_sections) == 0

        # Check empty sections
        sections_content = re.split(r"^##\s+.+$", markdown, flags=re.MULTILINE)
        empty_sections = []
        for i, content in enumerate(sections_content[1:]):
            sec_name = h2_headings[i] if i < len(h2_headings) else f"Section {i + 1}"
            if not content.strip():
                empty_sections.append(sec_name)
        every_section_has_content = len(empty_sections) == 0

        # Check duplicate headings
        duplicate_headings = []
        seen_headings = set()
        for h in h2_headings:
            h_lower = h.lower()
            if h_lower in seen_headings:
                duplicate_headings.append(h)
            seen_headings.add(h_lower)

        # 4. Calculate score
        score = 50

        # Additions
        if has_title:
            score += 10
        if is_not_empty:
            score += 10
        if all_planned_sections_exist:
            score += 10
        if report_len > 1000:
            score += 10
        if every_section_has_content:
            score += 10

        # Deductions
        if missing_sections:
            score -= 10 * len(missing_sections)
        if empty_sections:
            score -= 10 * len(empty_sections)
        if duplicate_headings:
            score -= 10 * len(duplicate_headings)
        if report_len < 200:
            score -= 20

        # Clamp score between 0 and 100
        score = max(0, min(100, score))

        # 5. Populate review sections
        strengths = []
        if is_not_empty:
            strengths.append("Report generated successfully")
        if all_planned_sections_exist:
            strengths.append("All planned sections completed")
        if not duplicate_headings and every_section_has_content:
            strengths.append("Markdown structure is valid")
        if report_len > 1000:
            strengths.append("Provides a detailed, comprehensive overview")
        if not missing_sections and not empty_sections:
            strengths.append("Consistent content delivery across all sections")

        if not strengths:
            strengths.append("Document structure parsed successfully")

        weaknesses = []
        if missing_sections:
            weaknesses.append(
                f"Missing planned sections: {', '.join(missing_sections)}"
            )
        if empty_sections:
            weaknesses.append(
                f"Empty sections detected with no content: {', '.join(empty_sections)}"
            )
        if duplicate_headings:
            weaknesses.append(
                f"Duplicate headings found: {', '.join(duplicate_headings)}"
            )
        if report_len < 200:
            weaknesses.append("Extremely short report, lacks necessary details")
        elif report_len < 1000:
            weaknesses.append(
                "Report length is on the shorter side, could benefit from more detail"
            )
        if not has_title:
            weaknesses.append("Missing a clear document title heading")

        suggestions = []
        if missing_sections:
            suggestions.append(
                "Re-run the generation to ensure all planned sections are populated"
            )
        if empty_sections:
            suggestions.append("Add detailed paragraphs to the empty sections")
        if duplicate_headings:
            suggestions.append(
                "Rename duplicate section headings to ensure unique structure"
            )
        if report_len < 1000:
            suggestions.append(
                "Expand technical depth and add more detailed "
                "paragraphs to short sections"
            )

        # General suggestions
        suggestions.append("Add academic citations to support statements")
        suggestions.append(
            "Include diagrams or flowcharts to visualize complex workflows"
        )
        suggestions.append(
            "Add a dedicated references section at the end of the report"
        )
        suggestions.append("Expand technical depth with specific domain examples")

        logger.info(
            "ReviewerAgent successfully completed deterministic review for "
            f"title='{title}' with score={score}"
        )

        return {
            "score": score,
            "strengths": strengths,
            "issues": weaknesses,
            "suggestions": suggestions,
            "ready_for_editing": True,
        }
