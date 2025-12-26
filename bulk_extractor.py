import os
import time
import shutil # ⬅️ เพิ่มตัวนี้เพื่อใช้ย้ายไฟล์
from main_sync import process_and_sync 

def start_extraction():
    folder_path = "all_scores"
    success_path = "processed_scores" # ⬅️ โฟลเดอร์สำหรับไฟล์ที่เสร็จแล้ว
    
    # 📁 สร้างโฟลเดอร์สำหรับเก็บไฟล์ที่สำเร็จ (ถ้ายังไม่มี)
    if not os.path.exists(success_path):
        os.makedirs(success_path)

    # อ่านรายชื่อไฟล์เฉพาะที่ยังเหลืออยู่ใน all_scores
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    total_files = len(all_files)
    
    if total_files == 0:
        print("✅ ไม่มีไฟล์เหลือให้จัดการแล้วค่ะ!")
        return

    print(f"📦 ตรวจพบไฟล์ที่ต้องจัดการ {total_files} รายการ")

    for index, filename in enumerate(all_files):
        file_path = os.path.join(folder_path, filename)
        dest_path = os.path.join(success_path, filename) # ปลายทางหลังทำเสร็จ
        
        print(f"🔄 [{index + 1}/{total_files}] กำลังจัดการ: {filename}")
        
        success = False
        while not success:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if not content.strip():
                    shutil.move(file_path, dest_path) # ย้ายไฟล์ว่างทิ้งไปเลย
                    success = True
                    break

                process_and_sync(content)
                
                # ✅ ถ้ามาถึงจุดนี้แปลว่า Sync สำเร็จ! 
                # ย้ายไฟล์ไปที่โฟลเดอร์ processed_scores ทันที
                shutil.move(file_path, dest_path) 
                
                success = True 
                print(f"✨ สำเร็จและย้ายไฟล์ไปที่ {success_path} เรียบร้อย!")
                time.sleep(15) 

            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"🛑 โควตาเต็ม! พักยก 70 วินาที...")
                    time.sleep(70)
                else:
                    print(f"❌ Error อื่นๆ: {e}")
                    # ถ้าพังแบบอื่นที่ไม่ใช่ลิมิต อาจจะกักไว้ที่เดิมก่อนเพื่อมาเช็คทีหลัง
                    break 

    print("\n🏁 จบภารกิจ! ไฟล์ที่สำเร็จถูกแยกไว้ที่ processed_scores แล้วค่ะ")

if __name__ == "__main__":
    start_extraction()