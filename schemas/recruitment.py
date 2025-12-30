from pydantic import BaseModel
from typing import Dict, Optional

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