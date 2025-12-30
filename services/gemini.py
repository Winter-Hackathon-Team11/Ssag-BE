import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def analyze_trash_image(image_data: bytes):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["해변 쓰레기 사진을 분석해서 JSON으로 답해줘. location, trash_summary, required_people, estimated_time_min, tool 항목이 꼭 있어야 해.", image_data]
        )
        return response.parsed if response.parsed else json.loads(response.text)
        
    except Exception as e:
        print(f"⚠️ Gemini 실제 호출 실패: {e}")
        return {
            "location": "부산 해변 (분석 실패 대체)",
            "trash_summary": {"plastic": 5, "etc": 2},
            "required_people": 5,          
            "estimated_time_min": 60,    
            "tool": {"집게": 5, "마대": 5}  
        }

def generate_recruitment_content(analysis_data: dict, user_request: dict):
    try:
        prompt = f"""
        너는 환경 보호 단체의 홍보 전문가야. 아래 정보를 바탕으로 인스타그램이나 블로그에 올릴 매력적인 자원봉사 모집글을 작성해줘.
        
        [지역 정보]: {analysis_data.get('location', '알 수 없는 지역')}
        [발견된 쓰레기]: {analysis_data.get('trash_summary', {})}
        [필요 인원]: {analysis_data.get('required_people', 5)}명
        [모임 시간 및 장소]: {user_request.get('activity_date')} / {user_request.get('meeting_place')}
        
        글에는 '환경 보호의 중요성'과 '함께하면 즐겁다'는 내용을 포함하고, 이모지를 적절히 섞어서 500자 정도로 작성해줘.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        if not response.text:
            raise ValueError("Gemini 응답이 비어있습니다.")

        return {
            "title": f"🌊 {analysis_data.get('location', '해변')} 정화 활동 모집",
            "content": response.text.strip()
        }
    except Exception as e:
        if "429" in str(e):
            msg = "AI 사용량이 초과되었습니다. 1분 뒤에 다시 시도해주세요!"
        else:
            msg = f"서비스 점검 중입니다: {str(e)}"
            
        return {
            "title": "잠시 후 다시 시도해주세요",
            "content": msg
        }