from django import forms
from .models import UserProfile, Transaction, CommunityPost, CommunityComment

class PostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all', 'placeholder': 'What do you want to ask or share?'}),
            'content': forms.Textarea(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all min-h-[150px]', 'placeholder': 'Write your story or question here...'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommunityComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all min-h-[100px]', 'placeholder': 'Add a comment...'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'payee', 'category', 'receipt_image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'payee': forms.TextInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'category': forms.Select(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'receipt_image': forms.FileInput(attrs={'class': 'w-full text-sm text-neutral-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 transition-all'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'nickname', 'birth_date', 'marital_status', 'monthly_base_salary',
            'children_before_2018', 'children_after_2018',
            'parents_care_count', 'disabled_care_count'
        ]
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all', 'placeholder': 'เช่น พี่หนุ่ม, น้องเบล'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'marital_status': forms.Select(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'monthly_base_salary': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all', 'placeholder': '0.00'}),
            'children_before_2018': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'children_after_2018': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'parents_care_count': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
            'disabled_care_count': forms.NumberInput(attrs={'class': 'w-full bg-white dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 rounded-xl px-5 py-3 focus:ring-2 focus:ring-indigo-500/20 transition-all'}),
        }
