from django.urls import path
from .views import OrganizationLoginView,OrganizationHomePageView,AgentChatSessionView,CreateChatMessageView,SettingsPageAPIView,EODReportAPIView,OrgSetupAPIView,OrganizationLogoutView,RaiseTicketView,company_a_data

urlpatterns = [
     path('login/', OrganizationLoginView.as_view(), name='organization-login'),
     path('logout/', OrganizationLogoutView.as_view(), name='organization-login'),
     path('home/', OrganizationHomePageView.as_view(), name='organization-home'),
     path('agent/<int:agent_id>/chat-sessions/', AgentChatSessionView.as_view(), name='agent-chat-sessions'),
     path('agents/<int:agent_id>/create-chat-message/', CreateChatMessageView.as_view(), name='create-chat-message'),
     path('settings/', SettingsPageAPIView.as_view(), name='settings-page'),
     path('eod-report/', EODReportAPIView.as_view(), name='eod-report'),
     path('raise-ticket/', RaiseTicketView.as_view(), name='raise-ticket'),
     path('user_details/', company_a_data, name='ticket'),
     path('org-setup/', OrgSetupAPIView.as_view(), name='org-setup'),
     
]