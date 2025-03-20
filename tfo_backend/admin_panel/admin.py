from django.contrib import admin
from .models import APIKey

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "value")  # Show both fields in admin panel
    search_fields = ("name",)  # Enable search by name
    list_filter = ("name",)  # Allow filtering by name

admin.site.register(APIKey, APIKeyAdmin)
