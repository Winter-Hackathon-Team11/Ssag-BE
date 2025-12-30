import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_trash_image(image_data: bytes):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    이 사진 속 해안가 쓰레기를 분석해서 반드시 아래 JSON 형식으로만 응답해줘. 
    다른 설명은 생략해.
    {
        "trash_summary": {"plastic": 개수, "can": 개수, "glass": 개수, "net": 개수},
        "required_people": 권장인원(숫자),
        "estimated_time_min": 예상소요시간(분, 숫자),
        "tool": {"tongs": 개수, "bag": 개수},
        "location": "사진 기반 추정 위치(예: 부산 해운대구)"
    }
    """
    
    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    json_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_text)