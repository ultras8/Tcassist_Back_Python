import requests
import json

def get_tcas_score_smartly():
    print("✨ เริ่มภารกิจสวยๆ: ดึงข้อมูลผ่าน API (ไม่ต้องเปิด Browser!)")
    
    # ลิสต์รหัส 15 หลักที่เรามี
    target_codes = [
        "10010121300001A", 
        "10010121300501A", 
        "10010121300601A"
    ]
    
    for code in target_codes:
        # URL ของ API สวรรค์ (รอบที่ 3)
        api_url = f"https://api.mytcas.com/v1/programs/{code}/admission/3"
        
        print(f"📡 กำลังขอข้อมูลรหัส: {code}...")
        
        try:
            # ส่งคำขอไปที่ Server
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                
                # บันทึกเป็น JSON เลย จะได้เอาไปทำ Database ง่ายๆ
                filename = f"data_{code}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                print(f"✅ สำเร็จ! ข้อมูลมาแบบสะอาดกริบ บันทึกใน {filename}")
            else:
                print(f"❌ แป่ว! Server บอกว่าไม่มีข้อมูลรอบ 3 สำหรับรหัส {code} (Code: {response.status_code})")
                
        except Exception as e:
            print(f"⚠️ เกิดข้อผิดพลาดทางเทคนิค: {e}")

    print("\n💖 จบภารกิจแบบสวยงาม ไม่เหนื่อยแล้วค่ะ!")

if __name__ == "__main__":
    get_tcas_score_smartly()