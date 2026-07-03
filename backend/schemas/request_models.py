from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="The main topic of research.")
    style: str = Field(
        ..., description="The writing style (e.g., Technical, Academic, Creative)."
    )
    depth: str = Field(
        ..., description="The depth of research (e.g., Brief, Standard, Detailed)."
    )
