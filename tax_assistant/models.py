from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    MARITAL_CHOICES = [
        ('Single', 'โสด'),
        ('Married_No_Income', 'สมรส (คู่สมรสไม่มีรายได้)'),
        ('Married_With_Income', 'สมรส (คู่สมรสมีรายได้)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=50, choices=MARITAL_CHOICES, default='Single')
    children_before_2018 = models.IntegerField(default=0)
    children_after_2018 = models.IntegerField(default=0)
    parents_care_count = models.IntegerField(default=0)
    disabled_care_count = models.IntegerField(default=0)
    monthly_base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Profile: {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50 , choices=[
        ('Income', 'รายรับ'),
        ('Expense', 'รายจ่าย'),
        ('Deduction', 'ค่าลดหย่อน'),
    ])

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payee = models.CharField(max_length=255, blank=True , null=True )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.date} - {self.amount} - {self.payee}"

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])
    content = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    ui_component = models.CharField(max_length=50, blank=True, null=True)
    ui_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.created_at}"

class CommunityPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title

class CommunityComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"