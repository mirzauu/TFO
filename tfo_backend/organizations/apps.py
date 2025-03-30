from django.apps import AppConfig
import json

class OrganizationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organizations"
    

    def ready(self):
        import organizations.signals  # Ensure signals are loaded
