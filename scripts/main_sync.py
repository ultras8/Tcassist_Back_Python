import os
import json
from google import genai 
from google.genai import types 
from dotenv import load_dotenv
from sync_manager import sync_data 

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.0-flash" 

def process_and_sync(raw_text, code_from_filename=None):
    print(f"🤖 กำลังให้ AI ({MODEL_NAME}) วิเคราะห์ข้อมูล...")
    
    prompt = f"""
    คุณเป็นผู้เชี่ยวชาญด้านข้อมูล TCAS (Admission) ของประเทศไทย
    จงสกัดข้อมูลเกณฑ์การรับสมัครจากข้อความดิบ (Raw Text) ที่ได้รับ ให้ออกมาเป็น JSON เท่านั้น
    
    ข้อความดิบ:
    "{raw_text}"
    
    หมายเหตุพิเศษ: 
    1. หากหา 'program_code' ในข้อความไม่เจอ ให้ใช้รหัสนี้: "{code_from_filename}"
    2. "year": หากไม่ระบุให้ใช้ 2568
    
    รูปแบบ JSON ที่ต้องการ:
    {{
        "year": 2568,
        "uni_full": "ชื่อเต็มมหาวิทยาลัย",
        "uni_abbr": "ชื่อย่อ",
        "faculty": "ชื่อคณะ",
        "major": "ชื่อสาขา",
        "program_code": "{code_from_filename}",
        "program_type": "REGULAR",
        "source_url": "", 
        "weights": {{ "tgat": 20, "tpat3": 30 }},
        "min_scores": {{ "last_year_min": 0 }},
        "min_requirements": {{ 
            "gpax_min": 0, 
            "score_sum_min": 0,
            "extra_criteria": ""
        }}
    }}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
            ),
        )
        
        data = json.loads(response.text)
        if isinstance(data, list):
            data = data[0]
            
        # ✨ [จุดที่ 1] แก้บั๊ก NameError: final_code is not defined
        final_code = data.get('program_code') or code_from_filename
            
        # ✨ [จุดที่ 2] Mapping Enum ป้องกัน Error "พิเศษ"
        ai_program_type = str(data.get('program_type', 'REGULAR')).upper()
        type_mapping = {
            "REGULAR": "regular",
            "ปกติ": "regular",
            "INTERNATIONAL": "international",
            "นานาชาติ": "international",
            "VOCATIONAL": "vocational",
            "อาชีวะ": "vocational",
            "ENGLISH": "english",
            "ภาษาอังกฤษ": "english",
            "พิเศษ": "special",
            "SPECIAL": "special"
        }
        final_program_type = type_mapping.get(ai_program_type, "regular")

        # --- Mapping ข้อมูลลง Schema ---
        single_item = {
            "year": data.get('year', 2568),
            "fullName": data.get('uni_full'),
            "abbr": data.get('uni_abbr'),
            "facultyName": data.get('faculty'),  
            "majorName": data.get('major'),      
            "programCode": final_code, 
            "programType": final_program_type,
            "scoreWeights": data.get('weights'),
            "minScores": data.get('min_scores'),    
            "sourceUrl": data.get('source_url', ''), 
            "requirements": data.get('min_requirements')
        }
        
        formatted_data = [single_item]
        print(f"✅ AI แกะข้อมูลสำเร็จ: {single_item['majorName']} [Code: {final_code}]")
        
        # --- 5. ส่งเข้า Database ---
        # แก้ไข: ให้ส่งค่า True กลับไปบอก bulk_extractor ว่าสำเร็จ
        sync_data(formatted_data)
        return True

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน process_and_sync: {e}")
        return False

if __name__ == "__main__":
    process_and_sync("ข้อมูลทดสอบ...", "1234567890")