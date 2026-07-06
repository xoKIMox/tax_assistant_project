from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from .models import Transaction, ChatSession, ChatMessage, Category, UserProfile, CommunityPost, CommunityComment
from .forms import UserProfileForm, TransactionForm, PostForm, CommentForm

@login_required
def community_feed_view(request):
    posts = CommunityPost.objects.all().order_by('-created_at')
    return render(request, 'tax_assistant/community_feed.html', {'posts': posts})

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('community_feed')
    else:
        form = PostForm()
    return render(request, 'tax_assistant/create_post.html', {'form': form})

@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(CommunityPost, pk=pk)
    comments = post.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.id)
    else:
        form = CommentForm()
        
    is_liked = request.user in post.likes.all()
    like_count = post.likes.count()
        
    return render(request, 'tax_assistant/post_detail.html', {
        'post': post, 
        'comments': comments, 
        'form': form,
        'is_liked': is_liked,
        'like_count': like_count
    })

@login_required
def like_post_view(request, pk):
    post = get_object_or_404(CommunityPost, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    # Return just the heart button HTML for HTMX swapping
    is_liked = request.user in post.likes.all()
    like_count = post.likes.count()
    return render(request, 'tax_assistant/_like_button.html', {'post': post, 'is_liked': is_liked, 'like_count': like_count})

@login_required
def edit_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_detail', pk=transaction.id)
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'tax_assistant/edit_transaction.html', {'form': form, 't': transaction})

@login_required
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')
    return redirect('transaction_detail', pk=transaction.id)



@login_required
def profile_settings_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                return render(request, 'tax_assistant/_profile_form.html', {'form': form, 'success': True})
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'tax_assistant/profile_settings.html', {'form': form})
from .services import calculate_tax_summary
import easyocr
import datetime
from langchain_ollama import ChatOllama
# from langchain_google_genai import ChatGoogleGenerativeAI
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

# โหลดโมเดลอ่านตัวหนังสือ (OCR)
reader = easyocr.Reader(['th', 'en'])

def get_transaction_tool(user, receipt_image=None):
    @tool
    def record_transaction(amount: float, date: str, payee: str, category_type: str) -> str:
        """🚨 คำเตือนสำคัญ: เครื่องมือนี้ใช้สำหรับ "เพิ่มรายการบัญชีใหม่" เท่านั้น! 
        ห้ามใช้เครื่องมือนี้หากผู้ใช้แค่ถามถึง สถานะการเงิน, ยอดคงเหลือ, หรือสรุปยอด
        ห้ามนำตัวเลขจากข้อมูลสรุปทางการเงิน (Gross Income, Net Balance) มาบันทึกเป็นรายการใหม่เด็ดขาด!

        ใช้เฉพาะเมื่อผู้ใช้บอกว่า "ซื้อ...", "จ่าย...", "ได้รับเงิน...", หรือมีการอัปโหลดรูปสลิปเท่านั้น
        
        Args:
            amount: จำนวนเงิน (ตัวเลขเท่านั้น ห้ามเอามาจาก Net Balance)
            date: วันที่รูปแบบ YYYY-MM-DD (เช่น 2024-01-01) 
            payee: รายละเอียด, ชื่อรายการ หรือชื่อผู้รับ/ผู้จ่ายเงิน
            category_type: ประเภทของรายการ ต้องเป็น 1 ใน 3 ค่านี้เท่านั้น: 'INCOME', 'EXPENSE', หรือ 'DEDUCTIBLE'
        """
        cat, _ = Category.objects.get_or_create(type=category_type, defaults={'name': category_type})
        
        # Failsafe: Prevent AI from recording the summary as a new transaction
        from .services import calculate_tax_summary
        current_summary = calculate_tax_summary(user)
        if float(amount) == float(current_summary['net_balance']) or float(amount) == float(current_summary['gross_income']):
            return "ERROR: You tried to record the Net Balance or Gross Income as a new transaction! Do NOT do this. Just answer the user's question without recording."
            
        new_transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            date=date,
            payee=payee,
            category=cat,
            receipt_image=receipt_image
        )
        return f"บันทึก {payee} จำนวน {amount} บาท ประเภท {category_type} เมื่อวันที่ {date} สำเร็จแล้ว"
    
    return record_transaction

def get_chart_tool():
    @tool
    def generate_financial_chart(chart_type: str) -> str:
        """ใช้สำหรับขอให้ระบบสร้างกราฟแสดงข้อมูลทางการเงิน 
        chart_type: ประเภทของกราฟ ('expense_pie' สำหรับสัดส่วนรายจ่าย, 'income_expense_bar' สำหรับเปรียบเทียบรายรับรายจ่าย)
        """
        return f"CHART_REQUESTED:{chart_type}"
    
    return generate_financial_chart

@login_required
def dashboard_view(request):
    summary = calculate_tax_summary(request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-id')[:10]
    return render(request, 'tax_assistant/dashboard.html', {
        'summary': summary,
        'transactions': transactions
    })

@login_required
def upload_receipt_view(request):
    if request.method == "POST" and request.FILES.get('receipt'):
        image_bytes = request.FILES['receipt'].read()
        
        # 1. อ่านรูปด้วย EasyOCR
        extracted_text = " ".join(reader.readtext(image_bytes, detail=0))

        # 2. ให้ Ollama จัดหมวดหมู่
        llm = ChatOllama(model="qwen2.5-coder", temperature=0)
        messages = [
            SystemMessage(content="Extract Date, Amount, Payee, Category(INCOME/EXPENSE/DEDUCTIBLE). Format: Date,Amount,Payee,Category"),
            HumanMessage(content=extracted_text)
        ]
        
        try:
            res = llm.invoke(messages).content.split(',')
            date, amount, payee, category = res[0], res[1], res[2], res[3]
        except:
            date, amount, payee, category = "N/A", "0", "N/A", "EXPENSE"

        return render(request, 'tax_assistant/_ocr_preview.html', {
            'date': date, 'amount': amount, 'payee': payee, 'category': category
        })
    return HttpResponse("Error")

@login_required
def chat_api_view(request, session_id=None):
    if request.method == "POST":
        user_message = request.POST.get('message', '')
        receipt_file = request.FILES.get('receipt')
        
        # 1. Get session
        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session, created = ChatSession.objects.get_or_create(user=request.user, title="Main Chat")
        
        # 2. Handle Receipt Upload (AI OCR)
        extracted_context = ""
        if receipt_file:
            # บันทึกรูปใน ChatMessage
            user_msg_obj = ChatMessage.objects.create(
                session=session, 
                role='user', 
                content="[อัปโหลดรูปภาพใบเสร็จ]",
                image=receipt_file
            )
            
            # อ่านข้อความจากรูป (ใช้ .open() เพื่อรีเซ็ต pointer ถ้าจำเป็น)
            receipt_file.seek(0)
            image_bytes = receipt_file.read()
            extracted_text = " ".join(reader.readtext(image_bytes, detail=0))
            extracted_context = f"\n[ข้อมูลจากสลิปที่ผู้ใช้อัปโหลด: {extracted_text}]"
            
            if not user_message:
                user_message = "ช่วยบันทึกข้อมูลจากสลิปนี้ให้หน่อย"
        else:
            # บันทึกข้อความแชทปกติ
            if user_message:
                ChatMessage.objects.create(session=session, role='user', content=user_message)
        
        if not user_message and not receipt_file:
            return HttpResponse("")

        # 3. Prepare context and prompt
        summary = calculate_tax_summary(request.user)
        today = datetime.date.today().strftime('%Y-%m-%d')
        profile = getattr(request.user, 'profile', None)
        user_nickname = profile.nickname if profile and profile.nickname else request.user.username
        
        system_prompt = f"""คุณคือผู้เชี่ยวชาญด้านภาษีอากรและบัญชีส่วนบุคคลของประเทศไทย (Tax Expert) 
หน้าที่ของคุณคือให้คำแนะนำเกี่ยวกับการคำนวณภาษี การลดหย่อนภาษี และการจัดการบัญชีรายรับ-รายจ่าย 
คุณกำลังคุยกับผู้ใช้ชื่อ "{user_nickname}" โปรดเรียกชื่อเล่นของผู้ใช้ในการสนทนาเพื่อให้ดูเป็นกันเองและพรีเมียม

กฎการตอบคำถาม:
- หากผู้ใช้ถามถึง "สถานะการเงิน", "ยอดคงเหลือ", "สรุปยอด", หรือ "ปัจจุบันเป็นยังไง": ให้คุณนำข้อมูลจาก "ข้อมูลสรุปทางการเงินของผู้ใช้ ณ ปัจจุบัน" ด้านล่างนี้ไปตอบผู้ใช้โดยตรง **ห้ามเรียกใช้เครื่องมือใดๆ ทั้งสิ้น**
- หากผู้ใช้สั่งให้ "บันทึก", "เพิ่ม", "จ่าย", หรือ "ได้รับ" (เช่น "กินข้าว 50", "ได้เงินเดือน", หรือมีสลิป): คุณ **ต้อง** เรียกใช้เครื่องมือ `record_transaction` เสมอ ห้ามตอบว่าบันทึกแล้วโดยไม่ได้เรียกใช้เครื่องมือเด็ดขาด
- หากผู้ใช้ต้องการดู "กราฟ", "รายงานสรุปแบบภาพ", หรือ "สถิติ": ให้เรียกใช้เครื่องมือ `generate_financial_chart`
- หากเป็นคำถามทั่วไปที่ไม่เกี่ยวกับการเงิน: ให้ปฏิเสธอย่างสุภาพ

วันนี้คือวันที่ {today}

ข้อมูลสรุปทางการเงินของผู้ใช้ ณ ปัจจุบัน:
- รายรับรวม (Gross Income): {summary['gross_income']} บาท
- รายจ่ายรวม (Total Expenses): {summary['total_expenses']} บาท
- ยอดเงินคงเหลือ (Net Balance): {summary['net_balance']} บาท
- ประมาณการภาษีที่ต้องจ่าย: {summary['estimated_tax']} บาท
"""
        
        # 4. Build message history
        messages = [SystemMessage(content=system_prompt)]
        for msg in session.messages.all().order_by('created_at'):
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        # หากมีข้อมูล OCR ให้แนบเป็นข้อความล่าสุดเพื่อให้ AI ประมวลผล
        if extracted_context:
            messages.append(HumanMessage(content=f"{user_message} {extracted_context}"))
        
        # 5. Setup Tools and Invoke LLM
        record_tool = get_transaction_tool(request.user, receipt_file)
        chart_tool = get_chart_tool()
        tools = [record_tool, chart_tool]
        
        llm = ChatOllama(model="qwen2.5-coder", temperature=0)
        llm_with_tools = llm.bind_tools(tools)
        
        ui_component = None
        ui_data = None
        
        try:
            ai_msg = llm_with_tools.invoke(messages)
            
            # --- Ollama Fallback Parser ---
            if not getattr(ai_msg, 'tool_calls', None) and ai_msg.content:
                import json
                content_str = str(ai_msg.content).strip()
                if content_str.startswith('```json'):
                    content_str = content_str[7:]
                elif content_str.startswith('```'):
                    content_str = content_str[3:]
                if content_str.endswith('```'):
                    content_str = content_str[:-3]
                content_str = content_str.strip()
                
                try:
                    parsed = json.loads(content_str)
                    if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
                        ai_msg.tool_calls = [{
                            "name": parsed["name"],
                            "args": parsed["arguments"],
                            "id": "call_ollama_fallback"
                        }]
                except Exception:
                    pass
            # ------------------------------
            
            if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
                messages.append(ai_msg)
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "record_transaction":
                        tool_res = record_tool.invoke(tool_call["args"])
                        messages.append(ToolMessage(content=tool_res, tool_call_id=tool_call["id"]))
                    elif tool_call["name"] == "generate_financial_chart":
                        chart_type = tool_call["args"].get("chart_type")
                        ui_component = chart_type
                        
                        if chart_type == 'expense_pie':
                            # ดึงข้อมูลรายจ่ายแยกตามหมวดหมู่
                            data = Transaction.objects.filter(user=request.user, category__type='EXPENSE').values('category__name').annotate(total=Sum('amount'))
                            ui_data = {
                                'labels': [item['category__name'] for item in data],
                                'values': [float(item['total']) for item in data]
                            }
                            tool_res = "ระบบกำลังสร้างกราฟสัดส่วนรายจ่ายให้คุณ..."
                        elif chart_type == 'income_expense_bar':
                            # ดึงข้อมูลรายรับ vs รายจ่าย
                            ui_data = {
                                'labels': ['Income', 'Expense'],
                                'values': [float(summary['gross_income']), float(summary['total_expenses'])]
                            }
                            tool_res = "ระบบกำลังสร้างกราฟเปรียบเทียบรายรับรายจ่ายให้คุณ..."
                        else:
                            tool_res = "ไม่รู้จักประเภทกราฟที่ระบุ"
                        
                        messages.append(ToolMessage(content=tool_res, tool_call_id=tool_call["id"]))
                
                final_msg = llm_with_tools.invoke(messages)
                raw_content = final_msg.content
            else:
                raw_content = ai_msg.content
                
            # Handle list content from LangChain Google GenAI
            if isinstance(raw_content, list):
                texts = []
                for item in raw_content:
                    if isinstance(item, dict) and 'text' in item:
                        texts.append(item['text'])
                    elif isinstance(item, str):
                        texts.append(item)
                res = " ".join(texts)
            else:
                res = str(raw_content)
                
        except Exception as e:
            res = f"ขออภัยครับ ระบบเกิดข้อผิดพลาด: {str(e)}"
            
        # 6. Save AI response
        ChatMessage.objects.create(session=session, role='ai', content=res, ui_component=ui_component, ui_data=ui_data)
        
        return render(request, 'tax_assistant/_chat_message.html', {
            'ai_reply': res,
            'ui_component': ui_component,
            'ui_data': ui_data,
            'user_msg': user_msg_obj if receipt_file else None,
            'user_text': user_message if not receipt_file else None
        })

@login_required
def chat_page_view(request, session_id=None):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    
    if session_id:
        active_session = ChatSession.objects.get(id=session_id, user=request.user)
    else:
        active_session = sessions.first()
        if not active_session:
            active_session = ChatSession.objects.create(user=request.user, title="New Chat")
            sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'tax_assistant/chat.html', {
        'session': active_session,
        'sessions': sessions
    })

@login_required
def create_chat_view(request):
    new_session = ChatSession.objects.create(user=request.user, title="New Chat")
    return redirect('chat_page_with_id', session_id=new_session.id)

@login_required
def rename_chat_view(request, session_id):
    if request.method == "POST":
        session = ChatSession.objects.get(id=session_id, user=request.user)
        new_title = request.POST.get('title')
        if new_title:
            session.title = new_title
            session.save()
    return redirect('chat_page_with_id', session_id=session_id)

@login_required
def delete_chat_view(request, session_id):
    session = ChatSession.objects.get(id=session_id, user=request.user)
    session.delete()
    return redirect('chat_page')

# View for transaction details
@login_required
def transaction_detail_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'tax_assistant/transaction_detail.html', {'t': transaction})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
