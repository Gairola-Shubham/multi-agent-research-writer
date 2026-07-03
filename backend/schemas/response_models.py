from typing import List

from pydantic import BaseModel, Field


class ReviewBlock(BaseModel):
    score: int = Field(..., description="The score evaluated by the reviewer.")
    strengths: List[str] = Field(
        ..., description="The positive aspects of the article."
    )
    issues: List[str] = Field(..., description="Problems identified in the article.")
    suggestions: List[str] = Field(
        ..., description="Improvements suggested for editing."
    )
    ready_for_editing: bool = Field(
        ..., description="Whether the report is ready for final editing."
    )


class ResearchResponse(BaseModel):
    topic: str = Field(..., description="The research topic.")
    title: str = Field(..., description="The compiled article title.")
    final_markdown: str = Field(
        ..., description="The refined and edited article Markdown."
    )
    review: ReviewBlock = Field(..., description="Peer review feedback report.")
    changes_applied: List[str] = Field(
        ..., description="The changes applied by the Editor."
    )
