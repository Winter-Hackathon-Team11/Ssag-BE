from google.genai import types
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
        {analysis_data}와 {user_request} 정보를 바탕으로 이모지를 섞어 
        150자 내외의 짧고 강렬한 SNS 스타일 자원봉사 모집글을 작성해줘.
        문장마다 줄바꿈을 두 번씩 넣어줘.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
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

def analyze_trash_image_resources(image_path: str, trash_summary: dict[str, int]):
    prompt = f"""
You are a decision-support AI for environmental cleanup operations.

You are given:
1) An on-site image
2) A precomputed summary of trash types and counts (trash_summary)

The provided trash_summary is a preliminary result.
You may use the image to:
- Translate trash class names into Korean
- Add additional trash items ONLY if they are clearly visible in the image
- Adjust counts conservatively if obvious trash was missing

Do NOT remove existing trash types from trash_summary.
Do NOT invent trash that is not visible in the image.

Input trash_summary:
{json.dumps(trash_summary, ensure_ascii=False)}

Your tasks:
1) Produce a final trash_summary:
   - Keys must be Korean trash names
   - Values must be integer counts
2) Based on the final trash_summary, calculate recommended cleanup resources

You MUST respond in the following JSON format ONLY.
Do NOT include explanations, markdown, code blocks, or any extra text.

{{
  "trash_summary": {{
    "쓰레기_이름(한국어)": number,
    "쓰레기_이름(한국어)": number
  }},
  "recommended_resources": {{
    "people": number,
    "tools": {{
      "도구_이름(한국어)": number,
      "도구_이름(한국어)": number
    }},
    "estimated_time_min": number
  }}
}}

Rules:
- The field "people" represents the required number of people for cleanup.
- The quantity of each tool must be greater than or equal to "people".
- estimated_time_min must be a realistic value based on typical cleanup speed.
- Add "cutter" ONLY if fishing nets, ropes, or tangled materials are visible.
- Be conservative when adding new trash items or increasing counts.
"""

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg",
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            image_part,
        ],
    )

    json_text = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    print(json_text)
    return json.loads(json_text)
