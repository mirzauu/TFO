from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .helpers import OrganizationToken
from rest_framework.permissions import IsAuthenticated
from .models import TicketIssue,OrganizationStaff,AgentChatSession,AIAgent,ChatMessage,Organization, LinkedInAPIKey, SMTPConfiguration, EODReportConfiguration,EODReport,UserLoginLog,ITSetup, PolicySetup
from .serializers import OrganizationDetailsSerializer,AgentChatSessionSerializer,ChatMessageSerializer,CreateChatMessageSerializer,ChatMessageIDSerializer,LinkedInAPIKeySerializer, SMTPConfigurationSerializer, EODReportConfigurationSerializer,ITSetupSerializer, PolicySetupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate, login
from .signals import log_user_login 
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from django.db.models import F
import csv
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.signals import user_logged_out
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
import json
class OrganizationLoginView(APIView):
    """
    Login view for organization users.
    Authenticates the user, generates a JWT token, and returns user details.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user and user.role.name in ['organization_admin', 'organization_staff']:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            access['role'] = user.role.name
            access['email'] = user.email

            response = Response({
                'access_token': str(access),
                'refresh_token': str(refresh),
                'user_id': str(user.id),
                'role': user.role.name,
            }, status=200)

            response.set_cookie(
                key='access_token',
                value=str(access),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600,
            )

            # Trigger the login signal manually
            user_logged_in.send(sender=user.__class__, request=request, user=user)

            return response

        return Response({'error': 'Invalid email, password, or user role'}, status=401)

class OrganizationHomePageView(APIView):
    """
    Fetch details of the organization for organization admins.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract user information from the token
        token = request.auth
        user_entity_id = token.get('user_id')  
        print(user_entity_id)  # Debugging

        try:
            # Get the OrganizationStaff record for the current user
            organization_staff = OrganizationStaff.objects.select_related('organization').get(user_id=user_entity_id)
            organization = organization_staff.organization
        except OrganizationStaff.DoesNotExist:
            return Response({'error': 'Organization not found for the given user'}, status=404)

        # Pass only the logged-in user's details to the serializer
        serializer = OrganizationDetailsSerializer(organization, context={'request_user_id': user_entity_id})
        return Response(serializer.data, status=200)
    
class AgentChatSessionView(APIView):
    """
    API to retrieve all chat sessions for a specific agent for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, agent_id):
        user = request.user

        # Find the organization linked to the user
        try:
            organization = OrganizationStaff.objects.get(user=user).organization
        except OrganizationStaff.DoesNotExist:
            return Response({"error": "User is not linked to any organization"}, status=403)

        # Fetch all chat sessions for the given agent in that organization
        sessions = AgentChatSession.objects.filter(agent_id=agent_id, organization=organization)

        # Fetch all chat messages linked to those sessions
        messages = ChatMessage.objects.filter(session__in=sessions,user=user)

        # Serialize message IDs
        serializer = ChatMessageIDSerializer(messages, many=True)
        return Response(serializer.data, status=200)




class CreateChatMessageView(APIView):
    """
    API to create a ChatMessage for a user and agent.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, agent_id):
        user = request.user

        # Get the user's organization
        try:
            organization = OrganizationStaff.objects.get(user=user).organization
        except OrganizationStaff.DoesNotExist:
            return Response({"error": "User is not linked to any organization"}, status=403)

        # Check if a session exists for this user and agent
        session = AgentChatSession.objects.filter(agent_id=agent_id, organization=organization).first()

        if not session:
            return Response(
                {"success": False, "message": "No active session found for this user and agent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve the last ChatMessage for the session
        last_chat_message = ChatMessage.objects.filter(session=session,user=request.user).order_by('-created_at').first()

        if last_chat_message:
            # Use the serializer to get the message data
            serializer = ChatMessageSerializer(last_chat_message)
            last_message_content = serializer.data.get("message", "")

            # Prevent creating a new chat message if the last message is empty
            if not last_message_content:
                return Response(
                    {"success": False, "message": "The last message is empty. Cannot create a new chat message."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Create a new ChatMessage
        chat_message = ChatMessage.objects.create(session=session,user=request.user)

        # Update EOD report for the organization
        self.update_eod_report(organization)

        return Response(
            {"success": True, "chat_message_id": chat_message.id},
            status=status.HTTP_200_OK,
        )

    def update_eod_report(self, organization):
        """
        Updates the EOD report by incrementing the chat message count for the organization.
        """
        today = now().date()
        eod_report, created = EODReport.objects.get_or_create(
            organization=organization, date=today,
            defaults={"total_chat_sessions": 1}
        )
        
        if not created:
            eod_report.total_chat_sessions = F('total_chat_sessions') + 1
            eod_report.save(update_fields=['total_chat_sessions'])

class SettingsPageAPIView(APIView):
    """
    API for viewing and updating LinkedIn API, SMTP, and EOD Report settings of an organization.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        staff = get_object_or_404(OrganizationStaff, user=user)
        organization = staff.organization

        # Check if the user's role is "organization_staff"
        if user.role.name == "organization_staff":
            return Response([], status=status.HTTP_200_OK)

        linkedin_api = LinkedInAPIKey.objects.filter(organization=organization).first()
        smtp_config = SMTPConfiguration.objects.filter(organization=organization).first()
        eod_config = EODReportConfiguration.objects.filter(organization=organization).first()

        data = {
            "linkedin_api": LinkedInAPIKeySerializer(linkedin_api).data if linkedin_api else None,
            "smtp_config": SMTPConfigurationSerializer(smtp_config).data if smtp_config else None,
            "eod_config": EODReportConfigurationSerializer(eod_config).data if eod_config else None
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update LinkedIn API, SMTP, and EOD Report settings for an organization.
        """
        user = request.user

        staff = get_object_or_404(OrganizationStaff, user=user)
        organization = staff.organization

        # If the user's role is "organization_staff", they cannot update settings
        if user.role.name == "organization_staff":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        linkedin_api = LinkedInAPIKey.objects.filter(organization=organization).first()
        smtp_config = SMTPConfiguration.objects.filter(organization=organization).first()
        eod_config = EODReportConfiguration.objects.filter(organization=organization).first()

        linkedin_serializer = LinkedInAPIKeySerializer(linkedin_api, data=request.data.get("linkedin_api", {}), partial=True)
        smtp_serializer = SMTPConfigurationSerializer(smtp_config, data=request.data.get("smtp_config", {}), partial=True)
        eod_serializer = EODReportConfigurationSerializer(eod_config, data=request.data.get("eod_config", {}), partial=True)

        if linkedin_serializer.is_valid() and smtp_serializer.is_valid() and eod_serializer.is_valid():
            linkedin_serializer.save()
            smtp_serializer.save()
            eod_serializer.save()
            return Response({
                "linkedin_api": linkedin_serializer.data,
                "smtp_config": smtp_serializer.data,
                "eod_config": eod_serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "linkedin_api_errors": linkedin_serializer.errors,
            "smtp_config_errors": smtp_serializer.errors,
            "eod_config_errors": eod_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




class EODReportAPIView(APIView):
    """
    API for viewing EOD reports of an organization.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user
        staff = get_object_or_404(OrganizationStaff, user=user)
        organization = staff.organization
        reports = EODReport.objects.filter(organization=organization).order_by("-date")

        # ✅ Check if user requested CSV format
        if request.GET.get("format") == "csv":
            return self.generate_csv(reports, organization)

        # ✅ Default JSON response
        eod_data = [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "total_logins": r.total_logins,
                "total_chat_sessions": r.total_chat_sessions,
                "total_messages": r.total_messages,
                "total_agents_used": r.total_agents_used,
                "agent_usage": r.agent_usage,
            }
            for r in reports
        ]
        return Response({"organization": organization.name, "eod_reports": eod_data})

    def generate_csv(self, reports, organization):
        """Helper function to generate a CSV file response."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="EOD_Report_{organization.name}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Date", "Total Logins", "Total Chat Sessions", "Total Messages", "Total Agents Used", "Agent Usage"])

        for report in reports:
            writer.writerow([
                report.date.strftime("%Y-%m-%d"),
                report.total_logins,
                report.total_chat_sessions,
                report.total_messages,
                report.total_agents_used,
                report.agent_usage,  # JSON field (Django automatically converts it to a string)
            ])

        return response



class OrganizationLogoutView(APIView):
    """
    Logout view for organization users.
    Blacklists the refresh token and removes the access token cookie.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Trigger the logout signal manually
            user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)

            response = Response({"message": "Successfully logged out"}, status=200)
            response.delete_cookie("access_token")  # Remove the access token cookie

            return response
        except Exception as e:
            return Response({"error": "Invalid token or already logged out"}, status=400)
        

class RaiseTicketView(APIView):
    """
    API for users to raise a ticket.
    The user must be authenticated.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        email = user.email
        username = user.username
        message = request.data.get('message')

        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the organization from the user's data
        try:
            organization_staff = OrganizationStaff.objects.select_related('organization').get(user=user)
            organization_name = organization_staff.organization.name
        except OrganizationStaff.DoesNotExist:
            return Response({"error": "User is not linked to any organization"}, status=status.HTTP_404_NOT_FOUND)

        # Save ticket issue
        ticket = TicketIssue.objects.create(
            user=user,
            email=email,
            username=username,
            organization=organization_name,
            message=message
        )

        return Response({
            "message": "Ticket raised successfully",
            "ticket_id": ticket.id,
            "username": username,
            "organization": organization_name
        }, status=status.HTTP_201_CREATED)           
    

@api_view(['GET'])
@permission_classes([AllowAny])
def company_a_data(request):
    # Get Company A
    company_a = get_object_or_404(Organization, name="companyA")

    # Get login details
    logins = UserLoginLog.objects.filter(organization=company_a).values(
        "user__username", "timestamp", "ip_address", "user_agent"
    )

    # Get agent usage
    sessions = AgentChatSession.objects.filter(organization=company_a)
    agent_usage = {}
    for session in sessions:
        agent_name = session.agent.name
        if agent_name not in agent_usage:
            agent_usage[agent_name] = 0
        agent_usage[agent_name] += 1

    # Get messages grouped by date
    messages = ChatMessage.objects.filter(session__organization=company_a).order_by("created_at")
    messages_by_date = {}
    for message in messages:
        date_str = message.created_at.date().isoformat()
        if date_str not in messages_by_date:
            messages_by_date[date_str] = []
        messages_by_date[date_str].append({
            "user": message.user.username,
            "session_id": message.session.id,
            "created_at": message.created_at.isoformat(),
        })

    # Prepare response
    data = {
        "company": company_a.name,
        "logins": list(logins),
        "agent_usage": agent_usage,
        "messages_by_date": messages_by_date
    }
    return Response(data)    


class OrgSetupAPIView(APIView):
    """
    API to retrieve and update IT Setup and Policy Setup for an organization.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        staff = get_object_or_404(OrganizationStaff, user=user)
        organization = staff.organization

        if user.role.name == "organization_staff":
            return Response([], status=status.HTTP_200_OK)

        it_setup = ITSetup.objects.filter(organization=organization).first()
        policy_setup = PolicySetup.objects.filter(organization=organization).first()

        data = {
            "it_setup": ITSetupSerializer(it_setup).data if it_setup else None,
            "policy_setup": PolicySetupSerializer(policy_setup).data if policy_setup else None,
        }
        return Response(data, status=status.HTTP_200_OK)

    
    def put(self, request):
        """
        Update IT Setup and Policy Setup for an organization.
        """
        user = request.user

        staff = get_object_or_404(OrganizationStaff, user=user)
        organization = staff.organization

        if user.role.name == "organization_staff":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        # Handle `form-data` with JSON in `data` and file in `file`
        try:
            payload = json.loads(request.data.get("data", "{}"))
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format in `data`"}, status=status.HTTP_400_BAD_REQUEST)

        it_data = payload.get("it_setup", {})
        policy_data = payload.get("policy_setup", {})

        # Add the uploaded file manually (if any)
        if "file" in request.FILES:
            policy_data["document"] = request.FILES["file"]

        it_setup = ITSetup.objects.filter(organization=organization).first()
        policy_setup = PolicySetup.objects.filter(organization=organization).first()

        it_serializer = ITSetupSerializer(it_setup, data=it_data, partial=True)
        policy_serializer = PolicySetupSerializer(policy_setup, data=policy_data, partial=True)

        if it_serializer.is_valid() and policy_serializer.is_valid():
            it_serializer.save()
            policy_serializer.save()
            return Response({
                "it_setup": it_serializer.data,
                "policy_setup": policy_serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            "it_setup_errors": it_serializer.errors,
            "policy_setup_errors": policy_serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)