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
        prompt = f"{analysis_data}와 {user_request} 정보를 바탕으로 매력적인 구인글을 작성해줘."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return {
            "title": f"🌊 {analysis_data['location']} 정화 활동 모집",
            "content": response.text
        }
    except:
        return {
            "title": "함께 바다를 청소해요!",
            "content": "분석 결과를 바탕으로 정화 활동에 참여할 분들을 모집합니다."
        }