from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Literal
from django.shortcuts import get_object_or_404
from crewai.tools import BaseTool

from typing import Type
from hr_crew.models import Onboarding, EmployeeOnboardingTask,EmployeeDocuments
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import BaseModel, EmailStr
import requests
import datetime
import json
import logging
from typing import Any, Type
import os
from django.conf import settings

from typing import Dict
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from organizations.models import Organization,OrganizationStaff,SMTPConfiguration,ChatMessage
from django.core.exceptions import ObjectDoesNotExist

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
    

class OnboardingPlan(BaseModel):
    task_name: str = Field(..., description="The name of the task being updated.")
    status: Literal["COMPLETED", "PENDING"] = Field(..., description="Task status must be 'COMPLETED' or 'PENDING' or 'FAILED'.")
    chat_message_id: int = Field(..., description="The ID of the chat message associated with the task.")
    onboarding_plan: str = "Generated onboarding plan"

class CreateOnboardingPlanTool(BaseTool):
    name: str = "create_onboarding_plan"
    description: str = "Generates a structured onboarding plan for a new hire based on role, department, and start date."
    args_schema: Type[BaseModel] = OnboardingPlan  

    def _run(self,onboarding_plan) -> str:
        """
        Generates a structured onboarding plan for a new employee.

        Args:
            newhireinfo (Dict): Dictionary containing new hire details.

        Returns:
            str: A structured onboarding schedule.
        """
       
        
        
        return onboarding_plan
    
    def _run2(self, task_name: str, status: str, chat_message_id: int) -> str:
       
        
        onboarding = get_object_or_404(Onboarding, id=chat_message_id)
        
        # # Get the corresponding RecruitmentTask based on task_name
        onboarding_task = get_object_or_404(EmployeeOnboardingTask, onboarding=onboarding, task_name=task_name)
        
        # # Update the status of the task
        onboarding_task.status = status
        onboarding_task.save()
        
        # Print and return the result
        print(f"Updated Task: {task_name} | Status: {status} for Recruitment ID:")
        return f"Task '{task_name}' for Recruitment ID status updated successfully to {status}"    


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def _save_results_to_file(content: str) -> None:
    """Saves the search results to a file."""
    try:
        filename = f"search_results_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(filename, "w") as file:
            file.write(content)
        logger.info(f"Results saved to {filename}")
    except IOError as e:
        logger.error(f"Failed to save results to file: {e}")


@tool
def training_schedule_generator_tool(role: str) -> str:
    """
    Generates a training schedule tailored to a specific role.

    Args:
        role (str): The role of the new hire.

    Returns:
        str: A detailed training schedule for the specified role.
    """
    # Placeholder implementation
    return f"Training schedule generated for the role: {role}."




@tool
def training_resource_manager_tool(role: str) -> str:
    """
    Provides access to training resources for a specific role.

    Args:
        role (str): The role of the new hire.

    Returns:
        str: A list of training resources available for the specified role.
    """
    # Placeholder implementation
    return f"Training resources prepared for the role: {role}."



@tool
def announcement_creator_tool(new_hire_name: str, new_hire_role: str, start_date: str, team_name: str) -> str:
    """
    Creates and sends a personalized announcement message about the new hire.

    Args:
        new_hire_name (str): The name of the new hire.
        new_hire_role (str): The role of the new hire.
        start_date (str): The start date of the new hire.
        team_name (str): The name of the team to which the new hire is joining.

    Returns:
        str: A confirmation message about the announcement being sent.
    """
    announcement = (
        f"Team {team_name},\n\n"
        f"Please welcome {new_hire_name}, our new {new_hire_role}, who will be joining us on {start_date}. "
        f"We're excited to have them on board and look forward to their contributions!\n\n"
        "Best regards,\nHR Team"
    )
    # Placeholder for sending the announcement (email or internal system)
    return f"Announcement sent: {announcement}"




@tool
def meeting_scheduler_tool(new_hire_name: str, team_name: str, meeting_date: str) -> str:
    """
    Schedules a meeting or event to introduce the new hire to their team.

    Args:
        new_hire_name (str): The name of the new hire.
        team_name (str): The name of the team.
        meeting_date (str): The scheduled date for the meeting.

    Returns:
        str: A confirmation message about the meeting being scheduled.
    """
    meeting_details = (
        f"Meeting scheduled for {team_name} to welcome {new_hire_name} on {meeting_date}. "
        "The meeting details have been shared with all participants."
    )
    # Placeholder for meeting scheduling logic
    return f"Meeting scheduled: {meeting_details}"


class TaskStatusUpdateSchema(BaseModel):
    task_name: str = Field(..., description="The name of the task being updated.")
    status: Literal["COMPLETED", "PENDING"] = Field(..., description="Task status must be 'COMPLETED' or 'PENDING' or 'FAILED'.")
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")

class TaskStatusUpdate(BaseTool):
    name: str = "task_status_update"
    description: str = "Updates the task status dynamically to either 'COMPLETED' or 'PENDING' along with the task name and chat message ID."
    args_schema = TaskStatusUpdateSchema  

    def _run(self, task_name: str, status: str, instance_id: int) -> str:
       
        
        onboarding = get_object_or_404(Onboarding, id=instance_id)
        
        # # Get the corresponding RecruitmentTask based on task_name
        onboarding_task = get_object_or_404(EmployeeOnboardingTask, onboarding=onboarding, task_name=task_name)
        
        # # Update the status of the task
        onboarding_task.status = status
        onboarding_task.save()
        
        # Print and return the result
        print(f"Updated Task: {task_name} | Status: {status} for Recruitment ID:")
        return f"Task '{task_name}' for Recruitment ID status updated successfully to {status}"    
    


# Define the input schema for the tool
class EmailSchema(BaseModel):
    employee_name: str
    recipient_email: EmailStr
    subject: str
    content: str
    chat_message_id: int = Field(..., description="The CHAT MESSAGE ID of the chat message associated with the task.")


class SendEmailTool(BaseTool):
    name: str = "send_email_tool"
    description: str = "Sends an email to an employee with a subject and content."

    args_schema: Type[BaseModel] = EmailSchema


    def _run(self, employee_name: str, recipient_email: str, subject: str, content: str, chat_message_id: int) -> str:
        """
        Sends an email using the SMTP details of the organization linked to the chat message ID.

        Args:
            employee_name (str): The name of the recipient.
            recipient_email (str): The email address of the recipient.
            subject (str): The subject of the email.
            content (str): The body of the email.
            chat_message_id (int): The ID of the chat message to fetch SMTP details.

        Returns:
            str: Confirmation message indicating success or failure.
        """

        try:
            # Fetch SMTP details based on chat_message_id
            smtp_details = get_smtp_details(chat_message_id)
            print("email",smtp_details)

            if "error" in smtp_details:
                return f"❌ Error: {smtp_details['error']}"

            smtp_host = smtp_details["smtp_host"]
            smtp_port = smtp_details["smtp_port"]
            sender_email = smtp_details["sender_email"]
            password = smtp_details["password"]

            if not smtp_host or not smtp_port or not sender_email or not password:
                return "❌ Error: Incomplete SMTP configuration."

            # Prepare email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))

            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)

            return f"✅ Email successfully sent to {employee_name} at {recipient_email}"

        except ObjectDoesNotExist:
            return "❌ Error: SMTP details not found for the given chat message ID."
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
        



class SerperDevToolSchema(BaseModel):
    """Input for SerperDevTool."""

    search_query: str = Field(
        ..., description="Mandatory search query you want to use to search the internet"
    )


class SerperDevTool(BaseTool):
    name: str = "Search the internet with Serper"
    description: str = (
        "A tool that can be used to search the internet with a search_query. "
        "Supports different search types: 'search' (default), 'news'"
    )
    args_schema: Type[BaseModel] = SerperDevToolSchema
    base_url: str = "https://google.serper.dev"
    n_results: int = 10
    save_file: bool = False
    search_type: str = "search"

    def _get_search_url(self, search_type: str) -> str:
        """Get the appropriate endpoint URL based on search type."""
        search_type = search_type.lower()
        allowed_search_types = ["search", "news"]
        if search_type not in allowed_search_types:
            raise ValueError(
                f"Invalid search type: {search_type}. Must be one of: {', '.join(allowed_search_types)}"
            )
        return f"{self.base_url}/{search_type}"

    def _process_knowledge_graph(self, kg: dict) -> dict:
        """Process knowledge graph data from search results."""
        return {
            "title": kg.get("title", ""),
            "type": kg.get("type", ""),
            "website": kg.get("website", ""),
            "imageUrl": kg.get("imageUrl", ""),
            "description": kg.get("description", ""),
            "descriptionSource": kg.get("descriptionSource", ""),
            "descriptionLink": kg.get("descriptionLink", ""),
            "attributes": kg.get("attributes", {}),
        }

    def _process_organic_results(self, organic_results: list) -> list:
        """Process organic search results."""
        processed_results = []
        for result in organic_results[: self.n_results]:
            try:
                result_data = {
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position"),
                }

                if "sitelinks" in result:
                    result_data["sitelinks"] = [
                        {
                            "title": sitelink.get("title", ""),
                            "link": sitelink.get("link", ""),
                        }
                        for sitelink in result["sitelinks"]
                    ]

                processed_results.append(result_data)
            except KeyError:
                logger.warning(f"Skipping malformed organic result: {result}")
                continue
        return processed_results

    def _process_people_also_ask(self, paa_results: list) -> list:
        """Process 'People Also Ask' results."""
        processed_results = []
        for result in paa_results[: self.n_results]:
            try:
                result_data = {
                    "question": result["question"],
                    "snippet": result.get("snippet", ""),
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                }
                processed_results.append(result_data)
            except KeyError:
                logger.warning(f"Skipping malformed PAA result: {result}")
                continue
        return processed_results

    def _process_related_searches(self, related_results: list) -> list:
        """Process related search results."""
        processed_results = []
        for result in related_results[: self.n_results]:
            try:
                processed_results.append({"query": result["query"]})
            except KeyError:
                logger.warning(f"Skipping malformed related search result: {result}")
                continue
        return processed_results

    def _process_news_results(self, news_results: list) -> list:
        """Process news search results."""
        processed_results = []
        for result in news_results[: self.n_results]:
            try:
                result_data = {
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result.get("snippet", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", ""),
                    "imageUrl": result.get("imageUrl", ""),
                }
                processed_results.append(result_data)
            except KeyError:
                logger.warning(f"Skipping malformed news result: {result}")
                continue
        return processed_results

    def _make_api_request(self, search_query: str, search_type: str) -> dict:
        """Make API request to Serper."""
        search_url = self._get_search_url(search_type)
        payload = json.dumps({"q": search_query, "num": self.n_results})
        headers = {
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "content-type": "application/json",
        }

        response = None
        try:
            response = requests.post(
                search_url, headers=headers, json=json.loads(payload), timeout=10
            )
            response.raise_for_status()
            results = response.json()
            if not results:
                logger.error("Empty response from Serper API")
                raise ValueError("Empty response from Serper API")
            return results
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to Serper API: {e}"
            if response is not None and hasattr(response, "content"):
                error_msg += f"\nResponse content: {response.content}"
            logger.error(error_msg)
            raise
        except json.JSONDecodeError as e:
            if response is not None and hasattr(response, "content"):
                logger.error(f"Error decoding JSON response: {e}")
                logger.error(f"Response content: {response.content}")
            else:
                logger.error(
                    f"Error decoding JSON response: {e} (No response content available)"
                )
            raise

    def _process_search_results(self, results: dict, search_type: str) -> dict:
        """Process search results based on search type."""
        formatted_results = {}

        if search_type == "search":
            if "knowledgeGraph" in results:
                formatted_results["knowledgeGraph"] = self._process_knowledge_graph(
                    results["knowledgeGraph"]
                )

            if "organic" in results:
                formatted_results["organic"] = self._process_organic_results(
                    results["organic"]
                )

            if "peopleAlsoAsk" in results:
                formatted_results["peopleAlsoAsk"] = self._process_people_also_ask(
                    results["peopleAlsoAsk"]
                )

            if "relatedSearches" in results:
                formatted_results["relatedSearches"] = self._process_related_searches(
                    results["relatedSearches"]
                )

        elif search_type == "news":
            if "news" in results:
                formatted_results["news"] = self._process_news_results(results["news"])

        return formatted_results

    def _run(self, **kwargs: Any) -> Any:
        """Execute the search operation."""
        search_query = kwargs.get("search_query") or kwargs.get("query")
        search_type = kwargs.get("search_type", self.search_type)
        save_file = kwargs.get("save_file", self.save_file)

        results = self._make_api_request(search_query, search_type)

        formatted_results = {
            "searchParameters": {
                "q": search_query,
                "type": search_type,
                **results.get("searchParameters", {}),
            }
        }

        formatted_results.update(self._process_search_results(results, search_type))
        formatted_results["credits"] = results.get("credits", 1)

        if save_file:
            _save_results_to_file(json.dumps(formatted_results, indent=2))

        return formatted_results        


class CreateTrainingPlanTool(BaseTool):
    name: str = "create_training_plan"
    description: str = "Generates a structured training plan for a new hire based on their role and training needs."

    def _run(self, newhireinfo: Dict) -> str:
        """
        Generates a customized training plan for a new employee.

        Args:
            newhireinfo (Dict): Dictionary containing new hire details.

        Returns:
            str: A structured training schedule.
        """
        first_name = newhireinfo.get('first_name', 'N/A')
        role = newhireinfo.get('role', 'N/A')
        department = newhireinfo.get('department', 'N/A')
        start_date = newhireinfo.get('start_date', 'N/A')

        training_plan = f"""
        **Training Plan for {first_name} (Role: {role}, Department: {department})**

        - **Week 1:** Introduction to company culture, policies, and tools.
        - **Week 2:** Hands-on role-specific training with mentors.
        - **Week 3:** Advanced training on key responsibilities.
        - **Week 4:** Assessment and final review.

        **Start Date:** {start_date}
        **Assigned Mentor:** {newhireinfo.get('mentor', 'TBD')}
        """
        return training_plan


class VerifyDocumentSchema(BaseModel):
    chat_message_id: int = Field(..., description="The ID of the chat message associated with the task.")
    employee_name: str
    recipient_email: EmailStr


class VerifyDocumentTool(BaseTool):
    name: str = "verify_document"
    description: str = "Verifies if a document has been submitted and processed successfully."
    args_schema: Type[BaseModel] = VerifyDocumentSchema  # Fix: Explicit type annotation

    def _run(self,chat_message_id: int, employee_name: str, recipient_email: str) -> str:
        subject='Document Verifications'
        content=f"{settings.SITE_URL}/o/upload-documents/{chat_message_id}/"
        print(f"Verifying document with ID: {chat_message_id}")
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)

            return f"✅ Email successfully sent to {employee_name} at {recipient_email}"

        except Exception as e:
            return f"❌ Error sending email to {recipient_email}: {str(e)}"


class DocumentSchema(BaseModel):
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")


class VerifyUploadedDocumentTool(BaseTool):
    name: str = "verify_document"
    description: str = "Verifies if a document has been submitted and processed successfully."
    args_schema: Type[BaseModel] = DocumentSchema  # Fix: Explicit type annotation

    def _run(self,instance_id: int) -> str:
       
        try:
            # Retrieve the onboarding record based on chat_message_id
            onboarding = Onboarding.objects.filter(id=instance_id).first()
            if not onboarding:
                return f"❌ No onboarding record found for chat_message_id: {instance_id}"

            # Retrieve the employee document verification status
            employee_document = EmployeeDocuments.objects.filter(onboarding=onboarding).first()
            
            if not employee_document:
                return f"⚠️ Employee not upload any documents"
            
            employee_document.refresh_from_db() 
            # Check if documents are verified
            if employee_document.verified:
                return f"✅ Document verification completed successfully for {onboarding.employee_name}."
            else:
                return f"⚠️ Document verification pending for {onboarding.employee_name}. Please verify using {settings.SITE_URL}/o/employee-documents/{chat_message_id}/"

        except Exception as e:
            return f"❌ Error verifying document for onboarding ID {instance_id}: {str(e)}"
    
    






