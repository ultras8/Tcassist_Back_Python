import asyncio
import os
from playwright.async_api import async_playwright

async def fast_js_striker():
    output_dir = "chula_eng_scores"
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    async with async_playwright() as p:
        # 💡 ปรับแต่ง Browser ให้เบาที่สุด: บล็อกรูปภาพเพื่อความเร็ว!
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ฟังก์ชันช่วยบล็อกรูปภาพ (ประหยัดเวลาโหลด)
        # ฟังก์ชันช่วยบล็อกรูปภาพ (เวอร์ชันแก้ Syntax Error)
        async def block_aggressively(route):
            if route.request.resource_type in ["image", "font", "media"]:
                await route.abort()
            else:
                # ใช้ .continue_() (มี underscore ต่อท้าย) เพื่อเลี่ยงคำสงวนของ Python ค่ะ
                await route.continue_() 
        
        await page.route("**/*", block_aggressively)

        target_codes = ["10010121300001A", "10010121300501A", "10010121300601A"]
        
        for code in target_codes:
            url = f"https://course.mytcas.com/programs/{code}"
            print(f"\n⚡ จู่โจมเป้าหมาย: {url}")
            
            try:
                # 💡 เปลี่ยนจาก networkidle เป็น domcontentloaded (โหลดเร็วกว่ามาก)
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # รอนิดหน่อยให้ปุ่มเลข 3 งอกออกมา (ไม่ต้องรอทั้งหน้า)
                print("⏳ รอโครงสร้างปุ่ม...")
                await page.wait_for_selector('a:has-text("3")', timeout=60000)

                # 🖱️ คลิกปุ่มเลข 3 ทันที
                await page.evaluate("""
                    () => {
                        const btn3 = Array.from(document.querySelectorAll('a')).find(el => el.textContent.includes('3'));
                        if (btn3) btn3.click();
                    }
                """)
                
                await asyncio.sleep(2) # รอให้ตารางกาง

                # 🔽 กางรายละเอียด (ถ้ามี)
                await page.evaluate("""
                    () => {
                        document.querySelectorAll('button').forEach(btn => {
                            if (btn.textContent.includes('ดูรายละเอียด')) btn.click();
                        });
                    }
                """)
                
                await asyncio.sleep(2)
                content = await page.inner_text("body")
                
                file_path = os.path.join(output_dir, f"score_{code}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ สำเร็จ! ข้อมูลรหัส {code} เข้าโฟลเดอร์แล้ว")
                
            except Exception as e:
                print(f"⚠️ รหัส {code} ช้าเกินไป ข้ามไปก่อน: {str(e)[:50]}")

        await browser.close()
        print("\n🏁 จบภารกิจจู่โจมสายฟ้าแลบ!")

if __name__ == "__main__":
    asyncio.run(fast_js_striker())