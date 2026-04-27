from django.urls import path, include
from . import views
from . import ai_tools_urls as tools

app_name = 'ai_agent'

urlpatterns = [
    # Chat endpoints
    path('chat/', views.chat_with_ai, name='chat'),
    path('student/', views.student_assistant, name='student_assistant'),
    path('student/guide/', views.student_housing_guide, name='student_guide'),
    path('tenant/', views.tenant_assistant, name='tenant_assistant'),
    path('tenant/guide/', views.tenant_housing_guide, name='tenant_guide'),
    path('conversations/', views.AIConversationListView.as_view(), name='conversation_list'),
    path('conversations/new/', views.create_new_conversation, name='create_conversation'),
    path('conversations/<int:pk>/', views.AIConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # Statistics and info
    path('statistics/', views.conversation_statistics, name='statistics'),
    path('capabilities/', views.ai_capabilities, name='capabilities'),
    
    # AI Tools for hostel booking
    path('tools/', include(tools)),
]
