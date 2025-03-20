from datetime import datetime
from crewai import Crew, Process
from hr_crew.src.onboarding.agents import OnboardingTeam
from hr_crew.src.onboarding.tasks import OnboardingTasks,context_response_task

from django.shortcuts import get_object_or_404
from organizations.models import ChatMessage

import json
from config.llm_config import openapi_llm 

from tfo_backend.mongodb import chat_collection,db

onboarding_team = OnboardingTeam()
onboarding_task = OnboardingTasks()

def main(message_id, form):
    chat_message = get_object_or_404(ChatMessage, id=message_id)

    # Create or update Onboarding instance
    onboarding, created = Onboarding.objects.update_or_create(
        session=chat_message,  
        defaults={
            "employee_id": form.get("employee_id"),
            "employee_name": form.get("first_name"),
            "employee_email": form.get("email"),
        }
    )
    form["id"] = onboarding.id
    form["chat_id"] = message_id
   
    # Creating onboarding tasks
    tasks = [
        onboarding_task.create_orientation_task(newhireinfo=form),
        onboarding_task.create_document_automation_task(newhireinfo=form),
        onboarding_task.document_verification(newhireinfo=form),
        onboarding_task.create_welcome_email_task(newhireinfo=form),
        onboarding_task.create_it_setup_coordination_task(newhireinfo=form),
        onboarding_task.create_policy_compliance_task(newhireinfo=form),
        onboarding_task.create_training_plan_development_task(newhireinfo=form),
    ]

    # Mapping task names
    task_name_mapping = {
        "create_orientation_task": "Orientation task",
        "create_document_automation_task": "Document Automation Task",
        "document_verification": "Document Verification Task",
        "create_welcome_email_task": "Welcome Email Task",
        "create_it_setup_coordination_task": "Software Installation Task",
        "create_policy_compliance_task": "Policy Compliance Task",
        "create_training_plan_development_task": "Training Plan Development Task",
    }

    # Ensure tasks are properly created
    for task_name, readable_name in task_name_mapping.items():
        task, created = EmployeeOnboardingTask.objects.get_or_create(
            onboarding=onboarding, 
            task_name=readable_name,
        )
    


    agents = [
        onboarding_team.create_orientation_coordinator(),
        onboarding_team.create_document_automation_specialist(),
        onboarding_team.create_welcome_email_specialist(),
        onboarding_team.create_it_setup_coordinator(),
        onboarding_team.create_training_development_specialist(),
        onboarding_team.create_team_integration_facilitator(),
        onboarding_team.create_policy_compliance_tracker(),
        onboarding_team.create_final_report_agent(),
    ]

    

    # Create and execute the Crew with all tasks
    onboarding_crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        manager_llm=openapi_llm,
         memory=False,  
     

    )

    print(f"Crew ID: {onboarding_crew.id}")

    print("🚀 Starting Employee Onboarding Process...")

    # Kick off the onboarding process
    results = onboarding_crew.kickoff(inputs=form)



    all_tasks = EmployeeOnboardingTask.objects.filter(onboarding=onboarding).order_by("id")

    # Ensure task status mapping is properly handled
    task_status_mapping = {}

   
    if not all_tasks.exists():
        print("No tasks found for onboarding!")

    for task in all_tasks:
        print(f"Processing task: {task.task_name} | Status: {task.status}") 
        if task.task_name:  # Ensure task_name is not None
            task_status_mapping[task.task_name] = task.status
        else:
            print(f"Warning: Task {task} has no task_name!")  
    
    message_data_string = json.dumps(task_status_mapping)

    onboarding_completed = not all_tasks.exclude(status='COMPLETED').exists()

    onboarding.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{onboarding_completed}"
                        },task_name="TASK STATUS")
    return str(results)


from hr_crew.models import Onboarding, EmployeeOnboardingTask
from hr_crew.src.onboarding.agents import OnboardingTeam 
import logging

from crewai import Crew, Process

logger = logging.getLogger(__name__)

def retry(chat_id):
    """
    Retry pending or failed tasks related to the given ChatMessage ID.
    """
    # Retrieve the Onboarding object related to the ChatMessage
    onboarding = Onboarding.objects.filter(session=chat_id).first()
    if not onboarding:
        raise ValueError(f"No Onboarding found for ChatMessage with ID {chat_id}.")

    # Create a form dictionary from the onboarding data
    form = {
        "employee_id": onboarding.employee_id,
        "first_name": onboarding.employee_name,
        "email": onboarding.employee_email,
        "id": onboarding.id,
        "chat_id":chat_id,
    }

    # Define task-method pairs for dynamic task creation
    task_methods = [
        (onboarding_task.create_orientation_task, "Orientation task", {"newhireinfo": form}),
        (onboarding_task.create_document_automation_task, "Document Automation Task", {"newhireinfo": form}),
        (onboarding_task.document_verification, "Document Verification Task", {"newhireinfo": form}),
        (onboarding_task.create_welcome_email_task, "Welcome Email Task", {"newhireinfo": form}),
        (onboarding_task.create_it_setup_coordination_task, "Software Installation Task", {"newhireinfo": form}),
        (onboarding_task.create_policy_compliance_task, "Policy Compliance Task", {"newhireinfo": form}),
        (onboarding_task.create_training_plan_development_task, "Training Plan Development Task", {"newhireinfo": form}),
        (onboarding_task.create_final_report_task, "Final Report", {"message_id": chat_id, "newhireinfo": form}),
    ]

    tasks_to_execute = []

        # Loop through tasks and check their status
    for task_method, task_name, extra_params in task_methods:
        if not callable(task_method):
            logger.error(f"Task method {task_name} is not callable. Skipping.")
            continue

        # Retrieve tasks with PENDING or FAILED status
        tasks = EmployeeOnboardingTask.objects.filter(
            onboarding=onboarding,
            task_name=task_name,
            status__in=["PENDING", "FAILED"]
        )
        
        dynamic_task = task_method(**extra_params)
        logger.info(f"Executed {task_name}: {dynamic_task}")
        logger.info(f"Found {len(tasks)} tasks for {task_name}: {tasks}")

        if tasks:
            tasks_to_execute.append(dynamic_task)
    
    print(tasks_to_execute)
    agents = [
        onboarding_team.create_orientation_coordinator,
        onboarding_team.create_document_automation_specialist,
        onboarding_team.create_welcome_email_specialist,
        onboarding_team.create_it_setup_coordinator,
        onboarding_team.create_training_development_specialist,
        onboarding_team.create_team_integration_facilitator,
        onboarding_team.create_policy_compliance_tracker,
        onboarding_team.create_final_report_agent,
    ]

    # Initialize the Crew instance
    onboarding_crew = Crew(
        agents=[agent() for agent in agents],
        tasks=tasks_to_execute,
        process=Process.sequential,
        manager_llm=openapi_llm,
         memory=False,  
    )
    

    # Kick off the crew to execute tasks
    results = onboarding_crew.kickoff()
    
    all_tasks = EmployeeOnboardingTask.objects.filter(onboarding=onboarding).order_by("id")

    # Ensure task status mapping is properly handled
    task_status_mapping = {}

   
    if not all_tasks.exists():
        print("No tasks found for onboarding!")

    for task in all_tasks:
        print(f"Processing task: {task.task_name} | Status: {task.status}") 
        if task.task_name:  # Ensure task_name is not None
            task_status_mapping[task.task_name] = task.status
        else:
            print(f"Warning: Task {task} has no task_name!")  
    
    message_data_string = json.dumps(task_status_mapping)

    onboarding_completed = not all_tasks.exclude(status='COMPLETED').exists()

    onboarding.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{onboarding_completed}"
                        },task_name="TASK STATUS")

    return str(results)



def manual(message_id,message):
     
    agents = [
        onboarding_team.create_orientation_coordinator(),
        onboarding_team.create_document_automation_specialist(),
        onboarding_team.create_welcome_email_specialist(),
        onboarding_team.create_it_setup_coordinator(),
        onboarding_team.create_training_development_specialist(),
        onboarding_team.create_team_integration_facilitator(),
        onboarding_team.create_policy_compliance_tracker(),
        onboarding_team.create_final_report_agent(),
    ]


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

    

    # Add user input to memory
   

    inputs={
        "hr_message" : message,
        "context":message_dict,
        "chat_id":message_id,
    }
    print("inputaaaaaaaa",inputs)
    crew = Crew(
        agents=list(agents),
        tasks=[context_response_task],
        process=Process.hierarchical,
        verbose=True,
         memory=False,  
        manager_agent=onboarding_team.create_onboarding_manager(), 
        manager_llm=openapi_llm # Main agent
    )

    response = crew.kickoff(inputs=inputs)


    print("eeee",response)
    return str(response)

    
#     # Initialize the onboarding team and tasks
#     onboarding_team = OnboardingTeam()
#     onboarding_task = OnboardingTasks()

#     # Collect inputs from the user
    
    
  

#     # Define tasks to execute based on database status
#     tasks_to_execute = []

#     # Define task-method pairs for dynamic task creation
#     task_methods = [
#         (onboarding_task.create_orientation_task, "Orientation Task", {"task_name": task_name, "start_date": start_date, "duration_days": duration_days}),
#         (onboarding_task.create_document_automation_task, "Document Automation", {}),
#         (onboarding_task.create_welcome_email_task, "Welcome Email", {"task_name": task_name, "start_date": start_date, "duration_days": duration_days, "company": company}),
#         (onboarding_task.create_it_setup_coordination_task, "IT Setup Coordination", {}),
#         (onboarding_task.create_policy_compliance_task, "Policy Compliance", {}),
#         (onboarding_task.create_training_plan_development_task, "Training Plan Development", {}),
#         (onboarding_task.create_team_integration_task, "Team Integration", {}),
#         (onboarding_task.create_final_report_task, "Final Report", {}),
#     ]

#     # Loop through task-method pairs and check database status
#     for task_method, task_name, extra_params in task_methods:
#         # Check the task's status in the database
#         task_progress, _ = EmployeeOnboardingTask.objects.get_or_create(
#             employee_id=employee_id,
#             task_name=task_name,
#             employee_name=employee_name,
#             employee_email=employee_email,
#         )

#         # Only create tasks that are pending or failed
#         if task_progress.status in ["PENDING", "FAILED"]:
#             # Dynamically create the task with additional parameters
#             task = task_method(employee_name=employee_name, employee_email=employee_email, **extra_params)
#             if task:
#                 tasks_to_execute.append(task)
                
             

#     # Retrieve all agents
#     agents = [
#         onboarding_team.create_orientation_coordinator(),
#         onboarding_team.create_document_automation_specialist(),
#         onboarding_team.create_welcome_email_specialist(),
#         onboarding_team.create_it_setup_coordinator(),
#         onboarding_team.create_training_development_specialist(),
#         onboarding_team.create_team_integration_facilitator(),
#         onboarding_team.create_policy_compliance_tracker(),
#         onboarding_team.create_final_report_agent(),
#     ]

    
#     # Create and execute the Crew
#     onboarding_crew = Crew(
#         agents=list(agents),  # Retrieve all agents
#         tasks=tasks_to_execute,
#         process=Process.sequential,
        
#     )
#     # new_hire_data ={
#     #     "first_name": "immanual",
#     #     "last_name": None,
#     #     "start_date": "June 15, 2023",
#     #     "role": "Software Developer",
#     #     "department": None,
#     #     "email": "alimirsa123@gmail.com",
#     #     "orientation_schedule": "Meeting scheduled for introductions with the team on June 15, 2023.",
#     #     "document_status": "Pending document collection and verification",
#     #     "it_setup_status": None
#     #     }
    
   
#     newhireinfo = {
#         "employee_id": "immanual-alimirsa123@gmail.com",
#         "first_name": "immanual",
#         "last_name": None,
#         "start_date": "June 15, 2023",
#         "role": "Software Developer",
#         "department": None,
#         "email": "alimirsa123@gmail.com",
#         "orientation_schedule": "Meeting scheduled for introductions with the team on June 15, 2023.",
#         "document_status": "pending",
#         "it_setup_status": "Completed"
#     }

#     print(type(newhireinfo))
#     task_pending_agent=onboarding_team.task_manager()
#     task_pending_task = onboarding_task.process_pending_tasks_task(newhireinfo=newhireinfo)

    
#     onboarding_crew_pending = Crew(
#         agents=list(agents),
#         tasks=[task_pending_task],
#         process=Process.hierarchical,
#         verbose=True,
#         manager_agent=task_pending_agent,
        
#     )

#     print("🚀 Starting Employee Onboarding Process...")


    
#     # Kick off the onboarding process
#     results = onboarding_crew.kickoff(inputs={"employee_id": employee_id})
#     # results = onboarding_crew_pending.kickoff(inputs={"newhireinfo": newhireinfo})
#     print(results)