import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tax_project.settings')
django.setup()
from django.contrib.auth.models import User
from tax_assistant.models import Transaction, ChatSession, Category
from tax_assistant.views import get_transaction_tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

user = User.objects.first()
Category.objects.get_or_create(type='EXPENSE', defaults={'name': 'EXPENSE'})

record_tool = get_transaction_tool(user)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools([record_tool])

messages = [
    SystemMessage(content="You are a helpful assistant. Use record_transaction to save expenses."),
    HumanMessage(content="ช่วยบันทึกข้อมูลจากสลิปนี้ให้หน่อย \n[ข้อมูลจากสลิปที่ผู้ใช้อัปโหลด: ร้านข้าวแกงอินเตอร์ 12 บาท 2026-07-07]")
]

ai_msg = llm_with_tools.invoke(messages)
print("First AI Msg tool calls:", getattr(ai_msg, 'tool_calls', None))
print("First AI Msg content:", ai_msg.content)

if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
    messages.append(ai_msg)
    for tool_call in ai_msg.tool_calls:
        if tool_call["name"] == "record_transaction":
            tool_res = record_tool.invoke(tool_call["args"])
            messages.append(ToolMessage(content=tool_res, tool_call_id=tool_call["id"]))
    
    final_msg = llm_with_tools.invoke(messages)
    print("Final Msg content:", final_msg.content)
    print("Is final content list?", isinstance(final_msg.content, list))

print("Transactions with 12:", Transaction.objects.filter(amount=12).count())
