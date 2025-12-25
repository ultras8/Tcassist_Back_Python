import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from sync_manager import sync_data  # ดึงฟังก์ชันที่เราทำสำเร็จก่อนหน้านี้มาใช้

load_dotenv()

# ตั้งค่า AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/gemini-2.5-flash')

def process_and_sync(raw_text):
    print("🤖 กำลังให้ AI วิเคราะห์ข้อมูล...")
    
    generation_config = {"response_mime_type": "application/json"}
    prompt = f"""
    สกัดข้อมูลเกณฑ์คะแนน TCAS จากข้อความนี้เป็น JSON:
    "{raw_text}"
    
    เงื่อนไข:
    - ใช้ชื่อ key ตามนี้: uni_full, uni_abbr, faculty, major, program_code, weights
    - ใน weights ให้ใช้ชื่อวิชาเป็นภาษาอังกฤษตัวเล็ก เช่น tgat, tpat3, a_level_math1
    """

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        data = json.loads(response.text)
        
        # แปลงชื่อ key ให้ตรงกับที่ sync_manager ต้องการ (ถ้าจำเป็น)
        # ในที่นี้เราส่งเป็น list ของ dict เข้าไป
        formatted_data = [{
            "uni_full": data['uni_full'],
            "uni_abbr": data.get('uni_abbr', ''),
            "faculty": data['faculty'],
            "major": data['major'],
            "program_code": data['program_code'],
            "weights": data['weights']
        }]
        
        print(f"✅ AI แกะข้อมูลสำเร็จ: {data['major']}")
        
        # ส่งเข้า Database
        sync_data(formatted_data)
        print("🚀 ข้อมูลถูกบันทึกลง Database เรียบร้อยแล้ว!")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    # ลองใส่ข้อความเกณฑ์การรับจริงๆ ที่น้องอยากเพิ่มลง DB
    text_to_import = """
    มหาวิทยาลัยเกษตรศาสตร์ คณะวิทยาศาสตร์ สาขาวิทยาการคอมพิวเตอร์ 
    รหัสหลักสูตร 10020104110101 
    ใช้เกณฑ์ TGAT 20% และ TPAT3 30% และ A-Level คณิต1 50%
    """
    process_and_sync(text_to_import)