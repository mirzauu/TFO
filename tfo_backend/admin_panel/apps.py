from django.apps import AppConfig
import os
from django.conf import settings
import threading

class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "admin_panel"

    def ready(self):
        from .models import APIKey  # Import inside ready()

        def load_api_keys():
            """Load API keys into Django settings after startup."""
            try:
                for api_key in APIKey.objects.all():
                    setattr(settings, api_key.name, api_key.value)  # Use plain text value
                    os.environ[api_key.name] = api_key.value
                    print(f"🔑 Loaded API Key: {api_key.name}")
                print("✅ API Keys Loaded into Settings")
            except Exception as e:
                print(f"⚠️ Error loading API keys: {e}")

        # Run in a separate thread to avoid blocking startup
        threading.Thread(target=load_api_keys).start()
