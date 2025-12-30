from datetime import datetime

from sqlalchemy.orm import Session

from models.analysis import AnalysisResult


def create_analysis_result(
    db: Session,
    *,
    image_name: str,
    image_path: str,
    location: str | None,
    area_type: str | None,
    trash_summary: dict,
    required_people: int,
    estimated_time_min: int,
    tool: dict,
    created_at: datetime,
) -> AnalysisResult:
    analysis_result = AnalysisResult(
        image_name=image_name,
        image_path=image_path,
        location=location,
        area_type=area_type,
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
