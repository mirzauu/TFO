#!/usr/bin/env python
import sys
import warnings

from django.shortcuts import get_object_or_404
from sales_crew.src.crm_team.crew import CrmTeam
from sales_crew.models import CustomerRelationshipManagement,CRMTask
from organizations.models import ChatMessage
import json
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

lead_id=None

def task_callback(task_name, result,formate):
    
    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        market_research_task = CRMTask.objects.filter(
            task_name=task_name,
            crm_strategy=lead_id # Ensuring it's the current session
        ).order_by("-id").first()

        if market_research_task:
            # Update task status and result
            market_research_task.status = "COMPLETED"
            market_research_task.output = json.dumps(result.to_dict())  # Save result as JSON string if needed
            market_research_task.formate = formate  # Save result as JSON string if needed
            market_research_task.save()
            print(f"Updated task: {task_name} -> COMPLETED for Research ID: {market_research_task}")
        else:
            print(f"Task '{task_name}' not found for the current MarketResearch session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")


def run(message_id,message):
    
    global lead_id
        
    # Prompt user for key CRM-related inputs
    company_product = "Apple - iPhone 15"
    customer_type = "Retail Consumers"
    interaction_channel = "Social Media"
    feedback_source = "Google Reviews and Twitter Mentions"
    purchase_history_depth = "Last 12 months"


    # Format the topic as a clear sentence
    topic = (f"Analyze customer engagement and CRM strategies for {company_product}, "
            f"targeting {customer_type}. Focus on interactions through {interaction_channel}, "
            f"while evaluating customer feedback from {feedback_source}. "
            f"Additionally, assess purchase behaviors based on {purchase_history_depth} of sales data.")
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    lead, created = CustomerRelationshipManagement.objects.update_or_create(
        session=chat_message,  
        topic=message.get("topic"),
        customer_segment=message.get("customer_segment"),
        interaction_history=message.get("interaction_history"),
        preferred_communication_channel=message.get("preferred_communication_channel"),
        business_goal=message.get("business_goal"),
    )

    lead_id=lead
    task_name_mapping = {
        "follow_up_manager_task": "Follow-Up Manager",
        "feedback_analyst_task": "Feedback Analyst",
        "customer_segmentation_task": "Customer Segmentation Specialist",
        "cross_sell_strategist_task": "Cross-Sell Strategist",
        "survey_specialist_task": "Survey Specialist",
    }
    for task_name, readable_name in task_name_mapping.items():
        CRMTask.objects.get_or_create(
            crm_strategy=lead, 
            task_name=readable_name, 
       
        )

    pending_tasks = CRMTask.objects.filter(crm_strategy=lead, status="PENDING").order_by("id")

    # Create a list of CrewAI tasks that match the pending ones
    crew_instance = CrmTeam()
    selected_tasks = []    
    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())

    if not selected_tasks:
        return "No pending tasks to execute."  
    
    crew = CrmTeam().crew()
    crew.tasks = selected_tasks  

    inputs = {
        "topic": topic,
    }
    result = crew.kickoff(inputs=inputs)

    tasks = CRMTask.objects.filter(crm_strategy=lead).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    
    status = tasks[0].crm_strategy.complete if tasks else False
    
    lead.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "RESULT",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="RESULT")

    return str(result)
    

