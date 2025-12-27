import pandas as pd
import os
import re
from database import get_engine
from sqlalchemy import text # เพิ่มตัวนี้เพื่อใช้รันคำสั่ง SQL ตรงๆ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data_stats')
engine = get_engine()

def extract_info_from_filename(filename):
    """ดึงข้อมูล ปี และ รอบ จากชื่อไฟล์"""
    year_match = re.search(r'(\d{2})', filename)
    year = int("25" + year_match.group(1)) if year_match else None
    
    round_no = 3
    if 'r3_1' in filename:
        round_no = 3.1
    elif 'r3_2' in filename:
        round_no = 3.2
        
    return year, round_no

def process_files():
    if not os.path.exists(DATA_PATH):
        print(f"❌ ไม่พบโฟลเดอร์: {DATA_PATH}")
        return

    # --- ส่วนที่เพิ่ม: ล้างข้อมูลเก่าก่อนเริ่ม (TRUNCATE) ---
    if engine:
        try:
            with engine.begin() as conn:
                # RESTART IDENTITY จะช่วยให้เลข id เริ่มนับ 1 ใหม่ทุกครั้งที่ล้าง
                conn.execute(text("TRUNCATE TABLE admission_stats RESTART IDENTITY CASCADE;"))
                print("🗑️ ล้างข้อมูลเก่าในตาราง admission_stats เรียบร้อย (Clean Start!)")
        except Exception as e:
            print(f"⚠️ คำเตือน: ล้างตารางไม่สำเร็จ (อาจยังไม่มีตาราง) แต่จะลองลงข้อมูลต่อไปค่ะ: {e}")

    files = [f for f in os.listdir(DATA_PATH) if f.endswith('.xlsx')]
    
    for filename in files:
        year, round_no = extract_info_from_filename(filename)
        print(f"📦 กำลังประมวลผล: {filename} (ปี {year} รอบ {round_no})")
        
        file_path = os.path.join(DATA_PATH, filename)
        df = pd.read_excel(file_path)
        
        # จัดการ Merge Cells
        df = df.ffill() 

        # ค้นหาคอลัมน์ 'รหัสหลักสูตร' แบบยืดหยุ่น
        code_col = [c for c in df.columns if 'รหัส' in str(c) and 'หลักสูตร' in str(c)]
        if not code_col:
            code_col = [c for c in df.columns if 'รหัส' in str(c)]
        
        if code_col:
            df['programCode'] = df[code_col[0]].astype(str).str.strip().str[:14]
        else:
            print(f"⚠️ ข้ามไฟล์ {filename} เพราะหารหัสหลักสูตรไม่เจอ")
            continue

        # แมปชื่อคอลัมน์
        column_mapping = {
            'ต่ำสุดประมวลผลครั้งที่ 2': 'minScore', 'สูงสุดประมวลผลครั้งที่ 2': 'maxScore',
            'ต่ำสุด': 'minScore', 'สูงสุด': 'maxScore', 'คะแนนต่ำสุด': 'minScore', 'คะแนนสูงสุด': 'maxScore',
            'รับ': 'total_seats', 'รับเท่าไหร่': 'total_seats', 'จำนวนรับ': 'total_seats',
            'สมัคร': 'total_candidates', 'สมัครเท่าไหร่': 'total_candidates', 'จำนวนผู้สมัคร': 'total_candidates'
        }
        df = df.rename(columns=column_mapping)
        
        # เตรียมข้อมูล
        cols_to_keep = ['programCode', 'total_seats', 'total_candidates', 'minScore', 'maxScore']
        df_final = df[[c for c in cols_to_keep if c in df.columns]].copy()
        df_final['year'] = year
        df_final['round_no'] = round_no

        # ทำความสะอาดข้อมูล
        df_final = df_final[df_final['programCode'].str.len() >= 10]
        for col in ['minScore', 'maxScore', 'total_seats', 'total_candidates']:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

        # ยิงเข้า Database
        if engine:
            try:
                df_final.to_sql('admission_stats', con=engine, if_exists='append', index=False)
                print(f"✅ บันทึกปี {year} เรียบร้อย! ({len(df_final)} แถว)")
            except Exception as e:
                print(f"❌ พังที่ไฟล์ {filename}: {e}")

if __name__ == "__main__":
    process_files()