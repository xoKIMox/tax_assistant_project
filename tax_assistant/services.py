from decimal import Decimal
from .models import Transaction

def calculate_tax_summary(user):
    # 1. รวมรายได้ทั้งหมด
    incomes = Transaction.objects.filter(user=user, category__type='INCOME')
    gross_income = sum(t.amount for t in incomes) or Decimal('0')

    # 2. รวมรายจ่ายทั้งหมด
    expenses = Transaction.objects.filter(user=user, category__type='EXPENSE')
    total_expenses = sum(t.amount for t in expenses) or Decimal('0')

    # 3. หักค่าใช้จ่ายเหมา 50% (แต่ไม่เกิน 100,000 บาท) - สำหรับภาษี
    expense_deduction_tax = min(gross_income * Decimal('0.5'), Decimal('100000'))

    # 4. หักค่าลดหย่อน (ส่วนตัว 60,000 + อื่นๆ)
    extra_deduct = sum(t.amount for t in Transaction.objects.filter(user=user, category__type='DEDUCTIBLE')) or Decimal('0')
    total_allowance = Decimal('60000') + extra_deduct

    # 5. เงินได้สุทธิ (สำหรับคิดภาษี)
    net_income_tax = max(gross_income - expense_deduction_tax - total_allowance, Decimal('0'))

    # 6. คำนวณภาษีขั้นบันได
    tax = Decimal('0')
    if net_income_tax > 150000:
        tax = (net_income_tax - 150000) * Decimal('0.05') 

    return {
        'gross_income': gross_income,
        'total_expenses': total_expenses,
        'net_balance': gross_income - total_expenses,
        'total_allowance': total_allowance,
        'estimated_tax': tax
    }
