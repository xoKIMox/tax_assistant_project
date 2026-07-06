# 🚀 Document: Thai Tax & Personal Finance Assistant

เอกสารฉบับนี้จัดทำขึ้นเพื่อใช้เป็นข้อมูลประกอบ Portfolio สำหรับสายงาน Backend Developer และ Software Tester โดยอ้างอิงจากโครงสร้างและ Source Code ของโปรเจกต์ **Thai Tax & Personal Finance Assistant** ตามหัวข้อเจาะลึก (Deep-Dive Questionnaire)

---

## 1. Project Overview & Objectives (ภาพรวมและเป้าหมาย)

* **Problem Statement:** 
  บุคคลทั่วไปมักประสบปัญหาความยุ่งยากในการบันทึกรายรับ-รายจ่าย และความซับซ้อนของการคำนวณภาษีเงินได้บุคคลธรรมดาของไทย (เช่น เงื่อนไขการลดหย่อนภาษีต่างๆ) นอกจากนี้การจัดการใบเสร็จหรือสลิปการโอนเงินจำนวนมากมักทำให้เกิดความสับสนและใช้เวลาเยอะในการจัดทำบัญชี
* **Core Value:** 
  ระบบผู้ช่วย AI ที่สามารถวิเคราะห์ข้อมูลทางการเงินแบบเรียลไทม์ พร้อมระบบ **AI-Powered OCR** สำหรับสแกนใบเสร็จอัตโนมัติ และ **Thai Personal Income Tax Engine** สำหรับคำนวณยอดภาษีขั้นบันไดและลดหย่อนภาษีได้ทันที
* **Target Users:** 
  ผู้มีรายได้และวัยทำงานในประเทศไทยที่ต้องการตัวช่วยจัดการภาษีและวางแผนการเงินส่วนบุคคลให้มีประสิทธิภาพมากยิ่งขึ้น

## 2. System Architecture & Tech Stack (สถาปัตยกรรมและเทคโนโลยี)

* **Architecture Diagram (Text Description):**
  1. **Client-Side:** ผู้ใช้งานโต้ตอบผ่านเบราว์เซอร์ โดยใช้ **HTMX** ในการส่ง Request แบบ Asynchronous (AJAX) ทำให้ UI โต้ตอบได้ทันทีโดยไม่ต้องโหลดหน้าเว็บใหม่ (เช่น การกดไลก์, ส่งข้อความแชท)
  2. **Backend Engine:** รับ Request เข้ามาผ่าน **Django** วิเคราะห์ Logic จัดการเซสชันผู้ใช้ และทำงานร่วมกับ **EasyOCR** ในการประมวลผลรูปภาพใบเสร็จ
  3. **External API Layer:** มีการเชื่อมต่อไปยัง **Google Gemini 2.5 Flash** ผ่าน **LangChain** เพื่อทำ Agentic AI ตอบสนองต่อแชทผู้ใช้ ตัดสินใจใช้ Tools และจัดรูปแบบข้อความดิบ (Raw Text) จาก OCR ให้เป็นโครงสร้างข้อมูล
  4. **Database:** ข้อมูลถูกจัดเก็บลง **SQLite3** (พร้อมอัปสเกลเป็น PostgreSQL) ผ่าน Django ORM
* **Tech Stack Justification:**
  * **Django:** เลือกใช้เนื่องจากมี ORM ที่ทรงพลัง มีระบบ Authentication ในตัว และเป็น Python Framework ซึ่งสามารถผนวกโค้ดเข้ากับเครื่องมือ AI (LangChain) และ Computer Vision (EasyOCR) ได้อย่างลื่นไหล
  * **HTMX:** เข้ามาเติมเต็มความเป็น SPA (Single Page Application) ในฟีเจอร์แชทและกระดานพูดคุย ลดความซับซ้อนของ Frontend ลดการใช้ JavaScript ลงได้อย่างมาก
  * **SQLite3:** เหมาะสำหรับโปรเจกต์ในระยะเริ่มต้น (MVP) มีน้ำหนักเบาและเปลี่ยนไปใช้ PostgreSQL ได้ทันทีเมื่อขยายระบบ

## 3. Database Schema & Data Management (การจัดการฐานข้อมูล)

* **ER Diagram / Schema Design:** ตารางข้อมูลหลัก (Core Tables) ได้แก่
  * `User`: ใช้จัดการสิทธิ์การเข้าถึง (Authentication)
  * `UserProfile` (One-to-One กับ User): เก็บข้อมูลประกอบการลดหย่อนภาษี เช่น `marital_status`, `children_before_2018`, `monthly_base_salary`
  * `Category`: เก็บหมวดหมู่ 3 ประเภท (`Income`, `Expense`, `Deduction`)
  * `Transaction`: เก็บบันทึกรายรับรายจ่าย (ยอดเงิน, วันที่, รูปสลิป) ผูกแบบ Foreign Key กับ `User` และ `Category`
  * `ChatSession` & `ChatMessage`: เก็บประวัติการสนทนาระหว่าง User และ AI 
* **Data Handling:** 
  ข้อมูลที่เกิดจากการสแกนใบเสร็จผ่าน `EasyOCR` จะเป็นชุดข้อความดิบ ระบบจะทำการส่งข้อความนี้ไปหา LLM ทันที เพื่อสกัดข้อมูลเฉพาะสิ่งที่สำคัญ ได้แก่ Date, Amount, Payee, และ Category โดยคืนค่ากลับมาในรูปแบบ String Comma-separated และบันทึกลงฐานข้อมูล

## 4. API Integration & AI Agent (การเชื่อมต่อและปัญญาประดิษฐ์)

* **External APIs:**
  * **Google Gemini 2.5 Flash API** ผ่านไลบรารี LangChain 
* **Request/Response Cycle:** 
  เมื่อผู้ใช้ส่งข้อความ หรือรูปภาพ ระบบ Backend จะส่งชุดข้อความรวม (System Prompt + Chat History + OCR Context) ไปยัง Gemini API เพื่อให้ LLM ประเมินสถานการณ์ หากเกิด Error ระบบมี `try-except` คอยดักจับและตอบกลับผู้ใช้อย่างสุภาพ (เช่น `ขออภัยครับ ระบบเกิดข้อผิดพลาด: ...`)
* **Agentic AI / Tool Calling:**
  ใน `views.py` ได้มีการผูก Tool เข้ากับ Agent (`llm.bind_tools(tools)`) ดังนี้:
  1. `record_transaction`: เมื่อผู้ใช้พิมพ์คำสั่งเช่น "กินข้าว 50 บาท" AI จะเรียก Tool นี้เพื่อบันทึกข้อมูลเข้า DB
  2. `generate_financial_chart`: เมื่อผู้ใช้ต้องการขอดู กราฟสรุปรายจ่าย AI จะตอบสนองและแสดงผลกราฟในแชท
  *กระบวนการตัดสินใจ (Reasoning):* AI จะพิจารณาจากบริบทและ Instruction ว่าผู้ใช้ต้องการ "บันทึกข้อมูล" หรือ "สอบถามสถานะ" ก่อนเลือกใช้ Tool

## 5. Complex Logic & Algorithms (ความซับซ้อนของระบบ)

* **Core Algorithm:** การคำนวณภาษีเงินได้บุคคลธรรมดาใน `services.py` (`calculate_tax_summary`)
  * *ความซับซ้อน:* ต้องทำการแยกประเภท `Transaction` (Income vs Expense) และนำ Income มาหักค่าใช้จ่ายเหมา 50% (แต่ไม่เกิน 100,000 บาท) จากนั้นนำมาหักค่าลดหย่อนส่วนตัวพื้นฐาน 60,000 บาท + ค่าลดหย่อนพิเศษ (Deductible) ก่อนนำไปเข้าสมการขั้นบันได 5% สำหรับเงินได้สุทธิส่วนที่เกิน 150,000 บาท
* **Asynchronous Processing:** 
  ระบบใช้งาน HTMX ในส่วนของการแชทแบบเรียลไทม์ และระบบไลก์/คอมเมนต์ของ Community (`community_feed.html`) ซึ่งจะรับค่า HTML Partial (เช่น `_chat_message.html` หรือ `_like_button.html`) มาเรนเดอร์แทนที่ (Swap) บน DOM ช่วยให้ไม่ต้องรีเฟรชทั้งหน้า

## 6. Testing, QA & Debugging (การทดสอบและแก้ปัญหา)

* **Edge Cases & Error Handling:**
  * **Failsafe การบันทึกข้อมูลซ้ำซ้อน:** ป้องกันกรณีที่ผู้ใช้สั่ง AI ด้วยคำพูดกำกวม แล้ว AI นำ "ยอดเงินคงเหลือ (Net Balance)" ใน Context กลับมาบันทึกเป็นรายรับรายการใหม่ ระบบมีการเขียนดักใน Tool (`record_transaction`) หากยอดเงินเท่ากับยอด Gross Income หรือ Net Balance ให้ตีกลับเป็นข้อความแจ้งเตือน (Reject) ทันที
  * **OCR ความแม่นยำต่ำ:** หากอัปโหลดรูปที่ EasyOCR อ่านไม่ออก หรือ Gemini จัดรูปแบบผิดพลาด ระบบมี `try-except` ใน View `upload_receipt_view` สำหรับกำหนดค่า Fallback เช่น `Amount=0, Category="EXPENSE"` เพื่อป้องกัน App Crash
* **Systematic Debugging:** 
  ปัญหาความล่าช้าในการสแกนใบเสร็จด้วย EasyOCR ถูกจำกัดวงด้วยการจำกัดพารามิเตอร์การอ่านข้อความ (`detail=0`) เพื่อคืนค่าเป็น list ข้อความดิบๆ และผลักภาระการประมวลผลเชิงภาษา (Semantics) ให้กับ LLM ที่มีความรวดเร็วกว่า

## 7. Version Control & Workflow (กระบวนการทำงาน)

* **Git/GitHub Workflow:**
  มีการจัดโครงสร้างแบบโมดูล (Django Apps) การแบ่งแยกไฟล์ `.env` ไม่ให้นำคีย์ลับ (API Key) ขึ้นไปบนระบบ Version Control ควบคุมผ่าน `.gitignore` อย่างเคร่งครัด
* **Project Structuring:**
  แบ่งแอป `tax_assistant` ออกจาก `tax_project` อย่างชัดเจน เพื่อให้ซอร์สโค้ดในเรื่องของ AI และ Business Logic แยกออกจาก Configuration ของระบบโดยรวม

## 8. Outcomes & Actionable Insights (ผลลัพธ์และการนำไปใช้)

* **Results:** 
  ผู้ใช้สามารถอัปโหลดใบเสร็จและพูดคุยกับผู้ช่วย AI ผ่านทางแชทเพื่อบันทึกธุรกรรมโดยแทบไม่ต้องกรอกฟอร์มเองด้วยมือ ลดเวลาและลด Human Error ในการทำบัญชี พร้อมสามารถดูผลลัพธ์ประมาณการภาษีแบบ Real-time
* **Future Scaling:**
  หากระบบนี้เปิดให้คนใช้งานจริง 10,000 คน จำเป็นต้องพัฒนาในส่วนของ:
  1. **Background Tasks (Celery + Redis):** ย้ายการทำงานของ **EasyOCR** และ LLM Call ออกจากการบล็อก HTTP Request (Synchronous View) เพื่อป้องกันปัญหา Server Timeout
  2. **Database Migration:** ย้ายจาก SQLite3 ไปสู่ PostgreSQL หรือ MySQL เพื่อรองรับ Concurrent Connections ของผู้ใช้หลักหมื่น
  3. **Caching:** นำการคำนวณ `calculate_tax_summary` ไปทำระบบแคช หากไม่มีการเปลี่ยนแปลง Transaction ในรอบวัน ก็ไม่ต้องประมวลผลใหม่
