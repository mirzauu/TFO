from django.contrib import admin
from .models import Role, User, Company, CompanyStaff

# Register your models here.
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Company)
admin.site.register(CompanyStaff)
