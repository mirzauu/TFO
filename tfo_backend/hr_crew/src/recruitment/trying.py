from pydantic import BaseModel, Field
from typing import Optional
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, PDFSearchTool,RagTool
from hr_crew.src.recruitment.tools.custom_tool import ListPDFsTool,TaskStatusUpdate,CheckApplicationCountTool,ResumeFetcherTool,ResumeEvaluatorTool,ATSFetcherTool,ATSEvaluatorTool,InterviewSlotCheckerTool,OfferLetterSenderTool,TaskStatusCheckerTool
from hr_crew.src.recruitment.tools.email import EmailSenderTool,InterviewNotificationTool
from hr_crew.src.recruitment.tools.job_posting import JobPostingTool,JobPostGeneratorTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from organizations.models import ChatMessage
from django.conf import settings
import re
# Load environment variables
from typing import Tuple, Any
from tfo_backend.mongodb import chat_collection,db

load_dotenv()

import re
from pymongo import MongoClient





chat_message_id=40

def update_chat_id(id):
    global chat_message_id
    chat_message_id = id
    


def update_task_status(result,task_name,chat_message_id):
    # Ensure result is a string
    if not isinstance(result, str):
        result = str(result)

    chat_message_id = chat_message_id

    cleaned_result = re.sub(r"Task Name: \[.*?\]\n- Status: \[.*?\]\n- chat_message_id: \d+\n", "", result, flags=re.MULTILINE).strip()

    try:
        if chat_message_id:
            recruitment = get_object_or_404(Recruitment, id=chat_message_id)
            recruitment_task = get_object_or_404(RecruitmentTask, recruitment=recruitment, task_name=task_name)
            # Update the status of the task
            recruitment_task.final_report = cleaned_result

            if task_name in ["Job Posting", "Interview Preparation"]:
                recruitment_task.status = "COMPLETED"

            recruitment_task.save()

    except Exception as e:
            print(f"Error updating task status for {task_name} - {task_name}: {e}")    




job_posting_specialist = Agent(
    role="Job Posting Specialist",
    goal="Create engaging and accurate job descriptions.",
    verbose=True,
    allow_delegation=False,
    
    backstory=(
        """
        - A seasoned HR professional with a knack for storytelling, 
          who has spent years crafting compelling job ads.
        - You focus on creating job descriptions that attract the right 
          candidates by using creative and precise language.
        """
    )
)

job_posting_specialist_task = Task(
    description=(
        """
        Write job descriptions for {job_title} and {job_requirement} at {company_name} in {location} that attract qualified candidates. 
        Ensure they are engaging, accurate, and reflect the requirements of the role.
        To apply for the post, ask them to Apply using the link {apply_link}.

        create the job posting.
        
        """
    ),
    expected_output="""
        **Job Posting Created**
        give the well structured generated job discription  
        
     
    """,
    agent=job_posting_specialist,
    tools=[],
    callback=lambda result: update_task_status(result, task_name="Job Posting", chat_message_id=chat_message_id),
)

sourcing_automation_agent = Agent(
    role="Sourcing Automation Agent",
    goal="Streamline job postings across various platforms.",
    verbose=True,
    allow_delegation=False,
    tools=[JobPostingTool()],
    backstory=(
        """
        - A tech-savvy recruiter who loves automation and has experience 
          in multi-platform posting strategies.
        - You are highly skilled at managing and automating job postings 
          across different recruitment platforms.
        """
    ),
)

sourcing_automation_agent_task = Task(
    description=(
        """
        Automate the posting of job ads on multiple job boards and social media.
        Ensure postings are accurate and live on all specified platforms simultaneously.

        After executing the JobPostingTool, update the task status using the TaskStatusUpdate tool.
        - If the job postings are successfully live, set the status to 'COMPLETED'.
        - If the job postings fail or require further action, set the status to 'PENDING'.

        The Details Are:
        - Task Name: [Sourcing Automation]
        - Status: [COMPLETED/PENDING]
        - chat_message_id: {chat_message_id}
        - INSTANCE ID: {instance_id}
        """
    ),
    expected_output="""
        **Job Postings Automated**

        *Job Posting Details:*
        - **Platforms:** Various job boards and social media
        - **Posting Status:** Successfully live or requires further action
        - **Automation Tool Used:** JobPostingTool

        *Task Status Update:*
        - **Task Name:** Sourcing Automation
        - **Status:** [COMPLETED/PENDING]
    """,
    tools=[TaskStatusCheckerTool(),JobPostingTool(), TaskStatusUpdate(result_as_answer=True)],
    agent=sourcing_automation_agent,
   
)


application_tracking_agent = Agent(
    name="Application Tracking Agent",
    role="Track and report job application status",
    goal="Monitor application numbers and update task status accordingly",
    backstory="An automated tracker that continuously monitors application pipelines and updates statuses in real-time",
    verbose=True
)

application_tracking_task = Task(
    description=(
        """
        Monitor and track applications for open job positions in real-time.
        Use CheckApplicationCountTool to get current application numbers.
        
        After checking applications, update task status using TaskStatusUpdate:
        - If applications exist (count > 0), set status to 'COMPLETED'
        - If no applications (count = 0), set status to 'PENDING'

     
        - [Application Count Message]
        - Task Name: [Application Tracking]
        - Status: [COMPLETED/PENDING]
        - chat_message_id: {chat_message_id}
        """
    ),
    expected_output="""
        **Application Tracking Update**

        *Application Status:*
        - Total Applications Received: X persons applied for this job / No update
      

        
    """,
    tools=[CheckApplicationCountTool(), TaskStatusUpdate(result_as_answer=True)],
    agent=application_tracking_agent,
    callback=lambda result: update_task_status(result, task_name="Application Tracking", chat_message_id=chat_message_id),

)

resume_screening_agent = Agent(
    role="Resume Screening Agent",
    goal="Efficiently screen resumes based on set criteria.",
    verbose=True,
    allow_delegation=True,
    tools=[ListPDFsTool(),PDFSearchTool()],
    backstory=(
        """
        - An analytical expert with a background in data analysis and recruitment, 
          skilled at identifying top talent quickly.
        - You utilize data-driven approaches to screen resumes efficiently.
        """
    ),
)
from typing import Tuple, Any

def resume_screening_guardrail(task_output) -> Tuple[bool, Any]:
    """
    Validates the application count before proceeding to resume screening.
    - If `application_count > 0`, proceed with resume screening.
    - If `application_count == 0`, stop execution and mark task as "PENDING".
    """
    
    print("DEBUG: TaskOutput structure:", task_output)  # Debugging line

    # Handle dictionary format
    if isinstance(task_output, dict):
        application_count = task_output.get("application_count", None)
    else:
        # Handle object format
        try:
            application_count = getattr(task_output, "application_count", None)
        except AttributeError:
            return False, "Error: Unable to retrieve application count."

    if application_count is None:
        return False, "Error: Application count is missing in TaskOutput."

    if application_count > 0:
        return True, f"Proceeding with resume screening. {application_count} applications found."
    else:
        return False, "No applications found. Resume screening task is set to PENDING."


resume_screening_agent_task = Task(
    description=(
        """
        It retrieves multiple resumes, evaluates them against the {job_title}, and updates the task status.

        **Process:**
        - Use ResumeFetcherTool to retrieve **all candidate names and resume file paths** .
        - Use ResumeEvaluatorTool to analyze **each resume** and determine if it matches the job description.
        - Update the task status accordingly.

        **Task Execution Rules:**
        
        - If ResumeFetcherTool contains no resumes, set the status to "PENDING" and stop execution.
        - If the task fails at any stage, update the status to "PENDING."
        - If successful, update the task status to "COMPLETED."

        The Details Are:
        - Task Name: [Resume Screening]
        - Status: [COMPLETED/PENDING]
        - chat_message_id: {chat_message_id}
    """
    ),
    expected_output="""
        **Resume Screening Results**

        *Candidate Evaluations:*
         - *Matching Candidates:*
          - "name": "John Doe", "resume_path": "path/to/resume.pdf", "status": "MATCH"
          - "name": "Jane Smith", "resume_path": "path/to/resume.pdf", "status": "NO MATCH"
        
        *Task Status Update:*
        - Resume Directory Status: {resume_directory} is empty → Task set to "PENDING"
        - Final Task Status: [COMPLETED/PENDING]
    """,
    agent=resume_screening_agent,
    tools=[ResumeFetcherTool(), ResumeEvaluatorTool(result_as_answer=True), TaskStatusUpdate()],
       callback=lambda result: update_task_status(result, task_name="Resume Screening", chat_message_id=chat_message_id),
        guardrail=resume_screening_guardrail, 

 

)

ats_manager = Agent(
    role="ATS Manager",
    goal="Rank resumes in a directory based on a specific requirement.",
    verbose=True,
    allow_delegation=True,
    tools=[],
    backstory=(
        """
        - A data management specialist who excels at organizing and evaluating resumes.
        - You ensure that resumes are ranked and sorted based on job-specific requirements.
        """
    ),
)

# Define the resume ranking task

ats_manager_task = Task(
    description=(
        """
        It evaluates ATS scores for candidates who passed resume screening.

        **Process:**
        - Use ATSFetcherTool to retrieve candidates where `resume_check=True`.
        - Use ATSEvaluatorTool to calculate ATS scores and update the database.
        - Update the task status accordingly.

        **Task Execution Rules:**
        - This task will execute only after "Resume Screening" is marked as "COMPLETED."
        - If no candidates have `resume_check=True`, set the status to "PENDING" and stop execution.
        - If the task fails at any stage, update the status to "PENDING."
        - If successful, update the task status to "COMPLETED."

        **Task Details:**
        - **Task Name:** ATS Manager
        - **Status:** [COMPLETED/PENDING]
        - **chat_message_id:** {chat_message_id}
        """
    ),
    expected_output="""
        **ATS Evaluation Results**

        *Candidate ATS Scores:*
        - Evaluated Candidates:
          - "name": "John Doe", "resume_path": "path/to/resume.pdf", "ats_score": 85
          - "name": "Jane Smith", "resume_path": "path/to/resume.pdf", "ats_score": 72

        *Task Status Update:*
        - Candidates Availability: No candidates with `resume_check=True` → Task set to "PENDING"
        - Final Task Status: [COMPLETED/PENDING]
    """,
    agent=ats_manager,
    tools=[TaskStatusCheckerTool(), ATSFetcherTool(), ATSEvaluatorTool(), TaskStatusUpdate()],
    callback=lambda result: update_task_status(result, task_name="ATS Manager", chat_message_id=chat_message_id),
)

candidate_outreach_specialist = Agent(
    role="Candidate Outreach Specialist",
    goal="Personalize communication with candidates efficiently.",
    verbose=True,
    allow_delegation=False,
    tools=[EmailSenderTool()],
    backstory=(
        """
        - A former recruiter who understands the importance of candidate experience 
          and values personalized outreach.
        - You ensure each candidate is reached out to in a personalized and meaningful way.
        """
    ),
)

candidate_outreach_specialist_task = Task(
    description=(
        """
        Automate email communication with candidates based on interview slot availability.
        "This task will execute only after "ATS Manager" is marked as "COMPLETED.""

        **Process:**    
        - Use InterviewSlotCheckerTool to check if a candidate has an available interview slot.
        - If no slot is available, **set task status using TaskStatusUpdate to "PENDING"** and stop execution.
        - If a slot is available:
          - Generate a personalized email containing the candidate's name and interview booking link.
          - Use EmailSenderTool to send the email.
        - Update the task status accordingly using TaskStatusUpdate.

        ***task status should be updated using TaskStatusUpdate tool.***

        **Task Execution Rules:**
        - If "ATS Manager" is PENDING, return the task status and stop execution.
        - If no interview slots are found, set the status using TaskStatusUpdate to "PENDING."
        - If the email fails to send, set the status using TaskStatusUpdate to "PENDING."
        - If the email is successfully sent, update the task status using TaskStatusUpdate to "COMPLETED."
        - task status should be updated using TaskStatusUpdate tool.

        **Task Details:**
        - **Task Name:** Candidate Outreach
        - **Status:** [COMPLETED/PENDING]
        - **chat_message_id:** {chat_message_id}
        - **INSTANCE ID:** {instance_id} 
        """
    ),
    expected_output="""

        **Candidate Outreach Result**


        *Interview Slot Availability:*
        - Status: [Available/Not Available]
        - InterviewSlotCheckerTool Output: [Tool output here]

        *Email Communication:*
        - Candidate Name: [Candidate's Name]
        - nterview Booking Link: [Generated link]
        - Email Sent Status: [Success/Failure]

        *Task Status Update:*
        - Task Status: [COMPLETED/PENDING]
    """,
    agent=candidate_outreach_specialist,
    tools=[TaskStatusCheckerTool(), InterviewSlotCheckerTool(), EmailSenderTool(), TaskStatusUpdate()],
        callback=lambda result: update_task_status(result, task_name="Candidate Outreach", chat_message_id=chat_message_id),

)


interview_coordinator = Agent(
    role="Interview Coordinator",
    goal="Facilitate seamless interview scheduling.",
    verbose=True,
    allow_delegation=False,
    tools=[],
    backstory=(
        """
        - A highly organized individual with a background in logistics, 
          ensuring that all parties are aligned for interviews.
        - You manage the logistics and coordination of interview schedules.
        """
    ),
)
interview_coordinator_task = Task(
    description=(
        """
        ### This task will execute only after "Candidate Outreach Specialist" is marked as "COMPLETED." ###
        Coordinate schedules between candidates and hiring managers to set up interviews. 
        Confirm all scheduled interviews with both parties.


        **Process:**
        - This task will execute only after "Candidate Outreach" is marked as "COMPLETED."
        - Use InterviewNotificationTool to check booked slots.
        - If no interviews are booked:
          - Return an appropriate message.
          - Update task status to "PENDING."
        - If interviews are successfully scheduled:
          - Confirm with both candidates and hiring managers.
          - Update task status to "COMPLETED."

        **Task Execution Rules:**
        - If "Candidate Outreach" is PENDING, return the task status and stop execution.
        - If no meetings are scheduled, update status to "PENDING."
        - If confirmations fail, update status to "PENDING."
        - If interviews are successfully scheduled and confirmed, update status to "COMPLETED."

        **Task Details:**
        - **Task Name:** Interview Coordinator
        - **Status:** [COMPLETED/PENDING]
        - **chat_message_id:** {chat_message_id}
        - **INSTANCE ID:** {instance_id}
        """
    ),
    expected_output="""
        **Interview Scheduling Result**


        *Interview Slot Status:*
        - Scheduled Interviews: [List of scheduled interviews]
        - interviewNotificationTool Output: [Tool output here]

        *Confirmation Details:*
        - Candidates Notified: [Yes/No]
        - Hiring Managers Notified: [Yes/No]

        *Task Status Update:*
        - Task Status: [COMPLETED/PENDING]
    """,
    agent=interview_coordinator,
    tools=[TaskStatusCheckerTool(), InterviewNotificationTool(), TaskStatusUpdate()],
        callback=lambda result: update_task_status(result, task_name="Interview Coordinator", chat_message_id=chat_message_id),

)

interview_preparation_agent = Agent(
    role="Interview Preparation Agent",
    goal="Generate relevant interview questions for roles.",
    verbose=True,
    allow_delegation=True,
    tools=[SerperDevTool()],
    backstory=(
        """
        - A recruitment strategist with extensive knowledge of various industries, 
          adept at formulating targeted questions.
        - You craft the most relevant and insightful interview questions for each role.
        """
    ),
)

interview_preparation_agent_task = Task(
    description=(
        """
        Create tailored interview questions based on {job_title} 
        and {job_requirement}. Ensure questions align with the skills 
        and competencies required for the position.

       
        
        """
    ),
    expected_output="""
        - Do not make up any information.
        - A well strucured relevant interview questions ready for interviewers with an heading "INTERVIEW QUESTION".
        - Dynamically update the task status based on success or failure.
    """,
    agent=interview_preparation_agent,
    tools=[SerperDevTool()],
        callback=lambda result: update_task_status(result, task_name="Interview Preparation", chat_message_id=chat_message_id),

)



offer_letter_generator = Agent(
    role="Offer Letter Generator",
    goal="Draft customized offer letters for selected candidates.",
    verbose=True,
    allow_delegation=False,
    tools=[],
    backstory=(
        """
        - An HR expert with a passion for negotiation, skilled at crafting offers 
          that resonate with top talent while aligning with company policies.
        - You generate personalized offer letters that match company standards and 
          are appealing to the candidate.
        """
    ),
)

offer_letter_generator_task = Task(
    description=(
        """
        Generate and send offer letters only if the previous recruitment step is completed.

        **Process:**
        - Use TaskStatusCheckerTool to verify if "Interview Coordinator" task is COMPLETED.
        - If "Interview Coordinator" is PENDING, do not proceed.
        - If COMPLETED, use OfferLetterSenderTool to send offer letters to selected candidates.

        **Task Execution Rules:**
        - If "Interview Coordinator" is PENDING, return the task status and stop execution.
        - If offer letters are successfully sent, mark this task as "COMPLETED."

        **Task Details:**
        - **Task Name:** Offer Letter Generator
        - **Status:** [COMPLETED/PENDING]
        - **chat_message_id:** {chat_message_id}
        - **INSTANCE ID:** {instance_id}
        """
    ),
    expected_output="""
        **Offer Letter Generation Status**


        *Offer Letter Dispatch:*
        - Selected Candidates: [List of selected candidates]
        - Emails Sent Status: [Success/Failure]
        - Offer Letter Attachments: Included

        *Task Status Update:*
        - Task Status: [COMPLETED/PENDING]
    """,
    agent=offer_letter_generator,
    tools=[TaskStatusCheckerTool(), OfferLetterSenderTool(), TaskStatusUpdate()],
     callback=lambda result: update_task_status(result, task_name="Offer Letter Generator", chat_message_id=chat_message_id),
  
)




task_manager = Agent(
    role="Task Manager",
    goal="Efficiently identify, delegate, and oversee the execution of tasks based on user input, ensuring timely and accurate completion while maintaining clear communication with the user.",
    verbose=True,
    tools=[],
    backstory=(
        """
        You are a highly organized and detail-oriented professional with extensive experience in task management and delegation. 
        Your expertise lies in understanding complex requirements, matching tasks to the right resources, and ensuring seamless execution.
        With a strong focus on efficiency and accountability, you thrive in dynamic environments where multiple tasks need to be managed simultaneously.
        Your ability to communicate clearly and monitor progress ensures that tasks are completed on time and meet the highest standards of quality.
        """
    ),
    allow_delegation=True,
    memory=True
)

process_pending_tasks_task=Task(
    description=(
        """
        **Task Overview:**  
        Analyze the user's input (`{human_task}`) within the context of previous messages (`{context}`).  
        Respond as a human would, ensuring continuity and relevance in the conversation.  

        ### **Steps to Follow:**  
        1. **Understand User Input**: Identify whether the user is asking a question, making a request, or greeting.  
        2. **Review Conversation Context**: Use `{context}` to understand past interactions and provide a relevant, coherent response.  
        3. **Assign work to coworker**:  
            -customer greeting use customer_service_agent
            -job creating use job_posting_specialist
            -posting on social media use sourcing_automation_agent
            -interview question use interview_preparation_agent
        4. **Generate a Thoughtful Reply**:  
           - If the user is greeting, respond in a natural and friendly manner.  
           - If the user asks a question, answer it using previous context when relevant.  
           - If more details are needed to complete the request, ask a **follow-up question**.  
        5. **Ensure a Human-Like Response**: The response should be clear, natural, and engaging, as if a human is responding.  
        """
    ),
    expected_output="""
    - A **natural, human-like response** considering the context of previous messages.  
    - If the user asks a question, the answer should integrate relevant information from past messages.  
    - If additional details are needed, ask a **follow-up question** to clarify before proceeding.  
      
    **Example Responses:**  

    **Case 1: Greeting**  
    **User:** "Hi"  
    **Response:** "Hey there! How's your day going?"  

    **Case 2: Context-Based Answer**  
    **User:** "Can you remind me of the agent’s capabilities?"  
    **Context:** "User previously discussed AI avatars answering questions on their website."  
    **Response:** "Sure! The agent can handle AI-driven avatars that answer customer queries on a website. Let me know if you need specifics!"  

    **Case 3: Follow-Up Required**  
    **User:** "How do I integrate it?"  
    **Context:** "User asked about AI avatars but didn't specify the platform."  
    **Response:** "Are you looking to integrate the AI avatar into a website, mobile app, or another platform?"  
    """
)

customer_service_agent = Agent(
    role="Customer Service Agent",
    goal="Handle interactions with human users by answering queries and providing guidance.",
    verbose=True,
    allow_delegation=False,
    tools=[],  # Add any customer service related tools if necessary.
    backstory="""
        - A friendly and knowledgeable representative dedicated to assisting users with their inquiries.
        - You excel at understanding user concerns, providing clear and helpful responses, and escalating issues when needed.
    """
)

customer_service_agent_task = Task(
    description="""
        Interact with the human user to answer their questions regarding HR and recruitment processes.
        Provide clear, concise, and friendly responses. 
        If needed, guide the user to the appropriate specialist agent for further assistance.
        Ensure that the response is accurate and helpful.
    """,
    expected_output="""
        A helpful and well-crafted response addressing the user's query.
    """,
    agent=customer_service_agent,
)


agents=[
    job_posting_specialist,
    sourcing_automation_agent,
    resume_screening_agent,
 
    application_tracking_agent,
    interview_coordinator,
    interview_preparation_agent,

    offer_letter_generator,
    ats_manager,
 
]
tasks=[
    job_posting_specialist_task,
    sourcing_automation_agent_task,
    application_tracking_task,
    resume_screening_agent_task,
    ats_manager_task,
    candidate_outreach_specialist_task,
    interview_coordinator_task,
    interview_preparation_agent_task,  
    offer_letter_generator_task,
  
]





from django.db import models
from django.shortcuts import get_object_or_404
from hr_crew.models import Recruitment,RecruitmentTask
import json

   


    
def auto(message_id, form):
    print(form)
    # Get or create Recruitment instance
    chat_message = get_object_or_404(ChatMessage, id=message_id)


    recruitment, created = Recruitment.objects.update_or_create(
        session=chat_message,  
        defaults={
            "job_title": form.get("job_title"),
            "location": form.get("location"),
            "job_requirement": form.get("job_requirement"),
            "expected_reach_out": form.get("expected_reach_out"),
        }
    )


    task_name_mapping = {
        "job_posting_specialist_task": "Job Posting",
        "sourcing_automation_agent_task": "Sourcing Automation",
        "application_tracking_task": "Application Tracking",
        "resume_screening_agent_task": "Resume Screening",
        "ats_manager_task": "ATS Manager",
        "candidate_outreach_specialist_task": "Candidate Outreach",
        "interview_coordinator_task": "Interview Coordinator",
        "interview_preparation_agent_task": "Interview Preparation",
        "offer_letter_generator_task": "Offer Letter Generator",
    
    }
    
    # Create RecruitmentTask instances for all tasks with pending status
    for task_name, readable_name in task_name_mapping.items():
        RecruitmentTask.objects.get_or_create(
            recruitment=recruitment, 
            task_name=readable_name, 
       
        )
    tasks = RecruitmentTask.objects.filter(recruitment=recruitment)
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status

    # Define required tasks (using the human-readable task names)
    required_tasks = [
        job_posting_specialist_task,
        sourcing_automation_agent_task,
        application_tracking_task,
    ]
    update_chat_id(id=recruitment.id)
    # Define the crew with limited tasks
    crew = Crew(
        agents=agents,
        tasks=required_tasks,
        process=Process.sequential,
        planning=True,
         memory=False,  
     
    )

    form["chat_message_id"] = recruitment.id 
    form["apply_link"] = f"{settings.SITE_URL}/o/apply/{recruitment.uuid}/"
    form["instance_id"] = chat_message.id


    # Execute recruitment process
    result = crew.kickoff(inputs=form)


    tasks = RecruitmentTask.objects.filter(recruitment=recruitment).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status

    message_data_string = json.dumps(task_status_mapping)

    recruitment_completed = tasks[0].recruitment.completed if tasks else False

    recruitment.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{recruitment_completed}"
                        },task_name="TASK STATUS")
    return str(result)



def reload(message_id):
    # Get the Recruitment instance based on message_id
    chat_message =message_id
    recruitment = get_object_or_404(Recruitment, session_id=message_id)
    print("re",chat_message.id)
    # Create the inputs JSON object with details from Recruitment instance
    inputs = {

        "location": recruitment.location,
        "job_title": recruitment.job_title,
        "job_requirement": recruitment.job_requirement,
        "expected_reach_out": recruitment.expected_reach_out,
        "company_name":"nypus",
        "chat_message_id":recruitment.id,
    }
    inputs["apply_link"] = f"{settings.SITE_URL}/o/apply/{recruitment.uuid}/"
    inputs["instance_id"] = chat_message.id

      
    
    task_name_mapping_reverse = {
        "Job Posting": job_posting_specialist_task,
        "Sourcing Automation": sourcing_automation_agent_task,
        "Application Tracking": application_tracking_task,
        "Resume Screening": resume_screening_agent_task,
        "ATS Manager": ats_manager_task,
        "Candidate Outreach": candidate_outreach_specialist_task,
       
        "Interview Coordinator": interview_coordinator_task,
        "Interview Preparation": interview_preparation_agent_task,
        "Offer Letter Generator": offer_letter_generator_task,
     
    }
    
    # Fetch all RecruitmentTasks associated with this Recruitment where status is "PENDING"
    pending_tasks = RecruitmentTask.objects.filter(
        recruitment=recruitment, 
        status="PENDING"
    ).order_by("id")
    # Create a list of original task names (reverse lookup using task_name_mapping_reverse)
    pendingtask_list = [
        task_name_mapping_reverse[task.task_name] 
        for task in pending_tasks if task.task_name in task_name_mapping_reverse
    ]
    print("pending",pendingtask_list)

    update_chat_id(id=recruitment.id)
    # Define the crew with the pending tasks
    crew = Crew(
        agents=agents,
        tasks=pendingtask_list,
        process=Process.sequential,
        planning=True,

    )
    
    # Execute recruitment process with the inputs and pending tasks
    result = crew.kickoff(inputs=inputs)
    tasks = RecruitmentTask.objects.filter(recruitment=recruitment).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status

    message_data_string = json.dumps(task_status_mapping)
    
    recruitment_completed = tasks[0].recruitment.completed if tasks else False

    recruitment.session.save_message_to_mongo({
        "Type": "box",
        "message": message_data_string,
        "task_name": "TASK STATUS",
        "user": "AI",
        "retry": f"{recruitment_completed}"
    }, task_name="TASK STATUS")

    return str(result)


def manual(message_id,message):

  
   # Query MongoDB to find all messages related to the given chat_message_id
    messages = list(chat_collection.find({"chat_message_id": str(message_id)}))

    

    # Convert ObjectId to string for readability and structure the data
    message_dict = {"user": [], "AI": []}

    for msg in messages:
        try:
            msg["_id"] = str(msg["_id"])  # Convert ObjectId to string
            message_dict[msg["user"]].append(msg["message"])  # Append message
        except KeyError:
            print(messages)

    print(message_dict)



    agents=[
            job_posting_specialist,
            customer_service_agent,
            sourcing_automation_agent,
            resume_screening_agent,
            interview_coordinator,
            interview_preparation_agent,
            offer_letter_generator,
            ats_manager,
        ]
    human_task_crew = Crew(
            agents=agents,
            tasks=[process_pending_tasks_task],
            process=Process.hierarchical,
            verbose=True,

            manager_agent=task_manager,
            )
    inputs={
        "human_task" : message,
        "context":message_dict
    }
    result=human_task_crew.kickoff(inputs=inputs)
    print(result)
    return str(result)
    