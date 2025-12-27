import asyncio
import os
from playwright.async_api import async_playwright

async def js_striker():
    print("เริ่มกวาดข้อมูล TCAS")
    
    folder_name = "all_scores"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # --- 📄 อ่านรหัสจากไฟล์ mega_unis_links.txt ---
    # สมมติในไฟล์เป็นลิ้งก์แบบ https://course.mytcas.com/programs/10010121300001A
    target_codes = []
    try:
        with open("mega_unis_links.txt", "r", encoding="utf-8") as f:
            for line in f:
                code = line.strip().split('/')[-1] # ดึงตัวหลังสุดมา
                if code:
                    target_codes.append(code)
        print(f"อ่านรหัสทั้งหมดได้: {len(target_codes)} รายการ")
    except FileNotFoundError:
        print("ไม่พบไฟล์ mega_unis_links.txt")
        return

    async with async_playwright() as p:
        # เปิด headless=True จะทำงานเร็วกว่าและไม่รบกวนหน้าจอ
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(user_agent="Mozilla/5.0 ...")
        page = await context.new_page()
        
        for index, code in enumerate(target_codes):
            file_path = os.path.join(folder_name, f"unlocked_score_{code}.txt")
            
            # ระบบข้ามไฟล์ที่เคยโหลดแล้ว (Resume)
            if os.path.exists(file_path):
                # print(f"ข้าม {code} (โหลดไปแล้ว)")
                continue

            url = f"https://course.mytcas.com/programs/{code}"
            print(f"[{index+1}/{len(target_codes)}] กำลังกวาด: {code}")
            
            try:
                # ลด timeout เหลือ 30 วินาทีเพื่อความไว
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2) # รอโครงสร้างหน้าเว็บนิดนึง

                # คลิกเลข 3
                # print("กำลังสั่ง JavaScript คลิกเลข 3")
                await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a'));
                        const btn3 = links.find(el => el.textContent.includes('3'));
                        if (btn3) { btn3.click(); return; }
                        const xpathResult = document.evaluate('//*[@id="root"]/main/div[2]/nav/a[4]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const node = xpathResult.singleNodeValue;
                        if (node) { node.click(); }
                    }
                """)
                await asyncio.sleep(3)

                # กาง Admission รอบ 3
                admission_selector = '#r3 span:text-is("Admission"), #r3 h2 span'
                
                try:
                    target_btn = page.locator(admission_selector).first
                    await target_btn.wait_for(state="attached", timeout=10000) 
                    # print("เจอ Admission รอบ 3 แล้ว! กำลังกาง")
                    await target_btn.scroll_into_view_if_needed()
                    await target_btn.evaluate("el => el.click()")
                except Exception:
                    print(f"แผนแรกพลาด ลองกวาดทุกลูกศร")
                    await page.evaluate("""() => {
                        const r3Zone = document.getElementById('r3');
                        if (r3Zone) {
                            const arrows = r3Zone.querySelectorAll('button, .v-expansion-panel-header, .v-icon');
                            arrows.forEach(el => el.click());
                        }
                    }""")
                
                await asyncio.sleep(3) # รอให้ Text กางออกมา

                # บันทึกเฉพาะข้อความ
                content = await page.inner_text("body")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
            except Exception as e:
                print(f"พลาด {code}: {str(e)[:30]}")
                continue # ไปตัวต่อไปทันที

        await browser.close()
        print(f"\nจบภารกิจ! ข้อมูลชุดอยู่ที่ '{folder_name}'")

if __name__ == "__main__":
    asyncio.run(js_striker())
