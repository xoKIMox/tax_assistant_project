# Thai Tax & Personal Finance Assistant (AI-Powered)

โปรแกรมผู้ช่วยจัดการการเงินส่วนบุคคลและคำนวณภาษีอากรส่วนบุคคลของไทย ขับเคลื่อนด้วย AI Agent และระบบสแกนใบเสร็จด้วยคอมพิวเตอร์วิทัศน์ (OCR)

โปรเจกต์นี้พัฒนาขึ้นด้วยเฟรมเวิร์ก Django (Python) ร่วมกับ LangChain (Gemini 2.5 Flash), EasyOCR และ HTMX เพื่อให้ระบบการใช้งานเป็นไปอย่างรวดเร็วและลื่นไหล (SPA-like experience)

---

## 🌟 Key Features (ฟีเจอร์หลัก)

1. **AI Tax Expert (Agentic AI Chatbot):**
   * สนทนาโต้ตอบวิเคราะห์สถานะการเงินกับผู้ใช้อย่างเป็นกันเอง
   * รองรับ **Tool Calling (Function Calling)** เพื่อบันทึกข้อมูลธุรกรรมใหม่ (`record_transaction`) หรือวาดกราฟวิเคราะห์ทางการเงิน (`generate_financial_chart`) ตามความต้องการของผู้ใช้งานโดยอัตโนมัติ
   * ป้องกันปัญหาการบันทึกข้อมูลซ้ำซ้อนผ่าน Failsafe Validation ในฝั่งเซิร์ฟเวอร์

2. **AI-Powered Slip/Receipt OCR:**
   * สแกนใบเสร็จหรือสลิปเพื่อแกะตัวหนังสือด้วย **EasyOCR** (รองรับทั้งภาษาไทยและอังกฤษ)
   * ส่งข้อมูลดิบที่ได้ไปให้ **Gemini 2.5 Flash** ช่วยจัดโครงสร้างข้อมูลแบบมีระบบ (สกัดออกมาเป็น วันที่, จำนวนเงิน, ร้านค้า/ผู้รับ, หมวดหมู่) และบันทึกลงฐานข้อมูลทันที

3. **Thai Personal Income Tax Engine:**
   * ระบบคำนวณภาษีเงินได้บุคคลธรรมดาของไทย (คำนวณแบบขั้นบันไดจริง)
   * รองรับการคำนวณลดหย่อนตามเงื่อนไข:
     * สถานะการสมรส (โสด / สมรสมีรายได้ / สมรสไม่มีรายได้)
     * จำนวนบุตร (ที่เกิดก่อน/หลังปี 2561)
     * ค่าอุปการะบิดามารดา และผู้พิการ
     * การหักค่าใช้จ่ายแบบเหมา 50% (สูงสุดไม่เกิน 100,000 บาท)

4. **Dynamic Data Visualizations:**
   * แสดงสรุปสถิติรายรับ-รายจ่ายผ่านกราฟแท่งและกราฟวงกลมแยกหมวดหมู่ (Bar/Pie charts) ภายในห้องแชทด้วยการประมวลผลของ AI

5. **Community Forum:**
   * พื้นที่สำหรับแชร์เคล็ดลับประหยัดภาษีและพูดคุยเรื่องการเงิน
   * รองรับการตั้งโพสต์, ตอบคอมเมนต์, และการกดไลก์แบบเรียลไทม์ผ่าน **HTMX** (ไม่ต้องโหลดหน้าเว็บใหม่)

---

## 🛠️ Tech Stack (เทคโนโลยีที่ใช้)

* **Backend:** Django (Python), Django ORM, Django Templates
* **Database:** SQLite3 (สามารถย้ายไป PostgreSQL ได้ง่าย)
* **AI & LLM:** LangChain, Google Gemini API (`gemini-2.5-flash`)
* **Computer Vision / OCR:** EasyOCR (PyTorch-based)
* **Frontend:** HTMX (สำหรับ Asynchronous UI), Vanilla CSS, HTML5

---

## 🚀 How to Run Locally (วิธีเปิดใช้งานในเครื่องคอมพิวเตอร์ของคุณ)

### 1. โคลนโปรเจกต์ (Clone Project)
```bash
git clone <URL_ของ_Github_Repository_ของคุณ>
cd tax_assistant_project
```

### 2. สร้างและใช้งาน Virtual Environment
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables
1. คัดลอกไฟล์ `.env.example` เป็น `.env`
   ```bash
   cp .env.example .env
   ```
2. เปิดไฟล์ `.env` แล้วระบุ API Key ของ Google Gemini ลงไป:
   ```env
   GOOGLE_API_KEY=AIzaSy... (คีย์ของคุณ)
   ```

### 5. ทำการ Run Migration เพื่อสร้างฐานข้อมูล
```bash
python manage.py migrate
```

### 6. สร้างบัญชีผู้ใช้เริ่มต้น หรือ Superuser
```bash
python manage.py createsuperuser
```

### 7. สตาร์ทเว็บเซิร์ฟเวอร์
```bash
python manage.py runserver
```
เปิดบราวเซอร์ไปที่ `http://127.0.0.1:8000/` เพื่อเข้าใช้งานระบบ

---

## 📁 Project Structure (โครงสร้างโปรเจกต์ที่สำคัญ)

```text
tax_assistant_project/
│
├── tax_project/              # ส่วนตั้งค่าโปรเจกต์หลักของ Django (settings, urls, wsgi)
├── tax_assistant/            # แอปพลิเคชันผู้ช่วยภาษี
│   ├── models.py             # โมเดลฐานข้อมูล (UserProfile, Transaction, Chats, Posts)
│   ├── views.py              # Logic การทำงาน, การเชื่อมโยง AI Agent (LangChain) และ OCR (EasyOCR)
│   ├── services.py           # ฟังก์ชันคำนวณภาษีเงินได้บุคคลธรรมดาของไทย
│   ├── forms.py              # ฟอร์มลงทะเบียนธุรกรรมและโปรไฟล์ผู้ใช้
│   └── templates/            # หน้าเว็บเพจและส่วนประกอบ Dynamic Components (HTMX)
│
├── .gitignore                # ป้องกันการอัปโหลดไฟล์ขยะและคีย์ส่วนตัวขึ้น GitHub
├── .env.example              # ตัวอย่างการตั้งค่า API Key
└── requirements.txt          # รายการ Library ทั้งหมดที่ต้องติดตั้ง
```
