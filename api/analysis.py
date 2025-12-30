from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from crud.analysis import create_analysis_result
from db.database import get_db
from schemas.analysis import AnalysisImageResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

UPLOAD_DIR = Path("uploads")


@router.post("/image", response_model=AnalysisImageResponse)
async def upload_analysis_image(
    image: UploadFile = File(...),
    location: Optional[str] = Form(default=None, max_length=255),
    db: Session = Depends(get_db),
):
    created_at = datetime.now(timezone.utc)
    upload_dir = UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = image.filename or "upload"
    extension = Path(original_name).suffix
    stored_name = f"{uuid4().hex}{extension}"
    stored_path = upload_dir / stored_name

    with stored_path.open("wb") as buffer:
        while chunk := await image.read(1024 * 1024):
            buffer.write(chunk)

    trash_summary = {"plastic": 14, "can": 6, "net": 1}
    recommended_resources = {
        "people": 5,
        "tools": {
            "tongs": 5,
            "bags": 8,
            "gloves": 5,
            "cutter": 1,
        },
        "estimated_time_min": 80,
    }

    analysis_result = create_analysis_result(
        db,
        image_name=original_name,
        image_path=f"/uploads/{stored_name}",
        location=location,
        area_type=None,
        trash_summary=trash_summary,
        required_people=recommended_resources["people"],
        estimated_time_min=recommended_resources["estimated_time_min"],
        tool=recommended_resources["tools"],
        created_at=created_at,
    )

    return {
        "analysis_id": analysis_result.id,
        "image_name": original_name,
        "trash_summary": trash_summary,
        "recommended_resources": recommended_resources,
        "created_at": created_at,
    }
