from django.contrib import admin

# Register your models here.
from .models import Organization, OrganizationStaff, Package, OrganizationSubscription,AIAgent,AgentChatSession,ChatMessage,UserLoginLog,EODReport,TicketIssue,ITSetup,PolicySetup
# Register your models here.
admin.site.register(Organization)
admin.site.register(OrganizationStaff)
admin.site.register(Package)
admin.site.register(OrganizationSubscription)
admin.site.register(AIAgent)
admin.site.register(AgentChatSession)
admin.site.register(ChatMessage)
admin.site.register(UserLoginLog)
admin.site.register(EODReport)
admin.site.register(TicketIssue)
admin.site.register(ITSetup)
admin.site.register(PolicySetup)

