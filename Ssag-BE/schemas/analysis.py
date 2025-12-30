from datetime import datetime
from typing import Dict, Optional

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

class AnalysisDetailResponse(BaseModel):
    id: int
    image_name: str
    location: Optional[str]
    trash_summary: Dict[str, int]
    required_people: int
    estimated_time_min: int
    tool: Dict[str, int]
    created_at: datetime

    class Config:
        from_attributes = True