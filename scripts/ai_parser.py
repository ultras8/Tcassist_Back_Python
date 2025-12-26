import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_admission_criteria(raw_text):
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = f"""
    คุณเป็นผู้เชี่ยวชาญด้านข้อมูล TCAS 
    จงสกัดข้อมูลเกณฑ์คะแนนจากข้อความที่กำหนดให้อยู่ในรูปแบบ JSON เท่านั้น โดยห้ามมีคำอธิบายอื่นเพิ่มเติม

    ข้อความ:
    "{raw_text}"

    เงื่อนไขการสกัดข้อมูล:
    - uni_full: ชื่อเต็มมหาวิทยาลัย
    - uni_abbr: ชื่อย่อมหาวิทยาลัย (ถ้าไม่มีให้เป็น null)
    - faculty: ชื่อคณะ
    - major: ชื่อสาขาวิชา/วิชาเอก
    - program_code: รหัสหลักสูตร 15 หลัก
    - program_type: ให้ตอบเฉพาะค่า 'REGULAR', 'SPECIAL', 'INTERNATIONAL', หรือ 'ENGLISH_PROGRAM' เท่านั้น
    - weights: สกัดชื่อวิชาและค่าน้ำหนัก (%) โดยใช้ Key เป็นภาษาอังกฤษตัวเล็ก (เช่น tgat, tpat1, tpat3, a_level_math1, a_level_phy)

    รูปแบบ JSON ที่ต้องการ:
    {{
        "uni_full": "...",
        "uni_abbr": "...",
        "faculty": "...",
        "major": "...",
        "program_code": "...",
        "program_type": "...",
        "weights": {{
            "วิชา": 0,
            "วิชา": 0
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