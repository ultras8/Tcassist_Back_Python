import asyncio
import os  # เพิ่มตัวนี้เพื่อจัดการโฟลเดอร์
from playwright.async_api import async_playwright

async def js_striker():
    print("🧨 เริ่มภารกิจระเบิดปุ่ม: ใช้ JS Injection คลิกตรงจุด!")
    
    # --- 📁 ขั้นตอนเตรียมโฟลเดอร์ ---
    folder_name = "all_scores"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"📁 สร้างโฟลเดอร์ใหม่: {folder_name}")
    # ---------------------------

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        target_codes = ["10010121300001A", "10010121300501A", "10010121300601A"]
        
        for code in target_codes:
            url = f"https://course.mytcas.com/programs/{code}"
            print(f"\n🚀 เข้าสู่เป้าหมาย: {url}")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(5)

                # 🖱️ คลิกเลข 3
                print("🖱️ กำลังสั่ง JavaScript คลิกเลข 3...")
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

                # 🎯 กาง Admission
                print("⏳ รอให้ปุ่ม Admission ของรอบ 3 ปรากฏ...")
                admission_selector = '#r3 span:text-is("Admission"), #r3 h2 span'
                
                try:
                    target_btn = page.locator(admission_selector).first
                    await target_btn.wait_for(state="attached", timeout=10000) 
                    print("🎯 เจอ Admission รอบ 3 แล้ว! กำลังกาง...")
                    await target_btn.scroll_into_view_if_needed()
                    await target_btn.evaluate("el => el.click()")
                except Exception:
                    print(f"⚠️ แผนแรกพลาด ลองกวาดทุกลูกศร...")
                    await page.evaluate("""() => {
                        const r3Zone = document.getElementById('r3');
                        if (r3Zone) {
                            const arrows = r3Zone.querySelectorAll('button, .v-expansion-panel-header, .v-icon');
                            arrows.forEach(el => el.click());
                        }
                    }""")

                print("⏳ กางแล้ว! รอข้อมูลเกณฑ์คะแนนไหลออก...")
                await asyncio.sleep(10) # เพิ่มเวลาอีกนิดให้ชัวร์ว่าโหลดครบ

                # 💾 บันทึกไฟล์ลงในโฟลเดอร์ all_scores
                content = await page.inner_text("body")
                
                # ระบุ Path ให้ไปอยู่ที่ folder/filename
                file_path = os.path.join(folder_name, f"unlocked_score_{code}.txt")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"✅ สำเร็จ! เขียนไฟล์ลงใน: {file_path}")
                
            except Exception as e:
                print(f"❌ พลาดรหัส {code}: {str(e)[:50]}")

        await browser.close()
        print(f"\n🏁 จบภารกิจ! ไฟล์ทั้งหมดอยู่ในโฟลเดอร์ '{folder_name}' แล้วค่ะ")

if __name__ == "__main__":
    asyncio.run(js_striker())