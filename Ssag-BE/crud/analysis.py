from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from models.analysis import AnalysisResult


def create_analysis_result(
    db: Session,
    *,
    image_name: str,
    original_image: str,
    location: Optional[str],
    trash_summary: dict,
    required_people: int,
    estimated_time_min: int,
    tool: dict,
    created_at: datetime,
) -> AnalysisResult:
    analysis_result = AnalysisResult(
        image_name=image_name,
        original_image=original_image,
        location=location,
        trash_summary=trash_summary,
        required_people=required_people,
        estimated_time_min=estimated_time_min,
        tool=tool,
        created_at=created_at,
    )
    db.add(analysis_result)
    db.commit()
    db.refresh(analysis_result)
    return analysis_result
