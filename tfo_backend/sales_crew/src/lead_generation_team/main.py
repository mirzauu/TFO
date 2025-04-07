#!/usr/bin/env python
import sys
import warnings
from crewai import Agent, Crew, Process, Task
from organizations.models import ChatMessage
import json
from sales_crew.models import LeadGeneration,LeadGenerationTask
from django.shortcuts import get_object_or_404


from sales_crew.src.lead_generation_team.crew import LeadGenerationTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


lead_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        market_research_task = LeadGenerationTask.objects.filter(
            task_name=task_name,
            lead_generation=lead_id # Ensuring it's the current session
        ).order_by("-id").first()

        if market_research_task:
            # Update task status and result
            market_research_task.status = "COMPLETED"
            market_research_task.output = json.dumps(result.to_dict()) # Save result as JSON string if needed
            market_research_task.formate = formate  # Save result as JSON string if needed
            market_research_task.save()
            print(f"Updated task: {task_name} -> COMPLETED for Research ID: {market_research_task}")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")
   


def run(message_id=1,message=2):

    global lead_id

    chat_message = get_object_or_404(ChatMessage, id=message_id)
    lead, created = LeadGeneration.objects.update_or_create(
        session=chat_message,  
        topic=message.get("target_industry")
    )
    target_industry = message.get("target_industry")
    company_size_range = message.get("company_size_range")
    geographic_focus = message.get("geographic_focus")
    lead_source_channels = message.get("lead_source_channels")

    topic = (f"Conduct a detailed market and lead analysis for the {target_industry} sector, "
             f"focusing on {company_size_range} businesses in {geographic_focus}. "
             f"Use data from {lead_source_channels} to assess market trends, identify leads, "
             f"analyze competitors, and develop strategic insights.")

    # Define inputs to be used by CrewAI tasks
   

    lead_id=lead
    
    task_name_mapping = {
    "lead_identifier_task": "Lead Identification",
    "research_analyst_task": "Market Research & Analysis",
    "social_media_extractor_task": "Social Media Data Extraction",
    "competitor_analyst_task": "Competitor Analysis",
    }

    for task_name, readable_name in task_name_mapping.items():
        LeadGenerationTask.objects.get_or_create(
            lead_generation=lead, 
            task_name=readable_name, 
       
        )

    pending_tasks = LeadGenerationTask.objects.filter(lead_generation=lead, status="PENDING").order_by("id")
    inputs = {"topic": topic}
    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = LeadGenerationTeam()
    message_result={}
    # Manually initialize all agents once
    agent_list = [
        crew_instance.lead_identifier(),
        crew_instance.research_analyst(),
        crew_instance.social_media_extractor(),
        crew_instance.competitor_analyst(),
    ]

    # Run each task separately
    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            task_func = getattr(crew_instance, crew_task_name, None)
            if not task_func:
                continue

            single_task = task_func()

            # Create a mini crew with only one task
            single_task_crew = Crew(
                agents=agent_list,
                tasks=[single_task],
                process=Process.sequential,
                verbose=True,
            )

            try:
                result = single_task_crew.kickoff(inputs=inputs)
                message_result[db_task_name] = "COMPLETED"
            except Exception as e:
                message_result[db_task_name] = f"FAILED: {str(e)}"

    message_data_string = json.dumps(message_result)

    lead.session.save_message_to_mongo({
        "Type": "box",
        "message": message_data_string,
        "task_name": "RESULT",
        "user": "AI",
        "retry": "True"
    }, task_name="Task Status")

    return str(message_result)


def retry(message_id):

    global lead_id

    chat_message = message_id
    lead, created = LeadGeneration.objects.update_or_create(
        session=chat_message,  
     
    )

    lead_id=lead
    
    task_name_mapping = {
    "lead_identifier_task": "Lead Identification",
    "research_analyst_task": "Market Research & Analysis",
    "social_media_extractor_task": "Social Media Data Extraction",
    "competitor_analyst_task": "Competitor Analysis",
    }

    for task_name, readable_name in task_name_mapping.items():
        LeadGenerationTask.objects.get_or_create(
            lead_generation=lead, 
            task_name=readable_name, 
       
        )

    pending_tasks = LeadGenerationTask.objects.filter(lead_generation=lead, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = LeadGenerationTeam()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."    

    crew = LeadGenerationTeam().crew()
    crew.tasks = selected_tasks 
    target_industry = "Smartphone and Consumer Electronics"
    company_size_range = "Mid-sized (50-500 employees)"
    geographic_focus = "North America and Europe"
    lead_source_channels = "LinkedIn, Crunchbase, and industry reports"

    # Format the topic as a clear sentence
    topic = (f"Conduct a detailed market and lead analysis for the {target_industry} sector, "
             f"focusing on {company_size_range} businesses in {geographic_focus}. "
             f"Use data from {lead_source_channels} to assess market trends, identify leads, "
             f"analyze competitors, and develop strategic insights.")

    # Define inputs to be used by CrewAI tasks
    inputs = {
        "topic": topic,
    }

    result = crew.kickoff(inputs=inputs)

    tasks = LeadGenerationTask.objects.filter(lead_generation=lead).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    
    status = lead.complete
    
    lead.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "RESULT",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="RESULT")

    return str(result)


