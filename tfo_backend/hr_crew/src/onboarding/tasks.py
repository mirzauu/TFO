from hr_crew.models import Onboarding, EmployeeOnboardingTask
from hr_crew.src.onboarding.agents import OnboardingTeam  # Import the OnboardingTeam class
from crewai import Agent
from django.shortcuts import get_object_or_404
import hr_crew.src.onboarding.tools.document_collection,hr_crew.src.onboarding.tools.it_setup,hr_crew.src.onboarding.tools.orientation_planning,hr_crew.src.onboarding.tools.policy_tracking,hr_crew.src.onboarding.tools.custom_tools

from crewai import Task
from organizations.models import ChatMessage
from textwrap import dedent 
import json

from typing import List, Optional
from pydantic import BaseModel,Field
from typing import Dict
from pydantic import BaseModel
from langchain.tools import tool
from hr_crew.src.onboarding.tools.custom_tools import TaskStatusUpdate,SendEmailTool,CreateOnboardingPlanTool,CreateTrainingPlanTool,VerifyDocumentTool,VerifyUploadedDocumentTool

class DocumentAutomation(BaseModel):
    has_link_generated: Optional[bool] = Field(None, description="True if the link is generated.")
    has_email_sent: Optional[bool] = Field(None, description="True if the email is sent to the employee.")
    has_document_verified: Optional[bool] = Field(None, description="True if the document is verified successfully.")
    document_status: Optional[str] = Field(None, description="Status of document collection and verification.")


class NewHireInfo(BaseModel):
    employee_id: Optional[str] = Field(None, description="Employee ID of the new hire.")
    first_name: Optional[str] = Field(None, description="First name of the new hire.")
    last_name: Optional[str] = Field(None, description="Last name of the new hire.")
    start_date: Optional[str] = Field(None, description="Start date of the new hire.")
    role: Optional[str] = Field(None, description="Role assigned to the new hire.")
    department: Optional[str] = Field(None, description="Department of the new hire.")
    email: Optional[str] = Field(None, description="Email address of the new hire.")
    orientation_schedule: Optional[str] = Field(None, description="Personalized orientation schedule.only mark as 'completed' or 'pending'")
    document_status: Optional[DocumentAutomation] = Field(
        None,
        description="Structured data for document collection and verification."
    )
    welcome_email: Optional[str] = Field(None, description="Status of welcome email sent.only mark as 'completed' or 'pending'")
    it_setup_status: Optional[str] = Field(None, description="Status of IT setup for the new hire.only mark as 'completed' or 'pending'")
    policy_compliance_status: Optional[str] = Field(None, description="Status of policy compliance tracking.only mark as 'completed' or 'pending'")
    training_plan_development: Optional[str] = Field(None, description="Status of training plan developement.only mark as 'completed' or 'pending'")
    team_integration_task: Optional[str] = Field(None, description="Status of team integration process.only mark as 'completed' or 'pending'")

def preprocess_form(raw_form):
        """
        Preprocess the form string into a dictionary.
        """
        from collections import defaultdict
        form_dict = defaultdict(lambda: None)

        # Parse the formatted string manually
        for pair in raw_form.split(' '):
            if '=' in pair:
                key, value = pair.split('=', 1)
                form_dict[key.strip()] = value.strip().strip("'\"")

        return dict(form_dict)
    
    
class OnboardingTasks:
    """
    A class to define onboarding-related tasks dynamically.
    """

    TIP_SECTION = "Ensure each step is personalized to enhance the onboarding experience!"

    def __init__(self):
        # Initialize the onboarding team
        self.onboarding_team = OnboardingTeam()
        self.create_orientation_coordinator = self.onboarding_team.create_orientation_coordinator()
        self.create_document_automation_specialist = self.onboarding_team.create_document_automation_specialist()
        self.create_welcome_email_specialist = self.onboarding_team.create_welcome_email_specialist()
        self.create_it_setup_coordinator = self.onboarding_team.create_it_setup_coordinator()
        self.create_training_development_specialist = self.onboarding_team.create_training_development_specialist()
        self.create_team_integration_facilitator = self.onboarding_team.create_team_integration_facilitator()
        self.create_policy_compliance_tracker = self.onboarding_team.create_policy_compliance_tracker()
        self.create_final_report_agent = self.onboarding_team.create_final_report_agent()
        self.task_manager = self.onboarding_team.task_manager()
        self.create_onboarding_manager = self.onboarding_team.create_onboarding_manager()

        self.orientation_planning = hr_crew.src.onboarding.tools.orientation_planning
        self.it_setup = hr_crew.src.onboarding.tools.it_setup
        self.custom_tool = hr_crew.src.onboarding.tools.custom_tools
        self.policy_tracking = hr_crew.src.onboarding.tools.policy_tracking
        self.document_verification_tool = hr_crew.src.onboarding.tools.document_collection

   
    

    def create_or_update_onboarding(self,form, message_id):

        if isinstance(form, str):
            try:
                form = json.loads(form)  # Convert JSON string to dictionary
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in form data")

            print("Parsed Form Data:", form)
        """
        Create or update the Onboarding model and associated EmployeeOnboardingTask based on the form data.

        :param form: Dictionary containing onboarding details.
        :param message_id: ID of the ChatMessage associated with the onboarding.
        """
        # Extract required fields from the form
        employee_id = form.get("employee_id", "N/A")
        employee_name = f"{form.get('first_name', '')} {form.get('last_name', '')}".strip() or None
        employee_email = form.get("email")
        print("mesafee",message_id)
        # Get or create the Onboarding object
        chat_message = ChatMessage.objects.get(id=message_id)
        print("alimi",chat_message)
        onboarding, created = Onboarding.objects.get_or_create(
            session=chat_message,
            defaults={
                "employee_id": employee_id,
                "employee_name": employee_name,
                "employee_email": employee_email,
            }
        )

        # If the Onboarding object already exists, update the fields
        if not created:
            onboarding.employee_id = employee_id
            onboarding.employee_name = employee_name
            onboarding.employee_email = employee_email
            onboarding.save()

        # Define the tasks to be created or updated
        tasks = {
            "Orientation Task": form.get("orientation_schedule"),
            "Document Automation": form.get("document_status", {}).get("document_status"),
            "Welcome Email": form.get("welcome_email"),
            "IT Setup Coordination": form.get("it_setup_status"),
            "Policy Compliance": form.get("policy_compliance_status"),
            "Training Plan Development": form.get("training_plan_development"),
            "Team Integration": form.get("team_integration_task"),
        }

        # Update or create EmployeeOnboardingTask for each task in the form
        for task_name, status in tasks.items():
            # Determine task status
            if status is None:
                task_status = "PENDING"
            elif isinstance(status, str) and "Completed" in status:
                task_status = "COMPLETED"
            elif isinstance(status, str) and "Requires" in status:
                task_status = "FAILED"
            elif isinstance(status, str) and "In Progress" in status:
                task_status = "IN_PROGRESS"
            else:
                task_status = "PENDING"

            # Create or update the task
            EmployeeOnboardingTask.objects.update_or_create(
                onboarding=onboarding,
                task_name=task_name,
                defaults={
                    "status": task_status,
                    "output": status if isinstance(status, (dict, str)) else None,
                },
            )


        return onboarding

 

    def update_task_status(self,result,task_name,id):
        print("expected_output",result,task_name,id)
        try:
            onboarding = get_object_or_404(Onboarding, id=id)
            onboarding_task = get_object_or_404(EmployeeOnboardingTask, onboarding=onboarding, task_name=task_name)
            onboarding_task.final_report=str(result)

            if task_name in ["Training Plan Development Task", "Interview Preparation"]:
                onboarding_task.status = "COMPLETED"
            onboarding_task.save()

        except Exception as e:
                print(f"Error updating task status for {task_name} - {task_name}: {e}")    
        

    def create_orientation_task(self, newhireinfo: Optional[Dict]) -> Optional[Task]:
        """
        Creates a task for generating an onboarding plan for a new employee.
        """
        expected_output = f"""
        A well structured onboarding plan for {newhireinfo.get('first_name', 'N/A')}
        """

        task_description = f"""
            Your task is to create a well-structured onboarding plan for {newhireinfo.get('first_name', 'N/A')} 
            who is joining as a {newhireinfo.get('role', 'N/A')}. The plan should include all key onboarding 
            components such as orientation, training, mentorship, and periodic performance reviews.

            After completing the plan, you MUST update the task status to 'COMPLETED' using the TaskStatusUpdate tool. 
            The status should reflect whether the onboarding plan has been successfully created.

            Task Name: [Orientation task]
            Status: [COMPLETED]
            INSTANCE ID: {newhireinfo.get('id', 'N/A')}
             """

        return Task(
            description=task_description,
            agent=self.create_orientation_coordinator,
            expected_output=expected_output,
            tools=[
         
                 TaskStatusUpdate()
      
            ],
            callback=lambda result: self.update_task_status(result, task_name="Orientation task", id=newhireinfo.get('id', 'N/A')),
        )



# Function to Create Document Automation Task
    def create_document_automation_task(self, newhireinfo: Optional[Dict] = None) -> Optional[Task]:
        """
        Creates a task for automating document collection and verification.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task or None: A dynamically created Task object for document automation, or None if the task is skipped.
        """

        # Document collection expected output
        expected_output = dedent(
            """A fully automated document collection and verification system, including:
            - send email reminders for pending submissions

            
            """
        )

        # Document collection and verification task description
        task_description = dedent(
            f"""
            **Task**: Send an email to {newhireinfo.get('first_name', 'N/A')} at {newhireinfo.get('email', 'N/A')} 
            requesting the necessary documents using the VerifyDocumentTool. 

            Once the email is sent, verify the submitted documents and update the task status to "COMPLETED" using the TaskStatusUpdate tool. 
            The task status update is **mandatory**.

            **Employee Details**:
            - Name: {newhireinfo.get('first_name', 'N/A')}
            - Email: {newhireinfo.get('email', 'N/A')}
            - Employee ID: {newhireinfo.get('employee_id', 'N/A')}

            **Task Parameters**:
            - Task Name: "Document Automation Task"
            - Status: ["COMPLETED"]
            - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
            """
        )

        # Create and return the Task
        return Task(
            description=task_description,
            agent=self.create_document_automation_specialist,
            expected_output=expected_output,
            tools=[VerifyDocumentTool(), TaskStatusUpdate()],
            callback=lambda result: self.update_task_status(result, task_name="Document Automation Task", id=newhireinfo.get('id', 'N/A')),
        )
    
    def document_verification(self, newhireinfo: Optional[Dict] = None) -> Optional[Task]:
        """
        Creates a task for verifying document status using VerifyUploadedDocumentTool
        and updating the task status using TaskStatusUpdate.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task or None: A dynamically created Task object for document verification, or None if skipped.
        """

        # Expected output of the task
        expected_output = dedent(
            f"""
            - Verified the document status of {newhireinfo.get('first_name', 'N/A')} ({newhireinfo.get('email', 'N/A')}).
            - Document status retrieved using VerifyUploadedDocumentTool.
            - Task status updated to COMPLETED or PENDING using TaskStatusUpdate.
            """
        )

        # Updated task description
        task_description = dedent(
            f"""
            **Task**: Verify the employee's document status using VerifyUploadedDocumentTool,
            then update the task status using TaskStatusUpdate. 

            everytime get the lastest updation using VerifyUploadedDocumentTool

            **Steps to Perform**:
            1. Check the document verification status of {newhireinfo.get('first_name', 'N/A')}.
            2. Retrieve document verification details using VerifyUploadedDocumentTool.
            3. Update the task status based on the verification result.

            **Task Parameters**:
            - Task Name: "Document Verification Task"
            - Status: ["COMPLETED" / "PENDING"]
            - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
            """
        )

        # Create and return the Task
        return Task(
            description=task_description,
            agent=self.create_document_automation_specialist,
            expected_output=expected_output,
            tools=[VerifyUploadedDocumentTool(result_as_answer=True), TaskStatusUpdate()],  # Mandatory tools
            callback=lambda result: self.update_task_status(
                result, task_name="Document Verification Task", id=newhireinfo.get('id', 'N/A')
            ),
        )



    def create_welcome_email_task(self, newhireinfo: Optional[Dict] = None) -> Optional[Task]:
        """
        Creates a task for generating and sending a personalized welcome email.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task or None: A dynamically created Task object for generating and sending the welcome email, or None if the task is skipped.
        """

        # Define the expected output
        expected_output = dedent(
            f"""A personalized welcome email has been sent to {newhireinfo.get('first_name', 'N/A')} at {newhireinfo.get('email', 'N/A')}, including:
            - A warm greeting addressed to {newhireinfo.get('first_name', 'N/A')}.
            - Introduction to Nypus, highlighting its culture and values.
            - Details about their first day, orientation schedule, and useful resources or links.
            """
        )

        # Define the task description with explicit instruction to update task status
        task_description = dedent(
            f"""
            "Generate and Send a Welcome Email.And then Update the task status using 'TaskStatusUpdate'"
            
            **MUST call** `TaskStatusUpdate()` to update the task status after using "SendEmailTool" .

            Employee Details:
            - Name: {newhireinfo.get('first_name', 'N/A')}
            - Email: {newhireinfo.get('email', 'N/A')}
            - Employee ID: {newhireinfo.get('employee_id', 'N/A')}

            **Steps**:
            1. Draft a **personalized welcome email**.
            2. Send an email containing personalized welcome email to {newhireinfo.get('email', 'N/A')} using "SendEmailTool".
            3. update the task status to COMPLETE using "TaskStatusUpdate"

            once email send  `TaskStatusUpdate()` to update the task status to complete.
              
            **Task Status Update Parameters**:
            - Task Name: "Welcome Email Task"
            - Status: ["COMPLETED"]
            - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
            - CHAT MESSAGE ID: {newhireinfo.get('chat_id', 'N/A')}
            """
        )

        # Return the Task object with explicit task update requirement
        return Task(
            description=task_description,
            agent=self.create_welcome_email_specialist,
            expected_output=expected_output,
            tools=[SendEmailTool(), TaskStatusUpdate()],
            callback=lambda result: self.update_task_status(result, task_name="Welcome Email Task", id=newhireinfo.get('id', 'N/A')),

        )


    def create_it_setup_coordination_task(self, newhireinfo: Optional[Dict] = None) -> Optional[Task]:
        """
        Creates a task for sending an email to an employee with software installation details and the installation file attached.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task: A dynamically created Task object for software installation email.
        """

        # Define the expected output
        expected_output = dedent(
            f"""A confirmation that an email has been sent to {newhireinfo.get('first_name', 'N/A')} at {newhireinfo.get('email', 'N/A')}, including:
            - Software installation file: Lark.apk
            - Software name: Lark
            - Step-by-step installation guide.

            Example Confirmation:
            An email has been successfully sent to {newhireinfo.get('first_name', 'N/A')} with the software installation details and required files attached.
            """
        )

        # Define the task description
        task_description = dedent(
            f"""
            **Task**: Send Software Installation Email to {newhireinfo.get('first_name', 'N/A')} And then Update the task status using 'TaskStatusUpdate'.

            **Steps**:
            1. Draft an email to {newhireinfo.get('email', 'N/A')} with the subject **"Software Installation Instructions: Lark"**.
            2. Include a brief introduction explaining the purpose of the email.
            3. Attach the **software installation file** (Lark.apk) from www.googledrive.com.
            4. Provide a **step-by-step installation guide** for Lark.
            6. Send an email containing the draft to {newhireinfo.get('email', 'N/A')} using "SendEmailTool".
            7. update the task status using "TaskStatusUpdate"

            **Task Completion Requirement**:
            - If the email is successfully sent, update the task status to **COMPLETED** using `TaskStatusUpdate`.
            - If there is an issue (e.g., invalid email, attachment missing, email undelivered), update the status to **PENDING**.

            **Task Parameters**:
            - Task Name: "Software Installation Task"
            - Status: ["COMPLETED"]
            - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
            - CHAT MESSAGE ID: {newhireinfo.get('chat_id', 'N/A')}

            """
        )

        # Return the Task object with status update integration
        return Task(
            description=task_description,
            agent=self.create_it_setup_coordinator, 
            expected_output=expected_output,
            tools=[SendEmailTool(),TaskStatusUpdate()],
            callback=lambda result: self.update_task_status(result, task_name="Software Installation Task", id=newhireinfo.get('id', 'N/A')),
        )


    def create_policy_compliance_task(self, newhireinfo: Optional[Dict] = None) -> Optional[Task]:
        """
        Creates a task for tracking policy compliance for a new employee.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task: A dynamically created Task object for policy compliance tracking.
        """

        # Define the expected output
        expected_output = dedent(
            f"""A detailed compliance report for {newhireinfo.get('first_name', 'N/A')}, including:
            - Confirmation that the policy email has been sent.
            - Automatic fetching and analysis of {newhireinfo.get('first_name', 'N/A')}'s response.
            - Status of compliance (e.g., "Understood", "Requires Follow-up").

            Example Report:
            Policy compliance for {newhireinfo.get('first_name', 'N/A')} is marked as "Understood". 
            Email sent to {newhireinfo.get('email', 'N/A')} has been acknowledged.
            """
        )

        # Define the task description
        task_description = dedent(
            f"""
            **Task**: Track Employee Policy Compliance And then Update the task status.

            **Employee Details**:
            - Name: {newhireinfo.get('first_name', 'N/A')}
            - Email: {newhireinfo.get('email', 'N/A')}
            - Employee ID: {newhireinfo.get('employee_id', 'N/A')}

            **Steps**:
            1. Send an email containing company policies to {newhireinfo.get('email', 'N/A')} using "SendEmailTool".
            2. update the task status using "TaskStatusUpdate"
           
            
            **Task Completion Requirement**:
            - If the email sent succesfully, update the task status to **COMPLETED** using `TaskStatusUpdate`.
            - If the email sent unsuccesfull, update the status to **PENDING**.

            **Task Parameters**:
            - Task Name: "Policy Compliance Task"
            - Status: ["COMPLETED"]
            - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
            - CHAT MESSAGE ID: {newhireinfo.get('chat_id', 'N/A')}
            """
        )

        # Return the Task object with status update integration
        return Task(
            description=task_description,
            agent=self.create_policy_compliance_tracker,
            expected_output=expected_output,
            tools=[SendEmailTool(),TaskStatusUpdate()],
            callback=lambda result: self.update_task_status(result, task_name="Policy Compliance Task", id=newhireinfo.get('id', 'N/A')),
        )

    
    def create_training_plan_development_task(self, newhireinfo: Optional[Dict] = None) -> Task:
        """
        Creates a task for developing training plans for new hires.
        """

        expected_output = f"""
        A structured training plan for {newhireinfo.get('first_name', 'N/A')}, including:
        - Role-specific training timelines.
        - Required resources (guides, tools, mentors).
        - Detailed supervision and mentoring structure.
        """

        task_description = f"""
        **Task**: Develop Training Plans for {newhireinfo.get('first_name', 'N/A')}

        **Employee Details**:
        - Name: {newhireinfo.get('first_name', 'N/A')}
        - Email: {newhireinfo.get('email', 'N/A')}
        - Employee ID: {newhireinfo.get('employee_id', 'N/A')}

        **Task Objectives**:
        Create a **customized training schedule** that aligns with {newhireinfo.get('first_name', 'N/A')}'s role.  
        The plan should include:
        - **Timelines** for key training milestones.
        - **Resources** needed for training.
        - **Mentors or trainers** overseeing the sessions.

        **Task Completion Requirement**:
        - If a comprehensive training plan is created, mark the task as **COMPLETED**.
        - If training details are missing, set status to **PENDING**.

        **Task Parameters**:
        - Task Name: "Training Plan Development Task"
        - Status: ["COMPLETED"]
        - INSTANCE ID: {newhireinfo.get('id', 'N/A')}
        """

        return Task(
            description=task_description,
            agent=self.create_training_development_specialist,
            expected_output=expected_output,
            tools=[
                CreateTrainingPlanTool(),
                TaskStatusUpdate(),
            ],
            callback=lambda result: self.update_task_status(result, task_name="Training Plan Development Task", id=newhireinfo.get('id', 'N/A')),
        )

   
    def create_team_integration_task(self,newhireinfo: Optional[Dict] = None) -> Task:
        """
        Creates a task for facilitating the integration of new hires into their teams.

        Args:
            employee_name (str): The name of the employee.
            employee_email (str): The email of the employee.

        Returns:
            Task: A dynamically created Task object for team integration.
        """
        employee_id = f"{newhireinfo.get('employee_id', 'N/A')}"

      
        # Define the expected output
        expected_output = dedent(
            f"""
            1- "An updated NewHireInfo model with the `team_integration_task` field populated with the status of the task.status should be completed or pending"
            Successful integration of {employee_id} into their team, including:
            - A personalized announcement message sent to the team.
            - A scheduled meeting or event for introductions.
            - Confirmation that {employee_id} feels welcomed and the team acknowledges their addition.

            Example Integration Steps:
            - Send personalized announcement email about {employee_id} to the team.
            - Schedule a team meeting for introductions on the first day.
            - Collect feedback to ensure a positive integration experience.
            """
        )

        # Define the task description
        task_description = dedent(
            f"""
            **Task**: Facilitate Team Integration for {employee_id}

            **Employee Details**:
                - **Employee ID**: {newhireinfo.get('employee_id', 'N/A')}
                - **First Name**: {newhireinfo.get('first_name', 'N/A')}
                - **Last Name**: {newhireinfo.get('last_name', 'N/A')}
                - **Start Date**: {newhireinfo.get('start_date', 'N/A')}
                - **Role**: {newhireinfo.get('role', 'N/A')}
                - **Department**: {newhireinfo.get('department', 'N/A')}
                - **Email**: {newhireinfo.get('email', 'N/A')}
                - **Orientation Schedule Status**: {newhireinfo.get('orientation_schedule', 'N/A')}
                - 
                - **IT Setup Status**: {newhireinfo.get('it_setup_status', 'N/A')}
                - **WELCOME EMAIL**: {newhireinfo.get('welcome_email', 'N/A')}
                - **POLICY COMPLIANCE STATUS**: {newhireinfo.get('policy_compliance_status', 'N/A')}

            **Description**:
            Automate and manage the introduction of {employee_id} to their team. Responsibilities include:
            - Creating and sending personalized announcements about {employee_id} to the team.
            - Scheduling an introduction meeting or event with team members.
            - Ensuring {employee_id} feels welcomed and the team is prepared for their arrival.

            **Note**: Prioritize creating a positive and collaborative atmosphere for {employee_id}'s integration.
            """
        )

        # Return the Task object with the expected output passed to the callback
        return Task(
            description=task_description,
            agent=self.create_team_integration_facilitator,
            output_pydantic=NewHireInfo,
            expected_output=expected_output,
            callback=lambda result: self.update_task_status(
                employee_id=employee_id,
                task_name="Team Integration",
                status="COMPLETED",
                expected_output=result  # Pass the result of this task
            ),
        )

    
    def create_final_report_task(self,message_id,newhireinfo: Optional[Dict] = None):
        """
        Creates a task for generating a final report summarizing all onboarding tasks.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task: A dynamically created Task object for final report generation.
        """
        employee_id = f"{newhireinfo.get('employee_id', 'N/A')}"
  
        # Define the task description
        task_description = dedent(f"""
            Task: Generate Final Onboarding Report.

            **Employee Details**:
                - **Employee ID**: {newhireinfo.get('employee_id', 'N/A')}
                - **First Name**: {newhireinfo.get('first_name', 'N/A')}
                - **Last Name**: {newhireinfo.get('last_name', 'N/A')}
                - **Start Date**: {newhireinfo.get('start_date', 'N/A')}
                - **Role**: {newhireinfo.get('role', 'N/A')}
                - **Department**: {newhireinfo.get('department', 'N/A')}
                - **Email**: {newhireinfo.get('email', 'N/A')}
                - **Orientation Schedule Status**: {newhireinfo.get('orientation_schedule', 'N/A')}
                - 
                - **IT Setup Status**: {newhireinfo.get('it_setup_status', 'N/A')}
                - **WELCOME EMAIL**: {newhireinfo.get('welcome_email', 'N/A')}
                - **POLICY COMPLIANCE STATUS**: {newhireinfo.get('policy_compliance_status', 'N/A')}

            Description:
            Create a structured report summarizing all onboarding tasks for new hires. 
            The report should include:
            - A summary of all onboarding tasks.
            - Final result of all onboarding tasks.
            - Any relevant insights or notes from each task.
            - A final compliance status.
            - Ensure to fill out the `NewHireInfo` model with 
            as much information as possible.
            
            ---
            class NewHireInfo(BaseModel):
                employee_id: Optional[str] = Field(None, description="Employee ID of the new hire.")
                first_name: Optional[str] = Field(None, description="First name of the new hire.")
                last_name: Optional[str] = Field(None, description="Last name of the new hire.")
                start_date: Optional[str] = Field(None, description="Start date of the new hire.")
                role: Optional[str] = Field(None, description="Role assigned to the new hire.")
                department: Optional[str] = Field(None, description="Department of the new hire.")
                email: Optional[str] = Field(None, description="Email address of the new hire.")
                orientation_schedule: Optional[str] = Field(None, description="Personalized orientation schedule.")
                document_status: Optional[DocumentAutomation] = Field(
                    None,
                    description="Structured data for document collection and verification."
                )
                welcome_email: Optional[str] = Field(None, description="Status of welcome email sent.")
                it_setup_status: Optional[str] = Field(None, description="Status of IT setup for the new hire.")
                policy_compliance_status: Optional[str] = Field(None, description="Status of policy compliance tracking.")
                training_plan_development: Optional[str] = Field(None, description="Status of training plan developement.")
                team_integration_task: Optional[str] = Field(None, description="Status of team integration process.")
            ---
                
            If any information is missing, leave the value as None.
            All information must come directly from the task output. 
            Do not make up any information.    


            
            
        """)

        # Prepare the report output in the desired format (string)
        report_output = dedent(f"""
            A structured report  all onboarding tasks:
            - Orientation details.
            - Document collection and verification .
            - Welcome email information.
            - IT setup status.
            - Training plan details.
            - Team integration summary.
            - Policy compliance status.
            - Filled `NewHireInfo` model.
        """)

        # Define the expected output for display purposes
        expected_output = dedent(f"""
            Final Onboarding Report for {employee_id}:
            {report_output}
        """)

        # Return the Task object
        return Task(
            description=task_description,
            agent=self.create_final_report_agent,
            expected_output=expected_output,
            callback=lambda result: self.create_or_update_onboarding(
                form=json.loads(result.raw) if result.raw else vars(result.pydantic),
                message_id=message_id
            ),
            output_pydantic=NewHireInfo,
            output_file="REPORT.md",
        )
   
    def process_pending_tasks_task(self, newhireinfo: Dict) -> Task:
        """
        Create a task to process pending tasks for the new hire.

        Args:
            newhireinfo (Dict): Dictionary containing new hire information.

        Returns:
            Task: Task instance for processing pending tasks.
        """
        # Format the task description with the values from `newhireinfo`
        description = f"""
        Identify and execute pending tasks for the new hire.
        Tasks are considered pending if their status is 'Pending', 'None', or 'In Progress'.
        Skip tasks with a status of 'Completed' or equivalent.
        Pass the employee_id when delegating work to your coworker. The coworker will complete the process of recruiting the employee_id.

        NewHireInfo:
            - Employee ID: {newhireinfo.get('employee_id', 'N/A')}
            - First Name: {newhireinfo.get('first_name', 'N/A')}
            - Last Name: {newhireinfo.get('last_name', 'N/A')}
            - Start Date: {newhireinfo.get('start_date', 'N/A')}
            - Role: {newhireinfo.get('role', 'N/A')}
            - Department: {newhireinfo.get('department', 'N/A')}
            - Email: {newhireinfo.get('email', 'N/A')}
            - Orientation Schedule: {newhireinfo.get('orientation_schedule', 'N/A')}
            - Document Status: {newhireinfo.get("document_status", {})}
            - IT Setup Status: {newhireinfo.get('it_setup_status', 'N/A')}

        Analyze and execute pending tasks for the new hire:
            - Orientation Schedule: {newhireinfo.get('orientation_schedule', 'N/A')}
            - Document Status: {newhireinfo.get("document_status", {})}
            - IT Setup Status: {newhireinfo.get('it_setup_status', 'N/A')}

        Example: If the orientation task is pending, assign work to the "create_create_orientation_coordinator" agent and complete the task.

        Execute only tasks with statuses: 'Pending', 'None', or 'In Progress'.  
        Update the statuses in the `NewHireInfo` model after execution .only execute once.
        if the status is pending after the execution mark as pending.
        If any information is missing, leave the value as None.
        All information must come directly from the task output. 
        Do not make up any information. 
        
        """

        return Task(
            description=description,
            expected_output=(
                """
                Updated `NewHireInfo` model with executed task statuses.
                
                Only pending tasks should be executed, and others should remain unchanged.
                """
            ),
         
            output_pydantic=NewHireInfo,
        )    
    

context_response_task=Task(
            description=(
                """
                **Task Overview:**  
                chat message id :{chat_id}
                Analyze the user's input (`{hr_message}`) within the context of previous messages (`{context}`).  
                Respond as a human would, ensuring continuity and relevance in the conversation.  

                ### **Steps to Follow:**  
                1. **Understand User Input**: Identify whether the user is asking a question, making a request, or greeting.  
                2. **Review Conversation Context**: Use `{context}` to understand past interactions and provide a relevant, coherent response.  
                3. **Generate a Thoughtful Reply**:  
                - If the user is greeting, respond in a natural and friendly manner.  
                - If the user asks a question, answer it using previous context when relevant.  
                - If more details are needed to complete the request, ask a **follow-up question**.  
                4. **Ensure a Human-Like Response**: The response should be clear, natural, and engaging, as if a human is responding.  
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





        