from langchain.tools import tool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "alimirsa123@gmail.com" 
EMAIL_PASSWORD = "myxz onbb acaf bnot"

@tool
def policy_email_sender_tool(employee_email: str, policy_details: str) -> str:
    """
    Sends an email with the company policy to the employee.

    Args:
        employee_email (str): The employee's email address.
        policy_details (str): The details of the company policy.

    Returns:
        str: A confirmation message that the email was sent.
    """
    try:
        # Email content
        subject = "Company Policy: Please Acknowledge"
        body = f"""
        Dear Employee,

        Please review the following company policy:
        {policy_details}

        Reply to this email with 'I understand and acknowledge' if you agree to the policy.

        Best regards,
        HR Department
        """

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

        return f"Policy email successfully sent to {employee_email}."

    except Exception as e:
        return f"Failed to send policy email to {employee_email}. Error: {str(e)}"


import imaplib
import email




@tool
def fetch_policy_response_tool(employee_email: str) -> str:
    """
    Fetches the response from the employee's email address.

    Args:
        employee_email (str): The email address of the employee.

    Returns:
        str: The body of the email response from the employee.
    """
    try:
        # Connect to the mail server
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")  # Select the inbox folder

        # Search for emails from the employee
        status, messages = mail.search(None, f'FROM "{employee_email}"')
        if status != "OK":
            return f"No email found from {employee_email}."

        # Fetch the most recent email
        email_ids = messages[0].split()
        latest_email_id = email_ids[-1]  # Get the last email
        status, data = mail.fetch(latest_email_id, "(RFC822)")
        if status != "OK":
            return f"Failed to fetch email from {employee_email}."

        # Parse the email content
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()

    except Exception as e:
        return f"Failed to fetch response. Error: {str(e)}"
    
    
@tool
def analyze_policy_response_tool(employee_email: str) -> str:
    """
    Fetches and analyzes the employee's email response to the policy.

    Args:
        employee_email (str): The email address of the employee.

    Returns:
        str: A compliance status (e.g., "Understood", "Requires Follow-up").
    """
    try:
        # Fetch the employee's response
        employee_response = fetch_policy_response_tool(employee_email)

        # Analyze the response for acknowledgment
        if "understand" in employee_response.lower() and "acknowledge" in employee_response.lower():
            return f"Compliance Status for {employee_email}: Understood"
        else:
            return f"Compliance Status for {employee_email}: Requires Follow-up"
    except Exception as e:
        return f"Error analyzing response from {employee_email}. Error: {str(e)}"
    
