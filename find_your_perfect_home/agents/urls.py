from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Agent Profiles
    path('profiles/', views.AgentProfileListView.as_view(), name='agent-list'),
    
    # Agent Requests
    path('requests/', views.AgentRequestListCreateView.as_view(), name='request-list-create'),
    
    # Statistics
    path('statistics/', views.agent_statistics, name='agent-statistics'),
    
    # Manual Assignment (Admin only)
    path('assign/<int:request_id>/', views.assign_agent_manually, name='assign-manual'),
]
