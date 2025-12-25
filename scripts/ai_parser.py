import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_admission_criteria(raw_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    คุณเป็นผู้เชี่ยวชาญด้านข้อมูล TCAS 
    จงสกัดข้อมูลเกณฑ์คะแนนจากข้อความต่อไปนี้ให้อยู่ในรูปแบบ JSON เท่านั้น
    
    ข้อความ:
    "{raw_text}"
    
    รูปแบบ JSON ที่ต้องการ:
    {{
        "uni_full": "ชื่อเต็มมหาวิทยาลัย",
        "uni_abbr": "ชื่อย่อ (ถ้ามี)",
        "faculty": "ชื่อคณะ",
        "major": "ชื่อสาขา",
        "program_code": "รหัสหลักสูตร 14 หลัก",
        "weights": {{
            "tgat": 20,
            "tpat3": 30,
            ...
        }}
    }}
    """
    
    response = model.generate_content(prompt)
    # ลบพวก ```json ... ``` ออกเพื่อให้ได้ข้อความ JSON เพียวๆ
    json_str = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_str)

# --- ทดสอบด้วยข้อความจริง ---
if __name__ == "__main__":
    sample_text = """
    จุฬาลงกรณ์มหาวิทยาลัย คณะวิศวกรรมศาสตร์ สาขาวิศวกรรมคอมพิวเตอร์ 
    รหัสหลักสูตร 10010101101011 
    ใช้เกณฑ์คะแนน TGAT 20% และ TPAT3 อีก 30% ส่วนที่เหลือเป็น A-Level Math1 50%
    """
    result = extract_admission_criteria(sample_text)
    print(json.dumps(result, indent=4, ensure_ascii=False))