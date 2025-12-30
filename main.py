from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import Generator
import logging

from db.database import engine, SessionLocal
from models.analysis import Base, AnalysisResult
import schemas

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """
    특정 분석 ID에 대한 상세 분석 결과를 조회합니다.
    """
    try:
        result = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if not result:
            logger.warning(f"분석 결과를 찾을 수 없음: ID={analysis_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # 이미지 URL 생성
        date_str = result.created_at.strftime("%Y-%m-%d")
        image_url = f"/uploads/{date_str}/{result.image_name}"
        
        logger.info(f"분석 결과 조회 성공: ID={analysis_id}")
        
        # 명세서 형식 응답
        return {
            "analysis_id": result.id,
            "image_url": image_url,
            "location": result.location,
            "area_type": "beach",  # 필요시 DB에서 가져오기
            "trash_summary": result.trash_summary or {},
            "recommended_resources": {
                "people": result.required_people,
                "tools": result.tool or {},
                "estimated_time_min": result.estimated_time_min
            },
            "created_at": result.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 결과 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )


@app.post("/recruitment/from-analysis/{analysis_id}")
async def create_recruitment(
    analysis_id: int = Path(..., gt=0),
    request: schemas.RecruitmentRequest = None,
    db: Session = Depends(get_db)
):
    """
    선택한 분석 결과를 기반으로 자원봉사자 모집용 구인글을 자동 생성합니다.
    """
    try:
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.id == analysis_id
        ).first()
        
        if not analysis:
            logger.warning(f"원천 분석 데이터를 찾을 수 없음: ID={analysis_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        trash_summary = analysis.trash_summary or {}
        if trash_summary:
            trash_names = {
                "plastic": "플라스틱",
                "can": "캔", 
                "net": "폐그물",
                "glass": "유리"
            }
            trash_items = [trash_names.get(k, k) for k in trash_summary.keys()]
            trash_text = ", ".join(trash_items)
        else:
            trash_text = "쓰레기"
        
        location = analysis.location or "해당 구역"
        required_people = analysis.required_people or 5
        estimated_time = analysis.estimated_time_min or 80
        
        title = f"[자원봉사 모집] {request.meeting_place.split()[0]} 환경 정화 활동"
        
        content = (
            f"{location}에서 {trash_text} 쓰레기가 다수 발견되었습니다.\n\n"
            f"현재 분석 결과 기준으로 약 {required_people}명의 봉사 인원이 필요하며, "
            f"집게·마대·장갑이 제공될 예정입니다.\n\n"
            f"예상 소요 시간은 약 {estimated_time}분이며, "
            f"안전한 환경 정화를 위해 많은 참여 부탁드립니다."
        )
        
        if request.additional_note:
            content += f"\n\n※ {request.additional_note}"

        logger.info(f"자원봉사 모집글 생성 성공: 분석 ID={analysis_id}")
        
        return {
            "title": title,
            "content": content,
            "required_people": required_people,
            "recommended_tools": analysis.tool or {},
            "activity_date": request.activity_date,
            "meeting_place": request.meeting_place
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"자원봉사 모집글 생성 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}