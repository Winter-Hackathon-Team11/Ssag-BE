from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, List

# 4번 구인글 입력
class RecruitmentRequest(BaseModel):
    activity_date: str
    meeting_place: str
    additional_note: Optional[str] = None

# 4번 구인글 결과 출력
class RecruitmentResponse(BaseModel):
    title: str
    content: str
    required_people: int
    recommended_tools: Dict[str, int]
    activity_date: str
    meeting_place: str


class RecruitmentListItem(BaseModel):
    id: int
    title: str
    location: Optional[str] = None
    required_people: int
    estimated_time_min: int
    activity_date: str
    status: str
    created_at: datetime


class RecruitmentListResponse(BaseModel):
    recruitments: List[RecruitmentListItem]


class RecruitmentDetailResponse(BaseModel):
    recruitment_id: int
    title: str
    content: str
    required_people: int
    recommended_tools: Dict[str, int]
    estimated_time_min: int
    activity_date: str
    meeting_place: str
    status: str
    created_at: datetime
    published_at: Optional[datetime] = None
