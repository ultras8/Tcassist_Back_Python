import json
import uuid # เผื่อใน DB ใช้ UUID หรือเอาไว้สร้างค่าเบื้องต้น
from database import get_connection
from psycopg2 import extras

def sync_data(scraped_items):
    conn = get_connection()
    if not conn: 
        return
        
    cur = None
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        for item in scraped_items:
            # --- 1. จัดการมหาวิทยาลัย (หาไม่เจอ...สร้างใหม่!) ---
            full_name = item.get('fullName')
            cur.execute('SELECT id FROM universities WHERE "fullName" = %s', (full_name,))
            uni = cur.fetchone()
            
            if uni:
                uni_id = uni['id']
            else:
                # ✨ จุดไม้ตาย: สร้างมหาวิทยาลัยใหม่ทันที
                print(f"🆕 พบมหาวิทยาลัยใหม่: {full_name} ... กำลังเพิ่มลงในระบบ")
                insert_uni_query = """
                    INSERT INTO universities ("fullName", "abbr")
                    VALUES (%s, %s)
                    RETURNING id;
                """
                cur.execute(insert_uni_query, (full_name, item.get('abbr', '')))
                uni_id = cur.fetchone()['id']

            # 🚨 ตรวจสอบเฉพาะ Program Code เท่านั้น (เพราะ Uni ID เราการันตีว่ามีแน่แล้ว)
            if not item.get('programCode'):
                print(f"\n❌ [ERROR] ข้ามรายการนี้เพราะไม่มี Program Code:")
                print(f"   - สาขา: {item.get('majorName')}")
                continue 

            # --- 2. เริ่ม Sync ข้อมูลเข้า admission_criteria ---
            print(f"📑 Syncing: {item['facultyName']} - {item['majorName']} ({item['year']})")
            
            query = """
                INSERT INTO admission_criteria 
                (
                    "universityId", "facultyName", "majorName", "programCode", "year", 
                    "programType", "scoreWeights", "minScores", "sourceUrl", "requirements", 
                    "createdAt", "updatedAt"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT ("programCode", "year") 
                DO UPDATE SET
                    "scoreWeights" = EXCLUDED."scoreWeights",
                    "minScores" = EXCLUDED."minScores",
                    "sourceUrl" = EXCLUDED."sourceUrl",
                    "requirements" = EXCLUDED."requirements",
                    "updatedAt" = NOW();
            """
            
            score_weights = extras.Json(item.get('scoreWeights') or {})
            min_scores = extras.Json(item.get('minScores') or {})
            req_data = item.get('requirements')
            final_req = extras.Json(req_data) if isinstance(req_data, (dict, list)) else extras.Json({"raw": str(req_data)})
            p_type = str(item.get('programType') or 'regular').lower()

            cur.execute(query, (
                uni_id,
                item['facultyName'],
                item['majorName'],
                item['programCode'],
                item.get('year'),
                p_type,
                score_weights,
                min_scores,
                item.get('sourceUrl', ''),
                final_req,
            ))
            
        conn.commit()
        print("🎉 ภารกิจ Sync ข้อมูลสำเร็จเรียบร้อยค่ะ!")
        
    except Exception as e:
        print(f"❌ Error ใน sync_manager: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()