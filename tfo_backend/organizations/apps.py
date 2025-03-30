from django.apps import AppConfig
import json

class OrganizationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organizations"
    

    def ready(self):
        import organizations.signals  # Ensure signals are loaded

        # Dynamically create periodic task
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        from django.db.utils import OperationalError, ProgrammingError

        try:
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=0, hour=23  # Adjust this time as needed
            )

            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                name="Send EOD Reports",
                task="organizations.tasks.send_eod_report",
                defaults={"kwargs": json.dumps({})}
            )
        except (OperationalError, ProgrammingError):
            # These errors occur if migrations haven't been applied yet
            pass
