import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from typing import Optional
# from crew.models import Document, EmployeeOnboardingTask
from langchain.tools import tool
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "alimirsa123@gmail.com"  # From your Django settings
EMAIL_PASSWORD = "myxz onbb acaf bnot"

from pydantic import BaseModel, Field
from typing import Dict, Optional

class DocumentAutomation(BaseModel):
    has_link_generated: Optional[bool] = Field(None, description="If the link is generated for the employee, this is True.")
    has_email_sent: Optional[bool] = Field(None, description="If the email is sent to the employee, this is True.")
    has_document_verified: Optional[bool] = Field(None, description="If the document is verified successfully, this is True.")
    document_status: Optional[str] = Field(None, description="Status of document collection and verification.")
    
 
  
@tool("DocumentAutomationStatus")    
def document_automation_status(newhireinfo: Dict) -> DocumentAutomation:
    """
    Processes the newhireinfo dictionary to determine the status of document automation.

    Args:
        newhireinfo (Dict): Dictionary containing new hire information.

    Returns:
        DocumentAutomation: The status of document automation tasks.
    """
    # Extract existing document status from newhireinfo
    current_status = newhireinfo.get("document_status", {})
    

    # If document_status already exists, return it
    if isinstance(current_status, dict):
        return DocumentAutomation(**current_status)

    # Initialize a default status if no document_status exists
    default_status = DocumentAutomation(
        has_link_generated=False,
        has_email_sent=False,
        has_document_verified=False,
        document_status="No document automation started."
    )

    return default_status

@tool
def google_form_link_generator_tool(employee_id: str) -> str:
    """
    Generates a default link for document upload for an employee.

    Args:
        employee_id (str): The ID of the employee.

    Returns:
        str: The link to upload the documents.
    """
    return f"http://127.0.0.1:8000/employee/{employee_id}/upload-documents/"
@tool("DocumentVerificationTool")
def verify_document(employee_id: str, document_type: Optional[str] = None) -> str:
    """
    Verifies if the specified document for an employee is uploaded.

    Args:
        employee_id (str): The ID of the employee.
        document_type (str, optional): The type of document to verify (e.g., 'resume' or 'education_qualification').

    Returns:
        str: Verification success or failure message.
    """
    return f"Verification failed: no documment uploaded"

    # try:
    #     # Fetch the employee's onboarding task
    #     task = EmployeeOnboardingTask.objects.filter(employee_id=employee_id).first()
    #     if not task:
    #         return f"Verification failed: No onboarding task found for employee ID '{employee_id}'."

    #     # Fetch the related documents for the task
    #     documents = Document.objects.filter(onboarding_task=task)

    #     if not documents.exists():
    #         print("000000000000000000000000")
    #         return f"Verification failed: No documents uploaded for employee ID '{employee_id}'."

    #     # If a specific document type is requested, verify its existence
    #     if documents.exists():
    #         print("==============================")
    #         return f"Verification successfull:documents found for employee ID '{employee_id}'."

    # except Exception as e:
    #     return f"Verification failed: An error occurred - {str(e)}"


@tool
def email_sender_tool(employee_email: str, form_link: str) -> str:
    """
    Sends the Google Form link to the employee's email.

    Args:
        employee_email (str): The email address of the employee.
        form_link (str): The link to the Google Form.

    Returns:
        str: A message confirming the email was sent successfully.
    """
    try:
        # Create the email
        subject = "Document Submission Link"
        body = (
            "Dear Employee,\n\n"
            "We hope this message finds you well.\n\n"
            "Please use the secure link below to submit your documents:\n"
            f"{form_link}\n\n"
            "If you have any questions or encounter any issues, feel free to reach out to us for assistance.\n\n"
            "Best regards,\n"
            "The NYPUS Team"
        )
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = employee_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return f"Email successfully sent to {employee_email} with the link: {form_link}"

    except Exception as e:
        return f"Failed to send email to {employee_email}. Error: {str(e)}"




@tool
def welcome_email_sender_tool(employee_email: str, employee_name: str) -> str:
    """
    Sends a personalized  email to the new employee.

    Args:
        employee_email (str): The email address of the employee.
        employee_name (str): The name of the employee.

    Returns:
        str: A message confirming the email was sent successfully.
    """
    try:
        # Email content
        subject = "Welcome to NYPUS!"
        body = f"""
        Dear {employee_name},

        Welcome to NYPUS! We are thrilled to have you join our team.

        Your first day is an exciting start to your journey with us. Please check your orientation details here: [link]
        If you have any questions or need assistance, feel free to reach out.

        Best regards,
        [Your Team]
        """

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = employee_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return f"Welcome email successfully sent to {employee_email}."

    except Exception as e:
        return f"Failed to send welcome email to {employee_email}. Error: {str(e)}"