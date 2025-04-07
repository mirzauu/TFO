#!/usr/bin/env python
import sys
import warnings
from crewai import Agent, Crew, Process, Task
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

def run(message_id, message):
    global lead_id

    # Extract message inputs
    company_product = message.get("company_product")
    customer_type = message.get("customer_type")
    interaction_channel = message.get("interaction_channel")
    feedback_source = message.get("feedback_source")
    purchase_history_depth = message.get("purchase_history_depth")

    # Format topic string
    topic = (
        f"Analyze customer engagement and CRM strategies for {company_product}, "
        f"targeting {customer_type}. Focus on interactions through {interaction_channel}, "
        f"while evaluating customer feedback from {feedback_source}. "
        f"Additionally, assess purchase behaviors based on {purchase_history_depth} of sales data."
    )

    chat_message = get_object_or_404(ChatMessage, id=message_id)
    lead, created = CustomerRelationshipManagement.objects.update_or_create(
        session=chat_message,
        topic=company_product,
        customer_segment=customer_type,
        interaction_history=interaction_channel,
        preferred_communication_channel=feedback_source,
        business_goal=purchase_history_depth,
    )
    lead_id = lead

    # Task mapping
    task_name_mapping = {
        "follow_up_manager_task": "Follow-Up Manager",
        "feedback_analyst_task": "Feedback Analyst",
        "customer_segmentation_task": "Customer Segmentation Specialist",
        "cross_sell_strategist_task": "Cross-Sell Strategist",
        "survey_specialist_task": "Survey Specialist",
    }

    for _, readable_name in task_name_mapping.items():
        CRMTask.objects.get_or_create(crm_strategy=lead, task_name=readable_name)

    pending_tasks = CRMTask.objects.filter(crm_strategy=lead, status="PENDING").order_by("id")
    inputs = {"topic": topic}
    message_result = {}

    # Initialize Crew instance and agents
    try:
        crew_instance = CrmTeam()
        agent_list = [
            crew_instance.follow_up_manager(),
            crew_instance.feedback_analyst(),
            crew_instance.customer_segmentation_expert(),
            crew_instance.cross_sell_strategist(),
            crew_instance.survey_specialist(),
        ]
    except Exception as e:
        return f"Error initializing CRM agents: {str(e)}"

    # Run each task individually
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

    lead.session.save_message_to_mongo({
        "Type": "box",
        "message": message_data_string,
        "task_name": "RESULT",
        "user": "AI",
        "retry": "True"
    }, task_name="Task Status")

    return str(message_result)


