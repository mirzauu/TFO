#!/usr/bin/env python
import sys
import warnings
from crewai import Agent, Crew, Process, Task
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
def run(message_id, message):
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

    social_id = social

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

    for _, readable_name in task_name_mapping.items():
        SocialMediaResearchTask.objects.get_or_create(research=social, task_name=readable_name)

    pending_tasks = SocialMediaResearchTask.objects.filter(research=social, status="PENDING").order_by("id")
    if not pending_tasks.exists():
        return "No pending tasks to execute."

    try:
        crew_instance = SocialMediaCrew()
        agent_list = [
            crew_instance.competitor_analyst(),
            crew_instance.content_planner(),
            crew_instance.brand_monitor(),
            crew_instance.influencer_scout(),
            crew_instance.customer_engagement_expert(),
            crew_instance.metrics_analyst(),
            crew_instance.hashtag_strategist(),
            crew_instance.campaign_designer(),
            crew_instance.caption_creator(),
            crew_instance.script_writer(),
        ]
    except Exception as e:
        return f"Error initializing social media agents: {str(e)}"

    topic = (
        f"Develop a social media campaign for {message.get('campaign_theme')}, targeting "
        f"{message.get('target_audience')} on {message.get('platform')}. "
        f"Analyze competitor strategies from {message.get('competitors')} and implement content "
        f"ideas to achieve the goal: {message.get('goal')}."
    )

    inputs = {
        "topic": topic
    }

    message_result = {}

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            task_func = getattr(crew_instance, crew_task_name, None)
            if not task_func:
                continue

            single_task = task_func()
            single_task_crew = Crew(
                agents=agent_list,
                tasks=[single_task],
                process=Process.sequential,
                verbose=True
            )

            try:
                result = single_task_crew.kickoff(inputs=inputs)
                message_result[db_task_name] = "COMPLETED"
            except Exception as e:
                message_result[db_task_name] = f"FAILED: {str(e)}"

    message_data_string = json.dumps(message_result)
    status = SocialMediaResearchTask.objects.filter(research=social).first().research.complete

    social.session.save_message_to_mongo({
        "Type": "box",
        "message": message_data_string,
        "task_name": "RESULT",
        "user": "AI",
        "retry": f"{status}"
    }, task_name="Task Result")

    return str(message_result)

