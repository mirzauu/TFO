#!/usr/bin/env python
import sys
import warnings
from marketing_crew.src.market_research_team.crew import MarketResearchTeam
from organizations.models import ChatMessage
import json
from marketing_crew.models import MarketResearchTask,MarketResearch
from django.shortcuts import get_object_or_404
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

research_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        market_research_task = MarketResearchTask.objects.filter(
            task_name=task_name,
            research=research_id # Ensuring it's the current session
        ).order_by("-id").first()

        if market_research_task:
            # Update task status and result
            market_research_task.status = "COMPLETED"
            market_research_task.output = json.dumps(result.to_dict())   # Save result as JSON string if needed
            market_research_task.formate = formate  # Save result as JSON string if needed
            market_research_task.save()
            print(f"Updated task: {task_name} -> COMPLETED for Research ID: {market_research_task.research.id}")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")
   




def run(message_id,message):

    global research_id
    
    print(message)
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    research, created = MarketResearch.objects.update_or_create(
        session=chat_message,  
        topic=message.get("topic")
       
    )
    
    research_id=research
    
    task_name_mapping = {
            "review_analyst_task": "Review Analysis",
            "survey_designer_task": "Survey Design",
            "trend_spotter_task": "Trend Spotting",
            "competitor_analyst_task": "Competitor Analysis",
            "demographic_specialist_task": "Demographic Analysis",
            "persona_creator_task": "Persona Creation",
            "geo_market_analyst_task": "Geographical Market Analysis",
            "sentiment_analyst_task": "Sentiment Analysis",
            "gap_analyst_task": "Gap Analysis",
            "strategic_planner_task": "Strategic Planning",
            }
    
    for task_name, readable_name in task_name_mapping.items():
        MarketResearchTask.objects.get_or_create(
            research=research, 
            task_name=readable_name, 
       
        )
  
    pending_tasks = MarketResearchTask.objects.filter(research=research, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = MarketResearchTeam()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."
    
    print("pending",selected_tasks)
    # Create a new Crew with only the selected tasks
    crew = MarketResearchTeam().crew()
    crew.tasks = selected_tasks  # Assign only pending tasks

    geographic_focus = "North America and Europe"
    review_source = "Google Reviews, Trustpilot, and Social Media Mentions"
    target_audience = "Tech Enthusiasts and Business Professionals"
    timeframe = "Last 12 months"

    topic = (f"Conduct a detailed market and lead analysis focusing on businesses in {geographic_focus}. "
             f"Additionally, review customer feedback from {review_source} to understand {target_audience} "
             f"preferences over the {timeframe}.")

    # Define inputs to be used by CrewAI tasks
    inputs = {
        "topic": topic,
    }
    result = crew.kickoff(inputs=inputs)

    tasks = MarketResearchTask.objects.filter(research=research).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    status = tasks[0].research.complete if tasks else False
    research.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="TASK STATUS")

    return str(result)

def retry(message_id,message):

    global research_id
    
    print(message)
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    research, created = MarketResearch.objects.update_or_create(
        session=chat_message,  
       
    )
    
    research_id=research

    task_name_mapping = {
            "review_analyst_task": "Review Analysis",
            "survey_designer_task": "Survey Design",
            "trend_spotter_task": "Trend Spotting",
            "competitor_analyst_task": "Competitor Analysis",
            "demographic_specialist_task": "Demographic Analysis",
            "persona_creator_task": "Persona Creation",
            "geo_market_analyst_task": "Geographical Market Analysis",
            "sentiment_analyst_task": "Sentiment Analysis",
            "gap_analyst_task": "Gap Analysis",
            "strategic_planner_task": "Strategic Planning",
            }
    
    for task_name, readable_name in task_name_mapping.items():
        MarketResearchTask.objects.get_or_create(
            research=research, 
            task_name=readable_name, 
        )
  
    pending_tasks = MarketResearchTask.objects.filter(research=research, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = MarketResearchTeam()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."
    
    print("pending",selected_tasks)
    # Create a new Crew with only the selected tasks
    crew = MarketResearchTeam().crew()
    crew.tasks = selected_tasks  # Assign only pending tasks

    inputs = {
        'topic': "tesla,Model x"
    }
    result = crew.kickoff(inputs=inputs)

    tasks = MarketResearchTask.objects.filter(research=research).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    status = tasks[0].research.complete if tasks else False
    research.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="TASK STATUS")

    return str(result)