from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type, ClassVar
import requests

from django.core.exceptions import ObjectDoesNotExist
from organizations.models import Organization,OrganizationStaff,SMTPConfiguration,ChatMessage,LinkedInAPIKey
# Email credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "alimirsa123@gmail.com"
EMAIL_PASSWORD = "myxz onbb acaf bnot"

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
    
class JobPostingInput(BaseModel):
    job_posting: str = Field(..., description="The job posting created by the agent.")
    instance_id: int = Field(..., description="The INSTANCE ID associated with the task.")
    

class JobPostingTool(BaseTool):
    """
    Tool to post job descriptions on LinkedIn.
    """
    name: str = "Job Posting"
    description: str = "Posts a job description to LinkedIn."
    args_schema: Type[BaseModel] = JobPostingInput

    LINKEDIN_API_URL: ClassVar[str] = "https://api.linkedin.com/v2/ugcPosts"  # Fixed issue by using ClassVar

   
    def _run(self, job_posting: str, instance_id: int) -> str:
        """
        Processes and posts a job description on LinkedIn.

        Args:
            job_posting (str): The job description to be posted.
            instance_id (int): The instance ID to retrieve the LinkedIn access token.

        Returns:
            str: Confirmation message if the job posting is successful.
        """
        # Get LinkedIn access token
        token_response = get_linkedin_access_token(instance_id)

        if "error" in token_response:
            return f"Failed to retrieve access token: {token_response['error']}"

        access_token = token_response.get("access_token")
        
        if not access_token:
            return "LinkedIn access token is missing."

        print("Received job_posting:", job_posting)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        payload = {
            "author": "urn:li:person:YpUWNYS6u-",  # TODO: Replace with a dynamic LinkedIn profile URN
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": job_posting
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        try:
            response = requests.post(self.LINKEDIN_API_URL, headers=headers, json=payload)

            if response.status_code == 201:
                return "Job posting successfully published on LinkedIn."
            else:
                return f"Failed to post job. Status Code: {response.status_code}, Error: {response.text}"

        except requests.RequestException as e:
            return f"Request failed: {str(e)}"
    
class JobPostGeneratorInput(BaseModel):
    job_title: str = Field(..., description="Title of the job position")
    job_requirement: str = Field(..., description="Job requirements and responsibilities")
    company_name: str = Field(..., description="Name of the company posting the job")
    location: str = Field(..., description="Job location")
    apply_link: str = Field(..., description="Application link for the job")

class JobPostGeneratorTool(BaseTool):
    """
    Tool to generate job descriptions based on input details.
    """
    name: str = "Job Post Generator"
    description: str = "Generates a job posting based on job details."
    args_schema: Type[BaseModel] = JobPostGeneratorInput

    def _run(self, job_title: str, job_requirement: str, company_name: str, location: str, apply_link: str) -> str:
        """
        Generates a job posting.

        Args:
            job_title (str): Job title.
            job_requirement (str): Job requirements.
            company_name (str): Name of the company.
            location (str): Location of the job.
            apply_link (str): Application link.

        Returns:
            str: A formatted job posting.
        """
        job_post = f"""
        **{job_title} at {company_name} ({location})**  

        **Job Description:**  
        {job_requirement}  

        **Location:** {location}  

        **How to Apply:**  
        Apply here: [Apply Now]({apply_link})
        """
        return job_post.strip()