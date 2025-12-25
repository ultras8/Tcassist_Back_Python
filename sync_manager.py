import json
from database import get_connection
from psycopg2 import extras

def sync_data(scraped_items):
    conn = get_connection()
    if not conn:
        return

    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)

        for item in scraped_items:
            # 1. จัดการตาราง universities
            cur.execute(
                'SELECT id FROM universities WHERE "fullName" = %s', 
                (item['fullName'],) # แก้จาก uni_full
            )
            uni = cur.fetchone()

            if not uni:
                print(f"➕ Adding University: {item['fullName']}")
                cur.execute(
                    'INSERT INTO universities ("fullName", "abbr", "createdAt") VALUES (%s, %s, NOW()) RETURNING id',
                    (item['fullName'], item['abbr']) # แก้จาก uni_full, uni_abbr
                )
                uni_id = cur.fetchone()['id']
            else:
                uni_id = uni['id']

            # 2. จัดการตาราง admission_criteria (Upsert)
            print(f"📑 Syncing: {item['facultyName']} - {item['majorName']}")
            
            # เราจะระบุชื่อคอลัมน์ชัดๆ เพื่อให้ Postgres ไม่งง (และไม่ต้องใส่ครบทุกช่องก็ได้)
            query = """
                INSERT INTO admission_criteria 
                ("universityId", "facultyName", "majorName", "programCode", "scoreWeights", "programType", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT ("programCode") DO UPDATE SET
                    "scoreWeights" = EXCLUDED."scoreWeights",
                    "programType" = EXCLUDED."programType",
                    "facultyName" = EXCLUDED."facultyName",
                    "majorName" = EXCLUDED."majorName",
                    "updatedAt" = NOW();
            """
            
            # ส่งค่าให้ตรงกับ %s ทั้ง 6 ตัวข้างบน
            cur.execute(query, (
                uni_id,                              # 1. "universityId"
                item['facultyName'],                 # 2. "facultyName"
                item['majorName'],                   # 3. "majorName"
                item['programCode'],                 # 4. "programCode"
                json.dumps(item['scoreWeights']),     # 5. "scoreWeights"
                item.get('programType', 'REGULAR').lower()   # 6. "programType" (ตัวเจ้าปัญหา!)
            ))

        conn.commit()
        print("✨ All data synced successfully!")

    except Exception as e:
        print(f"❌ Error during sync: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()