from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    # 기본 식별자
    id = Column(Integer, primary_key=True, index=True)

    original_image = Column(String(255), nullable=False)

    # 이미지 정보
    image_name = Column(String(255), nullable=False)

    # 메타 정보
    location = Column(String(255), nullable=True)

    # AI 분석 결과 (쓰레기 종류/개수)
    trash_summary = Column(JSON, nullable=False)
    # 예: {"plastic": 14, "can": 6, "net": 1}

    # ===== 추천 인원 =====
    required_people = Column(Integer, nullable=False)

    # ===== 예상 소요 시간 (분) =====
    estimated_time_min = Column(Integer, nullable=False)

    # ===== 추천 도구 수량 =====
    tool= Column(JSON, nullable=False)
    # 예:
    # {
    #   "tongs": 5,     # 집게
    #   "bags": 8,      # 마대 / 쓰레기 봉투
    #   "gloves": 5,    # 보호 장갑
    #   "cutter": 1     # 폐그물·로프 절단용 칼
    # }

    generated_title = Column(String(255), nullable=True)
    generated_content = Column(Text, nullable=True)
    activity_date = Column(String(255), nullable=True)
    meeting_place = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # 생성 시각
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    status = Column(
        Enum("analyzed", "uploaded", "expired", name="analysis_status"),
        default="analyzed",
        nullable=False,
    )
