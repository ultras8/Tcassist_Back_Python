import json
from database import get_connection
from psycopg2 import extras  # ⬅️ ตรวจสอบว่า import ตัวนี้มาแล้ว

def sync_data(scraped_items):
    conn = get_connection()
    if not conn: return

    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)

        for item in scraped_items:
            # 1. จัดการตาราง universities (เหมือนเดิม)
            cur.execute('SELECT id FROM universities WHERE "fullName" = %s', (item['fullName'],))
            uni = cur.fetchone()

            if not uni:
                cur.execute(
                    'INSERT INTO universities ("fullName", "abbr", "createdAt") VALUES (%s, %s, NOW()) RETURNING id',
                    (item['fullName'], item['abbr'])
                )
                uni_id = cur.fetchone()['id']
            else:
                uni_id = uni['id']

            # 2. จัดการตาราง admission_criteria
            print(f"📑 Syncing: {item['facultyName']} - {item['majorName']}")
            
            query = """
                INSERT INTO admission_criteria 
                ("universityId", "facultyName", "majorName", "programCode", "scoreWeights", "programType", "requirements", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT ("programCode") DO UPDATE SET
                    "scoreWeights" = EXCLUDED."scoreWeights",
                    "programType" = EXCLUDED."programType",
                    "facultyName" = EXCLUDED."facultyName",
                    "majorName" = EXCLUDED."majorName",
                    "requirements" = EXCLUDED."requirements",
                    "updatedAt" = NOW();
            """
            
            # ✨ จุดสำคัญ: ใช้ extras.Json(item['scoreWeights']) 
            # วิธีนี้ psycopg2 จะจัดการแปลง dict เป็น json ให้เราเองแบบไร้รอยต่อ!
            # ดึงค่าออกมาเตรียมไว้ก่อน
            score_weights = item.get('scoreWeights', {})
            requirements = item.get('requirements', '')
            
            # เช็คเผื่อว่า requirements ดันเป็น dict/list มาจาก Scraper
            if isinstance(requirements, (dict, list)):
                requirements = json.dumps(requirements, ensure_ascii=False)
            else:
                requirements = str(requirements) # บังคับเป็น string แน่นอน

            print(f"📑 Syncing: {item['facultyName']} - {item['majorName']}")
            
            # ส่งค่า (ใช้ extras.Json เฉพาะกับคอลัมน์ที่เป็น JSONB)
            cur.execute(query, (
                uni_id,
                str(item['facultyName']),
                str(item['majorName']),
                str(item['programCode']),
                extras.Json(score_weights),    # บังคับแปลงเป็น JSON
                str(item.get('programType', 'REGULAR')).lower(),
                requirements                   # ส่งค่าที่เราจัดการเป็น string แล้ว
            ))

        conn.commit()
        print("✨ All data synced successfully!")

    except Exception as e:
        print(f"❌ Error during sync: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()