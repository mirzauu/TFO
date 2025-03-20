import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, Field, EmailStr
from crewai.tools import BaseTool
from typing import Type
from django.urls import reverse
from django.conf import settings
from hr_crew.models import ChatMessage, Recruitment, Candidate,Schedule,Booking
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from organizations.models import Organization,OrganizationStaff,SMTPConfiguration,ChatMessage,LinkedInAPIKey

def get_smtp_details(chat_message_id):
    print("chat",chat_message_id)
    try:
        # Get the ChatMessage object
        chat_message = ChatMessage.objects.get(id=chat_message_id)
        # Get the associated Organization from the session
        print(chat_message)
        organization = chat_message.session.organization
        print(organization)
        
        # Get the SMTP configuration for the organization
        smtp_config = SMTPConfiguration.objects.get(organization=organization)
        print(smtp_config)
        
        # Return SMTP details
        return {
            "smtp_host": smtp_config.smtp_host,
            "smtp_port": smtp_config.smtp_port,
            "sender_email": smtp_config.sender_email,
            "password": smtp_config.password,  # Consider encrypting/decrypting this securely
        }
    except ObjectDoesNotExist:
        return {"error": "SMTP configuration not found for the given chat message ID"}
    except Exception as e:
        return {"error": str(e)}
    
class EmailSenderInput(BaseModel):
    chat_message_id: int = Field(..., description="The ID of the ChatMessage to fetch recruitment details.")
    content: str = Field(..., description="The content to be attached to the email.")
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")

class EmailSenderTool(BaseTool):
    name: str = "email_sender"
    description: str = "Sends an email with recruitment details to the top 5 candidates."

    def _run(self, chat_message_id: int, content: str,instance_id: int) -> str:
        try:
            # Get the ChatMessage
          
            recruitment = get_object_or_404(Recruitment, id=chat_message_id)
            # Get the related Recruitment entry
          

            # Get the top 5 candidates with the highest ATS score
            top_candidates = Candidate.objects.filter(
                recruitment=recruitment,
                ats_score__isnull=False,  # Ensure ATS score is not null
                screening=False  # Ensure screening is false
            ).order_by('-ats_score')[:5]  

            if not top_candidates:
                return "No candidates found for this recruitment."

            # Loop through candidates and send emails
            for candidate in top_candidates:
                booking_link = f"{settings.SITE_URL}{reverse('book_slot_by_candidate', kwargs={'candidate_id': candidate.id})}"
                email_content = f"""
                Dear {candidate.name},

                You have been shortlisted for the role of {recruitment.job_title} at {recruitment.location}.

                Job Description:
                {recruitment.job_requirement}

                Please use the link below to book your interview slot:
                {booking_link}

                Best regards,
                Recruitment Team
                """

                candidate.screening=True
                candidate.save()
                self.send_email(candidate.email, email_content,instance_id)

            return f"Emails successfully sent to the top {len(top_candidates)} candidates."

        except ChatMessage.DoesNotExist:
            return "ChatMessage with the given ID does not exist."
        except Recruitment.DoesNotExist:
            return "No recruitment found for the given ChatMessage."
        except Exception as e:
            return f"Failed to send emails. Error: {str(e)}"

    def send_email(self, recipient_email: str, content: str,instance_id:int):
        """
        Sends an email to the given recipient.
        """
        try:
            smtp_details = get_smtp_details(instance_id)
            print("email",smtp_details)

            if "error" in smtp_details:
                return f"❌ Error: {smtp_details['error']}"

            smtp_host = smtp_details["smtp_host"]
            smtp_port = smtp_details["smtp_port"]
            sender_email = smtp_details["sender_email"]
            password = smtp_details["password"]

            if not smtp_host or not smtp_port or not sender_email or not password:
                return "❌ Error: Incomplete SMTP configuration."
        
            subject = "Interview Slot Booking"
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")



class InterviewNotificationToolinput(BaseModel):
    """Input schema for checking booked interview slots."""
    chat_message_id: int = Field(..., description="ID of the recruitment process.")
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")

class InterviewNotificationTool(BaseTool):
    """
    Tool to check if any candidate has booked an interview slot.
    If booked, send an email confirmation with meeting details.
    """
    name: str = "interview_slot_checker"
    description: str = "Checks all booked candidates and sends email confirmations."
    args_schema: Type[BaseModel] = InterviewNotificationToolinput

    def _run(self, chat_message_id: int,instance_id:int) -> dict:
        """
        Checks for booked interview slots and sends an email to all candidates with interview_status=True.

        Args:
            chat_message_id (int): ID of the recruitment process.

        Returns:
            dict: Status of interview booking and email notifications.
        """
        try:
            # Get recruitment instance
            recruitment = get_object_or_404(Recruitment, id=chat_message_id)

            # Find all candidates who have booked an interview slot
            booked_candidates = Candidate.objects.filter(recruitment=recruitment, interview_status=True)

            if booked_candidates.exists():
                email_sender = EmailSenderTool()  # Use your existing email sender tool
                email_results = []

                for candidate in booked_candidates:
                    # Get the candidate's booked schedule via Booking model
                    booking = Booking.objects.filter(candidate=candidate).first()

                    if booking:
                        booked_slot = booking.schedule

                        # Prepare email content
                        email_content = f"""
                        Dear {candidate.name},

                        Your interview for the {recruitment.job_title} role at {recruitment.location} is scheduled.

                        Interview Date: {booked_slot.date}
                        Time: {booked_slot.time_slot}
                        Meeting Link: {booked_slot.meet_link}

                        Best regards,
                        Recruitment Team
                        """

                        # Send email using EmailSenderTool
                        email_sender.send_email(candidate.email, email_content,instance_id)
                        email_results.append({
                            "candidate_name": candidate.name,
                            "email": candidate.email,
                            "date": booked_slot.date.strftime("%Y-%m-%d"),
                            "time": booked_slot.time_slot.strftime("%H:%M"),
                            "meet_link": booked_slot.meet_link
                        })

                return {
                    "message": f"Emails sent to {len(email_results)} candidates.",
                    "details": email_results
                }

            # No candidates booked a slot
            return {
                "message": "No candidate booked a slot.",
                "task_status": "PENDING"
            }

        except Exception as e:
            return {"error": str(e), "task_status": "FAILED"}