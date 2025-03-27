import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.contrib import messages
import json
User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@method_decorator(csrf_exempt, name="dispatch")
class ForgotPasswordView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            user = User.objects.filter(email=email).first()

            if not user:
                return JsonResponse({"error": "Email is not found"}, status=404)

            # Generate password reset token
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct password reset link
            reset_link = f"{settings.SITE_URL}/auth/reset-password/{uidb64}/{token}/"

            # SMTP Email Configuration
            smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")  # Default to Gmail SMTP
            smtp_port = int(os.getenv("EMAIL_PORT", 587))  # Default to 587
            sender_email = os.getenv("EMAIL_HOST_USER")
            password = os.getenv("EMAIL_HOST_PASSWORD")
            recipient_email = email
            subject = "Password Reset Request"
            content = f"Click the link to reset your password: {reset_link}"
            print(sender_email,password)
            # Send email using the provided SMTP method
            if not smtp_host or not smtp_port or not sender_email or not password:
                return JsonResponse({"error": "❌ Incomplete SMTP configuration."}, status=500)
            try:
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = recipient_email
                msg["Subject"] = subject
                msg.attach(MIMEText(content, "plain"))

                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.send_message(msg)

                return JsonResponse({"message": "Reset link sent to email"}, status=200)

            except Exception as e:
                return JsonResponse({"error": f"❌ Email sending failed: {e}"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class ResetPasswordView(View):
    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
                return HttpResponse("Invalid or expired token.", status=400)
        return render(request, "reset_password.html", {"uidb64": uidb64, "token": token})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return HttpResponse("Invalid or expired token.", status=400)

            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password != confirm_password:
                return HttpResponse("Passwords do not match.", status=400)

            # Update password
            user.set_password(new_password)
            user.save()
            return HttpResponse("Your password has been reset successfully.", status=200)

        except Exception:
            return HttpResponse("Invalid reset link.", status=400)  