import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_pdf_to_criteria(file_path):
    # 1. อัปโหลดไฟล์ PDF ขึ้นไปบนระบบของ Gemini (Temporary)
    print(f"📤 กำลังอัปโหลดไฟล์: {file_path}...")
    sample_file = genai.upload_file(path=file_path, mime_type="application/pdf")
    
    # 2. รอให้ระบบประมวลผลไฟล์สักครู่
    while sample_file.state.name == "PROCESSING":
        print(".", end="")
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)

    print("\n✅ ไฟล์พร้อมประมวลผลแล้ว!")

    # 3. สั่งให้ AI อ่านไฟล์และสกัดข้อมูล
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = """
    จากไฟล์ PDF ระเบียบการ TCAS ที่แนบมานี้ 
    จงสกัดข้อมูลเกณฑ์คะแนนการรับสมัคร (Admission Criteria) ของทุกสาขาวิชาที่ปรากฏ
    ให้ออกมาเป็น List ของ JSON ตามรูปแบบนี้เท่านั้น:
    [{
        "uni_full": "ชื่อมหาวิทยาลัย",
        "faculty": "คณะ",
        "major": "สาขา",
        "program_code": "รหัสหลักสูตร 14 หลัก",
        "weights": { "tgat": 20, "tpat3": 30, ... }
    }]
    ตอบกลับเฉพาะ JSON เท่านั้น
    """

    generation_config = {"response_mime_type": "application/json"}
    
    print("🤖 AI กำลังอ่านและวิเคราะห์ PDF (อาจใช้เวลาสักครู่)...")
    response = model.generate_content([sample_file, prompt], generation_config=generation_config)
    
    # 4. ลบไฟล์ออกจากระบบ Gemini (เพื่อความเป็นส่วนตัว)
    genai.delete_file(sample_file.name)
    
    return json.loads(response.text)

if __name__ == "__main__":
    # ใส่ชื่อไฟล์ PDF ที่น้องมี (ต้องอยู่ในโฟลเดอร์เดียวกันหรือระบุ Path ให้ถูกนะคะ)
    pdf_path = "2569_admission.pdf" 
    
    if os.path.exists(pdf_path):
        result = parse_pdf_to_criteria(pdf_path)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print(f"❌ ไม่พบไฟล์ {pdf_path} กรุณาตรวจสอบชื่อไฟล์อีกครั้งค่ะ")