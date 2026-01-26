from django.urls import path
from .views import ChatAPIView

app_name = 'chatbot'

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
]
