import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tax_project.settings')
django.setup()
from django.contrib.auth.models import User
from tax_assistant.views import get_transaction_tool, get_chart_tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

user = User.objects.first()
record_tool = get_transaction_tool(user)
chart_tool = get_chart_tool()

llm = ChatOllama(model="qwen2.5-coder", temperature=0)
llm_with_tools = llm.bind_tools([record_tool, chart_tool])

messages = [
    SystemMessage(content="ข้อมูลสรุปทางการเงินของผู้ใช้: ยอดเงิน 5000 บาท"),
    HumanMessage(content="ช่วยสรุป ข้อมูล")
]

try:
    res = llm_with_tools.invoke(messages)
    print("Content:", res.content)
    print("Tool calls:", getattr(res, 'tool_calls', None))
except Exception as e:
    print("Error:", e)
