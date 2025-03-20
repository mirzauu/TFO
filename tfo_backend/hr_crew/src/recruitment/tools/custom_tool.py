from typing import Type, List,Optional
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os
from langchain.tools import tool
load_dotenv()
from hr_crew.models import Recruitment, RecruitmentTask,Candidate,Schedule
from django.shortcuts import get_object_or_404
from typing import Literal
import PyPDF2
import random
from django.conf import settings
from django.core.mail import EmailMessage

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from django.core.exceptions import ObjectDoesNotExist
from organizations.models import Organization,OrganizationStaff,SMTPConfiguration,ChatMessage,LinkedInAPIKey
# Email credentials

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
    
def get_linkedin_access_token(chat_message_id):
    print("Chat Message ID:", chat_message_id)
    try:
        # Get the ChatMessage object
        chat_message = ChatMessage.objects.get(id=chat_message_id)
        print("Chat Message:", chat_message)

        # Get the associated Organization from the session
        organization = chat_message.session.organization
        print("Organization:", organization)

        # Get the LinkedIn API key for the organization
        linkedin_api_key = LinkedInAPIKey.objects.get(organization=organization)
        print("LinkedIn API Key:", linkedin_api_key)

        # Return LinkedIn access token
        return {
            "access_token": linkedin_api_key.access_token,
        }
    except ObjectDoesNotExist:
        return {"error": "LinkedIn access token not found for the given chat message ID"}
    except Exception as e:
        return {"error": str(e)}
    
class TaskStatusUpdateSchema(BaseModel):
    task_name: str = Field(..., description="The name of the task being updated.")
    status: Literal["COMPLETED", "PENDING"] = Field(..., description="Task status must be 'COMPLETED' or 'PENDING' or 'FAILED'.")
    report:str = Field(..., description="the report of the task")
    chat_message_id: int = Field(..., description="The ID of the chat message associated with the task.")

class OfferLetterSenderInput(BaseModel):
    """Input schema for OfferLetterSenderTool."""
    chat_message_id: int = Field(..., description="ID of the recruitment process.")
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")


class OfferLetterSenderTool(BaseTool):
    """
    Tool to check for selected candidates and send offer letters.
    """
    name: str = "offer_letter_sender"
    description: str = "Checks if candidates are selected and sends offer letters via email."
    args_schema: Type[BaseModel] = OfferLetterSenderInput

    def _run(self, chat_message_id: int,instance_id: int) -> dict:
        """
        Checks if candidates are selected and sends offer letters via email.

        Args:
            chat_message_id (int): ID of the recruitment process.

        Returns:
            dict: Status of the offer letter process.
        """
        try:
            # Get recruitment instance
            recruitment = get_object_or_404(Recruitment, id=chat_message_id)

            # Find all selected candidates
            selected_candidates = Candidate.objects.filter(recruitment=recruitment, selected=True)

            if not selected_candidates.exists():
                selection_link = f"{settings.SITE_URL}/o/recruitment/{chat_message_id}/candidates/"
                recruitment.session.save_message_to_mongo({
                    "Type": "text",
                    "message": f"No candidates selected. Please complete the selection process: {selection_link}",
                    "task_name": "offer link",
                    "user": "AI",
                     },task_name="offer link")
                return {
                    "message": f"No candidates selected. Please complete the selection process: {selection_link}",
                    "task_status": "PENDING"
                }
          

            email_results = []

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

            # SMTP setup
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(sender_email, password)

            for candidate in selected_candidates:
                if candidate.offer_letter_document:
                    # Prepare email
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = candidate.email
                    msg["Subject"] = "Job Offer Letter"

                    body = f"""
                    Dear {candidate.name},

                    Congratulations! You have been selected for the {recruitment.job_title} position at {recruitment.location}.
                    Please find your offer letter attached.

                    Best regards,  
                    Recruitment Team
                    """

                    msg.attach(MIMEText(body, "plain"))

                    # Attach the offer letter PDF
                    file_path = candidate.offer_letter_document.path
                    attachment = open(file_path, "rb")

                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(part)
                    attachment.close()

                    # Send email
                    server.sendmail(sender_email, candidate.email, msg.as_string())

                    # Mark offer letter as sent
                    candidate.offer_letter = True
                    candidate.save()

                    email_results.append({
                        "candidate_name": candidate.name,
                        "email": candidate.email,
                        "offer_letter_sent": True
                    })

            server.quit()

            return {
                "message": f"Offer letters sent to {len(email_results)} candidates.",
                "task_status": "COMPLETED",
                "details": email_results
            }

        except Exception as e:
            return {"error": str(e), "task_status": "FAILED"}
    
class CheckApplication(BaseModel):
    """Input schema for offer."""
    chat_message_id: int = Field(..., description="ID of the chat message associated with the recruitment process.")

class CheckApplicationCountTool(BaseTool):
    name: str = "CheckApplicationCountTool"
    description: str = "A tool that checks the number of candidates who have applied for a recruitment process."
    args_schema: Type[BaseModel] = CheckApplication

    def _run(self, chat_message_id: int):
        recruitment = get_object_or_404(Recruitment, id=chat_message_id)
        candidate_count = Candidate.objects.filter(recruitment=recruitment).count()
        
        if candidate_count > 0:
            return f"{candidate_count} applications found."
        else:
            return "No one has applied yet."



class TaskStatusUpdate(BaseTool):
    name: str = "task_status_update"
    description: str = "Updates the task status dynamically to either 'COMPLETED' or 'PENDING' along with the task name and chat message ID."
    args_schema = TaskStatusUpdateSchema  # ✅ Ensure correct argument validation

    def _run(self, task_name: str, status: str, chat_message_id: int,report:str) -> str:
        """
        Updates the task status of the given task_name associated with the chat_message_id.

        Args:
            task_name (str): The name of the task being updated.
            status (str): Must be 'COMPLETED' or 'PENDING'.
            chat_message_id (int): The ID of the chat message associated with the task.

        Returns:
            str: A message confirming the update.
        """
        
        # Fetch the related Recruitment object using chat_message_id
        recruitment = get_object_or_404(Recruitment, id=chat_message_id)
        
        # Get the corresponding RecruitmentTask based on task_name
        recruitment_task = get_object_or_404(RecruitmentTask, recruitment=recruitment, task_name=task_name)
        
        # Update the status of the task
        recruitment_task.status = status
        recruitment_task.save()
        
        # Print and return the result
        print(f"Updated Task: {task_name} | Status: {status} for Recruitment ID: {recruitment.id}")
        return f"Task '{task_name}' for Recruitment ID {recruitment.id} status updated successfully to {status}Report is {report}"


class ResumeFetcherInput(BaseModel):
    """Input schema for ResumeFetcherTool."""
    chat_message_id: int = Field(..., description="ID of the chat message associated with the recruitment process.")

class ResumeFetcherTool(BaseTool):
    """
    Tool to retrieve candidate names and resume file paths from the Candidate model using chat_message_id.
    """
    name: str = "resume_fetcher"
    description: str = "Fetches candidate names and their resume file paths for a given recruitment process."
    args_schema: Type[BaseModel] = ResumeFetcherInput

    def _run(self, chat_message_id: int) -> List[dict]:
        """
        Fetches all candidate resumes linked to a recruitment session.

        Args:
            chat_message_id (int): The ID of the chat message associated with the recruitment.

        Returns:
            List[dict]: A list of candidate dictionaries containing:
                        - "name": Candidate's name
                        - "resume_path": Path to their resume file
        """
        resumes = []
        print(resumes,"sss")
        # Get the Recruitment instance based on chat_message_id
        recruitment = get_object_or_404(Recruitment, id=chat_message_id)

        print(recruitment,"ss11s")
        # Fetch all candidates linked to this recruitment
        candidates = Candidate.objects.filter(recruitment=recruitment)
        print(candidates,"ssss33s")

        if not candidates.exists():
            return [{"error": "No candidates found for this recruitment session."}]

        # Collect candidate details
        for candidate in candidates:
            if candidate.resume:  # Assuming 'resume' is a file path field
                resumes.append({"name": candidate.name, "resume_path": candidate.resume})
            else:
                resumes.append({"name": candidate.name, "resume_path": "No resume available"})

        return resumes




import PyPDF2

class ResumeEvaluatorInput(BaseModel):
    """Input schema for ResumeEvaluatorTool."""
    candidates: List[dict] = Field(..., description="List of candidates with their resume file paths.")
    job_description: str = Field(..., description="Job description to match against resumes.")

class ResumeEvaluatorTool(BaseTool):
    """
    Tool to evaluate multiple resumes against a job description and update the database.
    """
    name: str = "resume_evaluator"
    description: str = "Analyzes resumes and updates the candidate's resume_check field if they match the job description."
    args_schema: Type[BaseModel] = ResumeEvaluatorInput

    def _run(self, candidates: List[dict], job_description: str) -> List[dict]:
     
        results = []
        
        for candidate in candidates:
            resume_path = candidate["resume_path"]
            candidate_name = candidate["name"]

            try:
                with open(resume_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

                match_status = "MATCH" if job_description.lower() in text.lower() else "NO MATCH"

            
                if match_status == "MATCH":
                    Candidate.objects.filter(name=candidate_name).update(resume_check=True)

            except Exception as e:
                match_status = f"Error reading PDF: {str(e)}"

            results.append({
                "name": candidate_name,
                "resume_path": resume_path,
                "status": match_status,
                "resume_check_updated": match_status == "MATCH"
            })
        print(results)
        return results





class ListPDFsInput(BaseModel):
    """Input schema for ListPDFsTool."""
    directory_path: str = Field(..., description="Path to the directory whose PDF files are to be listed.")

class ListPDFsTool(BaseTool):
    """
    Tool to list all PDF file paths in the given directory (non-recursive).
    """
    name: str = "list_pdfs"
    description: str = "Lists all PDF file paths present directly in the given directory."
    args_schema: Type[BaseModel] = ListPDFsInput

    def _run(self, directory_path: str) -> List[str]:
        """
        Lists PDF file paths in the given directory.

        Args:
            directory_path (str): Path to the directory.

        Returns:
            List[str]: A list of PDF file paths in the directory.

        Raises:
            FileNotFoundError: If the directory does not exist.
            ValueError: If the provided path is not a directory.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"The directory at {directory_path} does not exist.")

        if not os.path.isdir(directory_path):
            raise ValueError(f"The path {directory_path} is not a directory.")

        # Collect only PDF file paths directly in the given directory
        pdf_paths = [
            os.path.join(directory_path, file_name)
            for file_name in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, file_name)) and file_name.endswith(".pdf")
        ]

        return pdf_paths


class ATSFetcherInput(BaseModel):
    """Input schema for ATSFetcherTool."""
    chat_message_id: int = Field(..., description="ID of the chat message associated with the recruitment process.")

class ATSFetcherTool(BaseTool):
    """
    Tool to fetch candidates who passed resume screening (`resume_check=True`).
    """
    name: str = "ats_fetcher"
    description: str = "Fetches candidates with resume_check=True for ATS scoring."
    args_schema: Type[BaseModel] = ATSFetcherInput

    def _run(self, chat_message_id: int) -> List[dict]:
        """
        Fetches candidates whose resumes passed initial screening.

        Args:
            chat_message_id (int): ID of the recruitment chat.

        Returns:
            List[dict]: List of candidates with:
                        - "name": Candidate's name
                        - "resume_path": Path to resume
                        - "resume_check": True
        """
        # Retrieve recruitment session
        recruitment = get_object_or_404(Recruitment, id=chat_message_id)

        # Fetch candidates who passed resume screening
        candidates = Candidate.objects.filter(recruitment=recruitment, resume_check=True)

        if not candidates.exists():
            return [{"error": "No candidates passed resume screening."}]

        return [{"name": c.name, "resume_path": c.resume, "resume_check": c.resume_check} for c in candidates]
    


class ATSEvaluatorInput(BaseModel):
    """Input schema for ATSEvaluatorTool."""
    candidates: List[dict] = Field(..., description="List of candidates with resumes to be evaluated.")
    job_description: str = Field(..., description="Job description to calculate ATS score.")

class ATSEvaluatorTool(BaseTool):
    """
    Tool to evaluate ATS scores and update the candidate's `ats_score` field.
    """
    name: str = "ats_evaluator"
    description: str = "Evaluates ATS score and updates the database."
    args_schema: Type[BaseModel] = ATSEvaluatorInput

    def _run(self, candidates: List[dict], job_description: str) -> List[dict]:
        """
        Evaluates ATS scores and updates `ats_score` in the Candidate model.

        Args:
            candidates (List[dict]): List of candidates with "name" and "resume_path".
            job_description (str): Job description for ATS scoring.

        Returns:
            List[dict]: List of candidates with ATS scores.
        """
        results = []

        for candidate in candidates:
            resume_path = candidate["resume_path"]
            candidate_name = candidate["name"]

            try:
                with open(resume_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

                # Simulate ATS scoring (Example: Score between 50-100 based on text similarity)
                ats_score = random.randint(50, 100)  # Replace with real NLP-based scoring logic

                # ✅ Update ATS score in the database
                Candidate.objects.filter(name=candidate_name).update(ats_score=ats_score)

            except Exception as e:
                ats_score = 0  # Default to 0 if there's an error

            results.append({
                "name": candidate_name,
                "resume_path": resume_path,
                "ats_score": ats_score
            })

        return results    


class InterviewSlotInput(BaseModel):
    """Input schema for InterviewSlotCheckerTool."""
    chat_message_id: int = Field(..., description="ID of the chat message associated with the recruitment process.")

class InterviewSlotCheckerTool(BaseTool):
    """
    Tool to check if there are available interview slots for a given candidate.
    """
    name: str = "interview_slot_checker"
    description: str = "Checks available interview slots for the candidate and returns a booking link."
    args_schema: Type[BaseModel] = InterviewSlotInput

    def _run(self, chat_message_id: int) -> dict:
        """
        Checks if there are available interview slots for the candidate.

        Args:
            chat_message_id (int): ID of the chat message.

        Returns:
            dict: Message indicating slot availability and booking link.
        """
        try:
            # Get the recruitment using chat_message_id
            recruitment = get_object_or_404(Recruitment, id=chat_message_id)

            # Check if there are any available slots
            available_slots = Schedule.objects.filter(recruitment=recruitment)

            if available_slots.exists():
                return {
                    "message": "Slot is available for booking.",
                    
                }
            else:
                recruitment.session.save_message_to_mongo({
                    "Type": "text",
                    "message": f"No interview slot selected yet. Add available slot for interview process:" f"{settings.SITE_URL}/o/recruitment/{recruitment.id}/add_schedule/",
                    "task_name": "outreach link",
                    "user": "AI",
                     },task_name="outreach link")

                return {
                    "message": f"No interview slot selected yet. Add available slot for interview process: ",
                               f"{settings.SITE_URL}/o/recruitment/{recruitment.id}/add_schedule/"
                    "add_slot_url": f"{settings.SITE_URL}/o/recruitment/{recruitment.id}/add_schedule/"
                }

        except Exception as e:
            return {"error": str(e)}
        
        
class TaskStatusCheckerSchema(BaseModel):
    task_name: str = Field(..., description="The name of the task whose status needs to be checked.")
    chat_message_id: int = Field(..., description="The ID of the chat message associated with the task.")

class TaskStatusCheckerTool(BaseTool):
    name: str = "task_status_checker"
    description: str = "Checks the current status of a task ('COMPLETED' or 'PENDING') based on the task name and chat message ID."
    args_schema:Type[BaseModel]= TaskStatusCheckerSchema  # ✅ Ensure correct type annotation

    def _run(self, task_name: str, chat_message_id: int) -> str:
        """
        Retrieves the current status of a task.

        Args:
            task_name (str): The name of the task being checked.
            chat_message_id (int): The ID of the chat message associated with the task.

        Returns:
            str: The task status (COMPLETED/PENDING) or an error message.
        """

        # Fetch the related Recruitment object using chat_message_id
        recruitment = get_object_or_404(Recruitment, id=chat_message_id)
        
        # Get the corresponding RecruitmentTask based on task_name
        recruitment_task = get_object_or_404(RecruitmentTask, recruitment=recruitment, task_name=task_name)
        
        # Retrieve the status of the task
        task_status = recruitment_task.status
        task_result = recruitment_task.final_report
        
        # Print and return the result
        print(f"Checked Task: {task_name} | Status: {task_status} for Recruitment ID: {recruitment.id}")
        return f"Task '{task_name}' for Recruitment ID {recruitment.id} is currently {task_status}. task Result is{task_result} "