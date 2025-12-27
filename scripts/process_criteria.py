import os
import time
import shutil
import re
from main_sync import process_and_sync 

def start_extraction():
    folder_path = "all_scores"       
    success_path = "processed_scores" 
    
    if not os.path.exists(success_path):
        os.makedirs(success_path)

    all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.txt', '.json'))]
    total_files = len(all_files)
    
    if total_files == 0:
        print("✅ ไม่มีไฟล์เหลือให้จัดการแล้วค่ะ!")
        return

    success_count = 0
    fail_count = 0

    print(f"📦 ตรวจพบไฟล์ที่ต้องจัดการทั้งหมด {total_files} รายการ")
    print("🚀 เริ่มระบบสายพานอัตโนมัติ...")

    for index, filename in enumerate(all_files):
        file_path = os.path.join(folder_path, filename)
        dest_path = os.path.join(success_path, filename)
        
        # ✨ [จุดที่แก้] ดึงตัวเลข 10-13 หลักจากชื่อไฟล์ปัจจุบันในลูป
        match = re.search(r'\d{10,13}', filename)
        code_from_filename = match.group(0) if match else None
        
        print(f"🔄 [{index + 1}/{total_files}] กำลังจัดการ: {filename}", end=" ", flush=True)
        
        success = False
        retry_count = 0 
        
        while not success and retry_count < 3:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if not content.strip():
                    print("➡️ (ไฟล์ว่าง: ข้าม)")
                    shutil.move(file_path, dest_path)
                    success = True
                    break

                # ✨ [จุดที่แก้] ส่งรหัสที่ดึงได้จากชื่อไฟล์เข้าไปด้วย
                process_and_sync(content, code_from_filename)
                
                shutil.move(file_path, dest_path) 
                success = True 
                success_count += 1
                print("✨ สำเร็จ!")
                time.sleep(1) # ปรับเหลือ 1 วินาทีได้ถ้าใช้ 2.0 Flash

            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    print(f"\n🛑 โควตาเต็ม! พักยก 70 วินาที...")
                    time.sleep(70)
                    retry_count += 1
                else:
                    print(f"\n❌ Error อื่นๆ ที่ไฟล์ {filename}: {e}")
                    fail_count += 1
                    break # ออกจาก while ไปทำไฟล์ถัดไป

    # --- [ทริคเสริม] รายงานสรุปยอด ---
    print("\n" + "="*30)
    print("🏁 จบภารกิจตัวแม่!")
    print(f"✅ สำเร็จ: {success_count} ไฟล์")
    print(f"❌ พลาด: {fail_count} ไฟล์")
    print(f"📁 ไฟล์ที่สำเร็จถูกแยกไว้ที่: {success_path}")
    print("="*30)

if __name__ == "__main__":
    start_extraction()