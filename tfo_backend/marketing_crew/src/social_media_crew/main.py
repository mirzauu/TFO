#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from marketing_crew.src.social_media_crew.crew import SocialMediaCrew

from organizations.models import ChatMessage
import json
from marketing_crew.models import SocialMediaResearch,SocialMediaResearchTask
from django.shortcuts import get_object_or_404

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


social_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        seo_task = SocialMediaResearchTask.objects.filter(
            task_name=task_name,
            research=social_id # Ensuring it's the current session
        ).order_by("-id").first()

        if seo_task:
            # Update task status and result
            seo_task.status = "COMPLETED"
            seo_task.output = json.dumps(result.to_dict()) # Save result as JSON string if needed
            seo_task.formate = formate  # Save result as JSON string if needed
            seo_task.save()
           # Save result as JSON string if needed
            print(f"Updated task: {task_name} -> ")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")

def run(message_id,message):
    global social_id
    
    print(message)
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    social, created = SocialMediaResearch.objects.update_or_create(
        session=chat_message,  
        competitors=message.get("competitors"),
        campaign_theme=message.get("campaign_theme"),
        target_audience=message.get("target_audience"),
        platform=message.get("platform"),
        goal=message.get("goal")
       
    )
    
    social_id=social
    task_name_mapping = {
        "competitor_analysis_task": "Competitor Analysis",
        "content_planner_task": "Content Planning",
        "brand_monitor_task": "Brand Monitoring",
        "influencer_scout_task": "Influencer Scouting",
        "customer_engagement_task": "Customer Engagement",
        "metrics_analyst_task": "Performance Metrics Analysis",
        "hashtag_strategy_task": "Hashtag Strategy Development",
        "campaign_design_task": "Campaign Design",
        "caption_creation_task": "Caption Creation",
        "scriptwriting_task": "Scriptwriting for Social Media",
    }

    for task_name, readable_name in task_name_mapping.items():
        SocialMediaResearchTask.objects.get_or_create(
            research=social, 
            task_name=readable_name, 
       
        )
  
    pending_tasks = SocialMediaResearchTask.objects.filter(research=social, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = SocialMediaCrew()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."
    
    crew = SocialMediaCrew().crew()
    crew.tasks = selected_tasks 

    competitors =message.get("competitors")
    campaign_theme = message.get("campaign_theme")
    target_audience =message.get("target_audience")
    platform = message.get("platform")
    goal = message.get("goal")

    topic = (f"Develop a social media campaign for {campaign_theme}, targeting {target_audience} on {platform}. "
             f"Analyze competitor strategies from {competitors} and implement content ideas to achieve the goal: {goal}.")
    
    inputs = {
        'topic': topic
    }

    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
    tasks = SocialMediaResearchTask.objects.filter(research=social).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    status = tasks[0].research.complete if tasks else False
    social.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "RESULT",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="RESULT")

    return str(result)

