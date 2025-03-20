#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from marketing_crew.src.seo_sem_crew.crew import SeoSemCrew
from organizations.models import ChatMessage
import json
from marketing_crew.models import SEOResearch,SEOResearchTask
from django.shortcuts import get_object_or_404
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

seo_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        seo_task = SEOResearchTask.objects.filter(
            task_name=task_name,
            research=seo_id # Ensuring it's the current session
        ).order_by("-id").first()

        if seo_task:
            # Update task status and result
            seo_task.status = "COMPLETED"
            seo_task.output = json.dumps(result.to_dict())  # Save result as JSON string if needed
            seo_task.formate=formate
            seo_task.save()
            print(f"Updated task: {task_name} -> ")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")




def run(message_id,message):

    global seo_id
    
    print(message)
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    seo, created = SEOResearch.objects.update_or_create(
        session=chat_message,  
        website_name=message.get("website_name"),
        competitors=message.get("competitors"),
        target_audience=message.get("target_audience"),
        ad_budget=message.get("ad_budget"),
        primary_goals=message.get("primary_goals")
       
    )
    
    seo_id=seo


    task_name_mapping = {
        "keyword_research_task": "Keyword Research",
        "competitor_analysis_task": "Competitor Analysis",
        "content_optimization_task": "Content Optimization",
        "backlink_analysis_task": "Backlink Analysis",
        "analytics_monitoring_task": "Analytics Monitoring",
        "seo_reporting_task": "SEO Reporting",
        "meta_description_task": "Meta Description Optimization",
        "ad_copy_task": "Ad Copy Creation",
        "sem_campaign_management_task": "SEM Campaign Management",
        "seo_audit_task": "SEO Audit",
        "internal_linking_task": "Internal Linking Strategy",
        "content_strategy_task": "Content Strategy",
    }
    for task_name, readable_name in task_name_mapping.items():
        SEOResearchTask.objects.get_or_create(
            research=seo, 
            task_name=readable_name, 
       
        )
  
    pending_tasks = SEOResearchTask.objects.filter(research=seo, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = SeoSemCrew()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."

    crew = SeoSemCrew().crew()
    crew.tasks = selected_tasks 
   
    website_name =  f"{message.get("website_name")}"
    competitors = f"{message.get("competitors")}"
    target_audience =  f"{message.get("target_audience")}"
    ad_budget =   f"{message.get("ad_budget")}"

    # Format the topic variable as a detailed sentence
    topic = (f"Develop and optimize SEO and SEM strategies for {website_name}, "
             f"targeting {target_audience}. Conduct competitive analysis against "
             f"{competitors} and create ad campaigns within an {ad_budget}.")

    # Define inputs for the CrewAI task
    inputs = {
        'topic': topic,
    }

    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    

    tasks = SEOResearchTask.objects.filter(research=seo).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    status = tasks[0].research.complete if tasks else False
    seo.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "TASK STATUS",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="TASK STATUS")

    return str(result)

