import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tax_project.settings')
django.setup()
from django.contrib.auth.models import User
from tax_assistant.models import ChatMessage, ChatSession, Transaction
from tax_assistant.views import get_transaction_tool
from django.core.files.uploadedfile import SimpleUploadedFile

user = User.objects.first()
session = ChatSession.objects.first()

receipt_file = SimpleUploadedFile("receipt.jpg", b"file_content", content_type="image/jpeg")

user_msg_obj = ChatMessage.objects.create(
    session=session, 
    role='user', 
    content="[อัปโหลดรูปภาพใบเสร็จ]",
    image=receipt_file
)
receipt_file.seek(0)
image_bytes = receipt_file.read()

record_tool = get_transaction_tool(user, receipt_file)
try:
    res = record_tool.invoke({"amount": 12.0, "date": "2026-07-07", "payee": "Test", "category_type": "EXPENSE"})
    print("Tool result:", res)
    print("Transaction count with amount 12:", Transaction.objects.filter(amount=12).count())
except Exception as e:
    print("Exception:", e)
