import asyncio
import re
from playwright.async_api import async_playwright

async def program_url_hunter_v5():
    print("🚀 เริ่มภารกิจ: ทะลวงด่าน Field เพื่อคว้าเลข 15 หลัก!")
    all_program_codes = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 1. ไปหน้าหลักจุฬาฯ (001)
        await page.goto("https://course.mytcas.com/universities/001", wait_until="networkidle")
        
        # เก็บลิ้งก์คณะ (เช่น /faculties/21)
        faculty_links = [f"https://course.mytcas.com{await a.get_attribute('href')}" 
                         for a in await page.query_selector_all('a[href*="/faculties/"]')]
        
        print(f"📋 พบ {len(faculty_links)} คณะ...")

        # 2. วนลูปเข้าหน้าคณะเพื่อเก็บลิ้งก์ "Field" (ที่น้องส่งมาล่าสุด)
        for f_url in faculty_links:
            try:
                print(f"🔎 กำลังหา Field ในคณะ: {f_url}")
                await page.goto(f_url, wait_until="networkidle")
                await asyncio.sleep(2)

                # ดึงลิ้งก์ที่มีคำว่า /fields/
                field_links = [f"https://course.mytcas.com{await a.get_attribute('href')}" 
                               for a in await page.query_selector_all('a[href*="/fields/"]')]
                
                print(f"   ∟ 📂 เจอสาขาหลัก (Field) {len(field_links)} แห่ง")

                # 3. มุดเข้าแต่ละ Field เพื่อหาเลข 15 หลัก
                for field_url in field_links:
                    try:
                        print(f"      ∟ 🎯 เจาะลึกสาขา: {field_url.split('/')[-1]}")
                        await page.goto(field_url, wait_until="networkidle")
                        await asyncio.sleep(2) # รอให้รายชื่อโครงการงอก

                        content = await page.content()
                        # ค้นหาเลข 15 หลัก (รหัสโครงการ)
                        found = re.findall(r'1001\w{11}', content)
                        for code in found:
                            all_program_codes.add(code)
                            
                    except Exception as e:
                        continue
                
                print(f"✅ สะสมรหัสได้รวม: {len(all_program_codes)} รายการ")

            except Exception as e:
                print(f"⚠️ พลาดคณะ {f_url}")

        # 4. บันทึกผล
        if all_program_codes:
            with open("chula_program_urls.txt", "w", encoding="utf-8") as f:
                for code in sorted(list(all_program_codes)):
                    f.write(f"https://course.mytcas.com/programs/{code}\n")
            print(f"\n✨ ปิดจ๊อบตัวแม่! ได้มาทั้งหมด {len(all_program_codes)} ลิ้งก์สาขา!")
        else:
            print("❌ ยังไม่ได้เลย พี่เจจะไปบวชแล้วนะ!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(program_url_hunter_v5())