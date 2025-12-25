import asyncio
from playwright.async_api import async_playwright

async def run_test():
    print("🚀 เริ่มต้นระบบหุ่นยนต์...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        url = "https://course.mytcas.com/universities/002/faculties/21"
        print(f"🌐 กำลังวิ่งไปที่: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle")
            print("⏳ บอทกำลังใช้ตาทิพย์มุด Shadow DOM หา /programs...")
            
            # 1. ใช้ CSS Selector ปกติ (Playwright จะมุด Shadow DOM ให้เองอัตโนมัติ!)
            # เราจะหา <a> ที่มี href ที่มีคำว่า /programs
            selector = 'a[href*="/programs"]'
            
            # รอให้มันปรากฏ (visible)
            await page.wait_for_selector(selector, timeout=15000)
            
            # 2. ดึง elements ทั้งหมด
            elements = await page.query_selector_all(selector)
            
            major_links = []
            for el in elements:
                name = await el.inner_text()
                href = await el.get_attribute("href")
                if href:
                    major_links.append({
                        "name": name.strip(),
                        "url": f"https://course.mytcas.com{href}" if href.startswith('/') else href
                    })

            # กรองลิ้งก์ซ้ำ
            unique_majors = {m['url']: m for m in major_links}.values()
            major_links = list(unique_majors)

            print(f"🎯 เย้! ใช้ตาทิพย์เจอคณะ/สาขา ทั้งหมด {len(major_links)} แห่ง")
            # ---------------------------------------------------------

            # (ส่วนที่เหลือเหมือนเดิม...)
            for m in major_links[:2]:
                print(f"👉 กำลังมุดเข้าสาขา: {m['name']}")
                major_page = await browser.new_page()
                await major_page.goto(m['url'], wait_until="networkidle")
                
                # ลองหาปุ่ม "รอบที่ 3" จากข้อความตรงๆ
                admission_tab = major_page.get_by_text("รอบที่ 3")
                
                if await admission_tab.count() > 0:
                    await admission_tab.first.click() # คลิกอันแรกที่เจอ
                    await major_page.wait_for_timeout(2000)
                    content = await major_page.inner_text("body")
                    print(f"✅ ดึงข้อมูลสำเร็จ! (ตัวอย่าง): {content[:50]}...")
                
                await major_page.close()
                
        except Exception as e:
            print(f"❌ พังตรงนี้: {e}")
        
        await browser.close()
        print("🏁 จบการทดสอบ")

if __name__ == "__main__":
    asyncio.run(run_test())