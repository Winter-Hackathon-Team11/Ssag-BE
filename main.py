import logging
from datetime import datetime, timezone
from pathlib import Path as FSPath
from typing import Generator, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Path, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from db.database import engine, SessionLocal
from models.analysis import Base, AnalysisResult

from services.gemini import analyze_trash_image, generate_recruitment_content

from schemas.recruitment import (
    RecruitmentDetailResponse,
    RecruitmentListResponse,
    RecruitmentRequest,
    RecruitmentResponse,
)

from utils.model_loader import ensure_model_exists

from api.analysis import router as analysis

ensure_model_exists()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

FSPath("uploads").mkdir(parents=True, exist_ok=True)

app = FastAPI(lifespan=lifespan)
app.include_router(analysis)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        date_str = result.created_at.strftime("%Y-%m-%d")
        return {
            "analysis_id": result.id,
            "image_url": f"/uploads/{date_str}/{result.image_name}",
            "location": result.location,
            "trash_summary": result.trash_summary or {},
            "recommended_resources": {
                "people": result.required_people,
                "tools": result.tool or {},
                "estimated_time_min": result.estimated_time_min
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/recruitment/from-analysis/{analysis_id}")
async def create_recruitment(
    analysis_id: int = Path(..., gt=0),
    request: Optional[RecruitmentRequest] = None, 
    db: Session = Depends(get_db)
):
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if not request:
            raise HTTPException(status_code=400, detail="Request body is missing")

        analysis_data_for_ai = {
            "location": analysis.location or "해당 구역",
            "trash_summary": analysis.trash_summary or {},
            "required_people": analysis.required_people or 5,
            "estimated_time_min": analysis.estimated_time_min or 60
        }
        
        generated_blog = generate_recruitment_content(analysis_data_for_ai, request.model_dump())

        location_tag = "모집"
        if request.meeting_place and request.meeting_place.strip():
            location_tag = request.meeting_place.split()[0]
        final_title = f"[{location_tag}] {generated_blog['title']}"

        analysis.generated_title = final_title
        analysis.generated_content = generated_blog['content']
        analysis.activity_date = request.activity_date
        analysis.meeting_place = request.meeting_place

        db.commit()
        db.refresh(analysis)
        
        logger.info(f"모집글 생성 및 DB 저장 성공: 분석 ID={analysis_id}")

        return {
            "image_name": analysis.image_name,
            "title": final_title,
            "content": generated_blog["content"],
            "required_people": analysis.required_people,
            "recommended_tools": analysis.tool,
            "activity_date": request.activity_date,
            "meeting_place": request.meeting_place
        }

    except Exception as e:
        logger.error(f"모집글 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recruitment/{recruitment_id}/publish")
async def publish_recruitment(
    recruitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    recruitment = db.query(AnalysisResult).filter(AnalysisResult.id == recruitment_id).first()
    if not recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    recruitment.status = "uploaded"
    recruitment.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(recruitment)

    return {"recruitment_id": recruitment.id, "status": recruitment.status}

@app.get("/recruitment", response_model=RecruitmentListResponse)
async def list_recruitments(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AnalysisResult).filter(AnalysisResult.generated_title.isnot(None))
    if status:
        query = query.filter(AnalysisResult.status == status)

    results = query.order_by(AnalysisResult.created_at.desc()).all()
    return {
        "recruitments": [
            {
                "id": item.id,
                "image_name": item.image_name,
                "title": item.generated_title or "",
                "location": item.location,
                "required_people": item.required_people,
                "estimated_time_min": item.estimated_time_min,
                "activity_date": item.activity_date or "",
                "status": item.status,
                "created_at": item.created_at,
            }
            for item in results
        ]
    }


@app.get("/recruitment/{recruitment_id}", response_model=RecruitmentDetailResponse)
async def get_recruitment_detail(
    recruitment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    recruitment = db.query(AnalysisResult).filter(AnalysisResult.id == recruitment_id).first()
    if not recruitment or not recruitment.generated_title:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    status_label = "PUBLISHED" if recruitment.status == "uploaded" else recruitment.status.upper()

    return {
        "recruitment_id": recruitment.id,
        "image_name": recruitment.image_name,
        "title": recruitment.generated_title or "",
        "content": recruitment.generated_content or "",
        "required_people": recruitment.required_people,
        "recommended_tools": recruitment.tool or {},
        "estimated_time_min": recruitment.estimated_time_min,
        "activity_date": recruitment.activity_date or "",
        "meeting_place": recruitment.meeting_place or "",
        "status": status_label,
        "created_at": recruitment.created_at,
        "published_at": recruitment.published_at,
    }

@app.post("/analyze", status_code=201)
async def create_analysis(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_bytes = await file.read()
        analysis_data = analyze_trash_image(image_bytes)
        new_result = AnalysisResult(
            image_name=file.filename,
            location=analysis_data.get("location", "알 수 없는 위치"),
            trash_summary=analysis_data.get("trash_summary"),
            required_people=analysis_data.get("required_people"),
            estimated_time_min=analysis_data.get("estimated_time_min"),
            tool=analysis_data.get("tool")
        )
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return {"analysis_id": new_result.id}
    except Exception as e:
        logger.error(f"분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
