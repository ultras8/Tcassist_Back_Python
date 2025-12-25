import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pdf_ai_parser import parse_pdf_to_criteria # ดึงไฟล์ที่น้องเพิ่งทำสำเร็จมาใช้
from sync_manager import sync_data

def crawl_and_process(target_url):
    print(f"🌐 กำลังเข้าตรวจสอบหน้าเว็บ: {target_url}")
    
    try:
        # 1. ไปดูหน้าเว็บว่ามี PDF ไหม
        response = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ค้นหาทุกลิ้งก์ (<a>) ที่ลงท้ายด้วย .pdf
        pdf_links = []
        for a in soup.find_all('a', href=True):
            if a['href'].endswith('.pdf'):
                # แปลง URL สัมพัทธ์ให้เป็น URL เต็ม (เช่น /doc.pdf -> https://uni.ac.th/doc.pdf)
                full_url = urljoin(target_url, a['href'])
                pdf_links.append(full_url)
        
        if not pdf_links:
            print("❌ ไม่พบไฟล์ PDF ในหน้านี้เลยค่ะ")
            return

        # 2. ลองโหลดไฟล์แรกที่เจอมาทดสอบ (หรือจะวนลูปทุกลิ้งก์ก็ได้นะ)
        target_pdf = pdf_links[0]
        file_name = "downloaded_temp.pdf"
        
        print(f"📥 เจอ PDF แล้ว! กำลังดาวน์โหลด: {target_pdf}")
        pdf_data = requests.get(target_pdf).content
        with open(file_name, 'wb') as f:
            f.write(pdf_data)

        # 3. ส่งต่อให้ AI (จากไฟล์เก่าที่เราเขียนไว้)
        print("🤖 ส่งไฟล์ให้ AI วิเคราะห์ต่อ...")
        extracted_data = parse_pdf_to_criteria(file_name)

        # 4. บันทึกลง Database
        if extracted_data:
            sync_data(extracted_data)
            print("🚀 บันทึกข้อมูลเรียบร้อย! ระบบสมบูรณ์แบบ")

        # 5. (Optional) ลบไฟล์ทิ้งหลังใช้เสร็จ
        # os.remove(file_name)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในท่อส่งข้อมูล: {e}")

if __name__ == "__main__":
    # ลองใส่ URL หน้าประกาศรับสมัครของมหาลัยที่น้องสนใจ
    # ตัวอย่าง: หน้าประกาศของ ม.เกษตร หรือ มหาลัยที่มีลิ้งก์ PDF วางอยู่
    test_url = "https://admission.ku.ac.th/ประกาศรับสมัคร" 
    crawl_and_process(test_url)