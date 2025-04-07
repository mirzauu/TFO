#!/usr/bin/env python
import sys
import warnings
from crewai import Agent, Crew, Process, Task
from organizations.models import ChatMessage
import json
from sales_crew.src.content_creation_team.crew import ContentCreationTeam
from django.shortcuts import get_object_or_404
from sales_crew.models import ContentCreation,ContentCreationTask


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")



lead_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{type(result)}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        market_research_task = ContentCreationTask.objects.filter(
            task_name=task_name,
            content_creation=lead_id # Ensuring it's the current session
        ).order_by("-id").first()
    
        if market_research_task:
            # Update task status and result
            market_research_task.status = "COMPLETED"
            market_research_task.output = json.dumps(result.to_dict())  # Save result as JSON string if needed
            market_research_task.formate = formate # Save result as JSON string if needed
            market_research_task.save()
            print(f"Updated task: {task_name} -> COMPLETED for Research ID: {market_research_task}")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")

    def run(message_id, message):
        global lead_id

        chat_message = get_object_or_404(ChatMessage, id=message_id)
        lead, created = ContentCreation.objects.update_or_create(
            session=chat_message,
            topic=message.get("topic")
        )

        lead_id = lead

        task_name_mapping = {
            "sales_brochure_specialist_task": "Sales Brochure Specialist",
            "email_template_creator_task": "Email Template Creation",
            "product_description_writer_task": "Product Description Writing",
            "presentation_designer_task": "Presentation Design",
            "social_media_content_creator_task": "Social Media Content Creation",
        }

        # Create task entries in DB
        for _, readable_name in task_name_mapping.items():
            ContentCreationTask.objects.get_or_create(content_creation=lead, task_name=readable_name)

        # Filter pending tasks
        pending_tasks = ContentCreationTask.objects.filter(content_creation=lead, status="PENDING").order_by("id")

        if not pending_tasks.exists():
            return "No pending tasks to execute."

        # Initialize Crew instance and agents
        try:
            crew_instance = ContentCreationTeam()
            agent_list = [
                crew_instance.sales_brochure_specialist(),
                crew_instance.email_template_creator(),
                crew_instance.product_description_writer(),
                crew_instance.presentation_designer(),
                crew_instance.social_media_content_creator(),
            ]
        except Exception as e:
            return f"Error initializing content agents: {str(e)}"

        inputs = {
            "topic": message.get("topic")
        }

        message_result = {}

        # Run each task one-by-one
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
                    verbose=True,
                )

                try:
                    result = single_task_crew.kickoff(inputs=inputs)
                    message_result[db_task_name] = "COMPLETED"
                except Exception as e:
                    message_result[db_task_name] = f"FAILED: {str(e)}"

        message_data_string = json.dumps(message_result)

        # Save result to Mongo
        lead.session.save_message_to_mongo({
            "Type": "box",
            "message": message_data_string,
            "task_name": "RESULT",
            "user": "AI",
            "retry": "True"
        }, task_name="RESULT")

        return str(message_result)


def retry(message_id):
    
    global lead_id

    chat_message = message_id
    lead, created = ContentCreation.objects.update_or_create(
        session=chat_message,  
  
    )

    lead_id=lead

    task_name_mapping = {
    "sales_brochure_specialist_task": "Sales Brochure Specialist",
    "email_template_creator_task": "Email Template Creation",
    "product_description_writer_task": "Product Description Writing",
    "presentation_designer_task": "Presentation Design",
    "social_media_content_creator_task": "Social Media Content Creation",
    }

    for task_name, readable_name in task_name_mapping.items():
        ContentCreationTask.objects.get_or_create(
            content_creation=lead, 
            task_name=readable_name, 
       
        )

    pending_tasks = ContentCreationTask.objects.filter(content_creation=lead, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = ContentCreationTeam()
    selected_tasks = []

    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."    

    crew = ContentCreationTeam().crew()
    crew.tasks = selected_tasks    

    inputs = inputs = {
        'topic': "Samsung Galaxy S24"
    }
    result = crew.kickoff(inputs=inputs)


    tasks = ContentCreationTask.objects.filter(content_creation=lead).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    
    status = tasks[0].content_creation.complete if tasks else False
    
    lead.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "RESULT",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="RESULT")

    return str(result)

