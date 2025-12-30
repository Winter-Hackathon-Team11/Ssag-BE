from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field

class RecommendedResources(BaseModel):
    people: int = Field(..., ge=0)
    tools: Dict[str, int] = Field(...)
    estimated_time_min: int = Field(..., ge=0)


class AnalysisImageResponse(BaseModel):
    analysis_id: int = Field(..., ge=1)
    image_name: str = Field(..., max_length=255)
    trash_summary: Dict[str, int] = Field(...)
    recommended_resources: RecommendedResources
    created_at: datetime
