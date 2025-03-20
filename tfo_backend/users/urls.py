from django.urls import path
from .views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset_password'),
]
