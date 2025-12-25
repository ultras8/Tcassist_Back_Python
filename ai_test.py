import google.generativeai as genai
import os
import json
import time # เพิ่มตัวนี้เข้ามา
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_ai_extraction():
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # พยายามบังคับให้ AI ตอบแค่ JSON อย่างเดียวด้วยการใส่ "json" ลงใน Generation Config
    generation_config = {
        "response_mime_type": "application/json",
    }

    raw_text = """
    มหาวิทยาลัยเกษตรศาสตร์ คณะวิทยาศาสตร์ สาขาวิทยาการคอมพิวเตอร์ 
    รหัสหลักสูตร 10020104110101 
    ใช้เกณฑ์ TGAT 20% และ TPAT3 30% และ A-Level คณิต1 50%
    """

    prompt = f"สกัดข้อมูลจากข้อความนี้ให้อยู่ในรูปแบบ JSON ตาม Schema นี้: {{\"uni_full\": str, \"uni_abbr\": str, \"faculty\": str, \"major\": str, \"program_code\": str, \"weights\": dict}}. ข้อความ: {raw_text}"

    print("🤖 AI is thinking...")
    
    try:
        # ใส่ generation_config เพื่อบังคับให้ AI ตอบเป็น JSON
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # ปริ้นท์สิ่งที่ AI ตอบกลับมาจริงๆ เพื่อดูว่ามีอะไรผิดพลาดไหม
        print("--- Raw AI Response ---")
        print(response.text)
        print("-----------------------")

        data = json.loads(response.text)
        print("\n✅ Success!")
        return data
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        # ถ้าพัง ให้ลองเช็คว่า response มีค่าไหม
        if 'response' in locals():
            print(f"Full response object: {response}")
        return None

if __name__ == "__main__":
    test_ai_extraction()