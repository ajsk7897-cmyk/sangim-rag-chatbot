import os
from pathlib import Path
from dotenv import dotenv_values
import google.generativeai as genai

# API 키 로드
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / "ChatbotAPI.env"
env_values = dotenv_values(env_path)
api_key = env_values.get("GEMINI_API_KEY")

if not api_key:
    print("API 키를 찾을 수 없습니다.")
    exit(1)

genai.configure(api_key=api_key)

print("=== 사용 가능한 모델 목록 ===")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name} | Display Name: {m.display_name}")
except Exception as e:
    print(f"에러 발생: {e}")
