import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tax_project.settings')
django.setup()
from django.contrib.auth.models import User
from tax_assistant.models import ChatSession
from tax_assistant.views import get_transaction_tool, get_chart_tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
import datetime

user = User.objects.first()
session = ChatSession.objects.get(user=user, id=7) # Main chat for user
record_tool = get_transaction_tool(user)
chart_tool = get_chart_tool()

llm = ChatOllama(model="qwen2.5-coder", temperature=0)
llm_with_tools = llm.bind_tools([record_tool, chart_tool])

today = datetime.date.today().strftime('%Y-%m-%d')
system_prompt = f"""คุณคือผู้เชี่ยวชาญด้านภาษีอากรและบัญชีส่วนบุคคลของประเทศไทย (Tax Expert) 
หน้าที่ของคุณคือให้คำแนะนำเกี่ยวกับการคำนวณภาษี การลดหย่อนภาษี และการจัดการบัญชีรายรับ-รายจ่าย 
คุณกำลังคุยกับผู้ใช้ชื่อ "admin" โปรดเรียกชื่อเล่นของผู้ใช้ในการสนทนาเพื่อให้ดูเป็นกันเองและพรีเมียม

กฎการตอบคำถาม:
- หากผู้ใช้ถามถึง "สถานะการเงิน", "ยอดคงเหลือ", "สรุปยอด", หรือ "ปัจจุบันเป็นยังไง": ให้คุณนำข้อมูลจาก "ข้อมูลสรุปทางการเงินของผู้ใช้ ณ ปัจจุบัน" ด้านล่างนี้ไปตอบผู้ใช้โดยตรง **ห้ามเรียกใช้เครื่องมือใดๆ ทั้งสิ้น**
- หากผู้ใช้สั่งให้ "บันทึก", "เพิ่ม", "จ่าย", หรือ "ได้รับ" (เช่น "กินข้าว 50", "ได้เงินเดือน", หรือมีสลิป): คุณ **ต้อง** เรียกใช้เครื่องมือ `record_transaction` เสมอ ห้ามตอบว่าบันทึกแล้วโดยไม่ได้เรียกใช้เครื่องมือเด็ดขาด
- หากผู้ใช้ต้องการดู "กราฟ", "รายงานสรุปแบบภาพ", หรือ "สถิติ": ให้เรียกใช้เครื่องมือ `generate_financial_chart`
- หากเป็นคำถามทั่วไปที่ไม่เกี่ยวกับการเงิน: ให้ปฏิเสธอย่างสุภาพ

วันนี้คือวันที่ {today}

ข้อมูลสรุปทางการเงินของผู้ใช้ ณ ปัจจุบัน:
- รายรับรวม (Gross Income): 10000 บาท
- รายจ่ายรวม (Total Expenses): 0 บาท
- ยอดเงินคงเหลือ (Net Balance): 10000 บาท
- ประมาณการภาษีที่ต้องจ่าย: 0 บาท
"""

messages = [SystemMessage(content=system_prompt)]
# Only get the last 5 messages to avoid overflow
for msg in list(session.messages.all().order_by('created_at'))[-5:]:
    if msg.role == 'user':
        messages.append(HumanMessage(content=msg.content))
    else:
        messages.append(AIMessage(content=msg.content))

# Add the user's latest query
messages.append(HumanMessage(content="ช่วยสรุป ข้อมูล"))

try:
    res = llm_with_tools.invoke(messages)
    print("Content:", res.content)
    print("Tool calls:", getattr(res, 'tool_calls', None))
except Exception as e:
    print("Error:", e)
