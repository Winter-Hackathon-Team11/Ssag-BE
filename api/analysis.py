from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from crud.analysis import create_analysis_result
from db.database import get_db
from schemas.analysis import AnalysisImageResponse
from services.gemini import analyze_trash_image_resources
from utils.yolo import (
    run_yolo,
    summarize_detections,
    save_annotated_image,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

UPLOAD_DIR = Path("uploads")


@router.post("/image", response_model=AnalysisImageResponse)
async def upload_analysis_image(
    image: UploadFile = File(...),
    location: Optional[str] = Form(default=None, max_length=255),
    db: Session = Depends(get_db),
):
    created_at = datetime.now(timezone.utc)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    original_name = image.filename or "upload"
    extension = Path(original_name).suffix
    stored_name = f"{uuid4().hex}{extension}"
    stored_path = UPLOAD_DIR / stored_name

    with stored_path.open("wb") as buffer:
        while chunk := await image.read(1024 * 1024):
            buffer.write(chunk)

    # ===== YOLO 박스 이미지 저장 =====
    annotated_name = f"annotated_{stored_name}"
    annotated_path = UPLOAD_DIR / annotated_name
    save_annotated_image(str(stored_path), str(annotated_path))

    # ===== YOLO inference (class_name 기준) =====
    detections = run_yolo(str(stored_path))
    trash_summary = summarize_detections(detections)
    print(trash_summary)

    recommended_resources = analyze_trash_image_resources(f"uploads/{stored_name}", trash_summary)

    analysis_result = create_analysis_result(
        db,
        image_name=annotated_name,
        original_image=stored_name,
        location=location,
        trash_summary=trash_summary,
        required_people=recommended_resources["people"],
        estimated_time_min=recommended_resources["estimated_time_min"],
        tool=recommended_resources["tools"],
        created_at=created_at,
    )

    return {
        "analysis_id": analysis_result.id,
        "image_name": annotated_name,
        "trash_summary": trash_summary,
        "recommended_resources": recommended_resources,
        "created_at": created_at,
    }