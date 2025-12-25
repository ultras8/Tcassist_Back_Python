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
            # 1. จัดการตาราง universities (Check or Insert)
            cur.execute(
                'SELECT id FROM universities WHERE "fullName" = %s', 
                (item['uni_full'],)
            )
            uni = cur.fetchone()

            if not uni:
                print(f"➕ Adding University: {item['uni_full']}")
                cur.execute(
                    'INSERT INTO universities ("fullName", "abbr", "createdAt") VALUES (%s, %s, NOW()) RETURNING id',
                    (item['uni_full'], item['uni_abbr'])
                )
                uni_id = cur.fetchone()['id']
            else:
                uni_id = uni['id']

            # 2. จัดการตาราง admission_criteria (Upsert โดยใช้ programCode)
            print(f"📑 Syncing: {item['faculty']} - {item['major']}")
            
            # ใส่ Double Quotes ครอบชื่อ Column ที่เป็น camelCase
            query = """
                INSERT INTO admission_criteria 
                ("universityId", "facultyName", "majorName", "programCode", "scoreWeights", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT ("programCode") DO UPDATE SET
                    "scoreWeights" = EXCLUDED."scoreWeights",
                    "updatedAt" = NOW();
            """
            
            cur.execute(query, (
                uni_id,
                item['faculty'],
                item['major'],
                item['program_code'],
                json.dumps(item['weights'])
            ))

        conn.commit()
        print("✨ All data synced successfully!")

    except Exception as e:
        print(f"❌ Error during sync: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# --- ทดสอบรันด้วยข้อมูล Mock ---
if __name__ == "__main__":
    test_data = [{
        "uni_full": "จุฬาลงกรณ์มหาวิทยาลัย",
        "uni_abbr": "CU",
        "faculty": "วิศวกรรมศาสตร์",
        "major": "วิศวกรรมคอมพิวเตอร์",
        "program_code": "10010101101011",
        "weights": {"tgat": 20, "tpat3": 30, "a_level_math1": 50}
    }]
    sync_data(test_data)