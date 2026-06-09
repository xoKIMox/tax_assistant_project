"""
URL configuration for tax_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_receipt_view, name='upload_receipt'),
    path('chat-api/', views.chat_api_view, name='chat_api'),
    path('chat-api/<int:session_id>/', views.chat_api_view, name='chat_api_with_id'),
    path('chat/', views.chat_page_view, name='chat_page'),
    path('chat/<int:session_id>/', views.chat_page_view, name='chat_page_with_id'),
    path('chat/new/', views.create_chat_view, name='create_chat'),
    path('chat/rename/<int:session_id>/', views.rename_chat_view, name='rename_chat'),
    path('chat/delete/<int:session_id>/', views.delete_chat_view, name='delete_chat'),
    path('transaction/<int:pk>/', views.transaction_detail_view, name='transaction_detail'),
    path('transaction/<int:pk>/edit/', views.edit_transaction_view, name='edit_transaction'),
    path('transaction/<int:pk>/delete/', views.delete_transaction_view, name='delete_transaction_action'),
    path('profile/', views.profile_settings_view, name='profile_settings'),
    path('register/', views.register_view, name='register'),
    path('community/', views.community_feed_view, name='community_feed'),
    path('community/new/', views.create_post_view, name='create_post'),
    path('community/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('community/<int:pk>/like/', views.like_post_view, name='like_post'),
]

