from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('create/', views.create_request, name='create_request'),
    path('chat/', views.maintenance_chat, name='chat'),
    path('owner/chats/', views.owner_maintenance_chats, name='owner_chats'),
    path('owner/chat/<int:chat_id>/', views.owner_maintenance_chat_detail, name='owner_chat_detail'),
]
