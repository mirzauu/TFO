from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now
from .models import UserLoginLog, EODReport, OrganizationStaff  # Import OrganizationStaff


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Signal to track user logins and update EOD reports.
    """
    print("signal recieved")
    ip = get_client_ip(request)
    print("signal recieved",ip)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    print("signal recieved",user_agent)
    
    organization_staff = OrganizationStaff.objects.filter(user=user).first()
    organization = organization_staff.organization if organization_staff else None
    print("signal recieved",organization)

    if organization:
        # Save login log entry
        UserLoginLog.objects.create(
            user=user,
            organization=organization,
            ip_address=ip,
            user_agent=user_agent
        )

        # Update EOD report
        today = now().date()
        eod_report, created = EODReport.objects.get_or_create(
            organization=organization, date=today,
            defaults={'total_logins': 1}
        )

        if not created:
            eod_report.total_logins += 1
            eod_report.save()


def get_client_ip(request):
    """
    Retrieve client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
