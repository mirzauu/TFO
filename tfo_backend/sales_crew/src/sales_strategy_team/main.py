#!/usr/bin/env python
import sys
import warnings
from django.shortcuts import get_object_or_404
from sales_crew.src.sales_strategy_team.crew import SalesStrategyTeam

from sales_crew.models import SalesStrategy,SalesStrategyTask
from organizations.models import ChatMessage
import json
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import json

lead_id=None

def task_callback(task_name, result,formate):

    print(f"\nTask Completed: {task_name}\nResult:\n{result}\n")

    try:
        # Find the latest MarketResearch entry that has this task
        market_research_task = SalesStrategyTask.objects.filter(
            task_name=task_name,
            sales_strategy=lead_id # Ensuring it's the current session
        ).order_by("-id").first()

        if market_research_task:
            # Update task status and result
            market_research_task.status = "COMPLETED"
            market_research_task.output =json.dumps(result.to_dict())  # Save result as JSON string if needed
            market_research_task.formate =formate # Save result as JSON string if needed
            market_research_task.save()
            print(f"Updated task: {task_name} -> COMPLETED for Research ID: {market_research_task}")
        else:
            print(f"Task '{task_name}' not found for the current SalesStrategyTask session.")

    except Exception as e:
        print(f"Error updating task '{task_name}': {e}")


def run(message_id,message):
    print("reached to sales")
    global lead_id

    chat_message = get_object_or_404(ChatMessage, id=message_id)
    lead, created = SalesStrategy.objects.update_or_create(
        session=chat_message,  
        industry_sector=message.get("industry_sector"),
        target_market=message.get("target_market"),
        timeframe=message.get("timeframe"),
        data_source=message.get("data_source")
    )
    print("reached to sales2",message)
    lead_id=lead
    task_name_mapping = {
        "market_research_analyst_task": "Market Research Analyst",
        "Code_Interpreter_Tool_task": "Code Interpreter Tool",
        "SWOT_analysis_evaluator_task": "SWOT Analysis Evaluator",
        "competitor_analyst_task": "Competitor Analyst",
        "pricing_strategist_task": "Pricing Strategist",
        "tailored_sales_pitch_specialist_task": "Tailored Sales Pitch Specialist",
    }

    for task_name, readable_name in task_name_mapping.items():
        SalesStrategyTask.objects.get_or_create(
            sales_strategy=lead, 
            task_name=readable_name, 
       
        )
    print("reached to sales4")
    pending_tasks = SalesStrategyTask.objects.filter(sales_strategy=lead, status="PENDING").order_by("id")
    print("reached to sales")
    # Create a list of CrewAI tasks that match the pending ones
    try:
        crew_instance = SalesStrategyTeam()
        print("crewins")
    except Exception as e:
        print("crewins none")
        crew_instance = None  # or handle it differently if needed
        print(f"Error creating SalesStrategyTeam instance: {e}")

    selected_tasks = []
    print("SALES ",selected_tasks)
    for crew_task_name, db_task_name in task_name_mapping.items():
        if pending_tasks.filter(task_name=db_task_name).exists():
            print(crew_task_name)            
            task_func = getattr(crew_instance, crew_task_name, None)
            if task_func:
                selected_tasks.append(task_func())
    print("SALES2 ",selected_tasks)

    if not selected_tasks:
        return "No pending tasks to execute."  
    
    print("reached to sales6")
    crew = SalesStrategyTeam().crew()
    crew.tasks = selected_tasks   

   
    industry_sector = message.get("industry_sector")
    target_market = message.get("target_market")
    timeframe = message.get("timeframe")
    data_source = message.get("data_source")

    # Format the topic as a clear sentence
    topic = f"Analyze the {industry_sector} with a focus on {target_market} over {timeframe}, using data from {data_source}."
    
    inputs = {
        'topic': topic
    }
    result = crew.kickoff(inputs=inputs)

    print(result)

    tasks = SalesStrategyTask.objects.filter(sales_strategy=lead).order_by("id")
    task_status_mapping = {}
    for task in tasks:
        task_status_mapping[task.task_name] = task.status 

    message_data_string = json.dumps(task_status_mapping)
    
    status = tasks[0].sales_strategy.complete if tasks else False
    
    lead.session.save_message_to_mongo({
                        "Type": "box",
                        "message": message_data_string,
                        "task_name": "RESULT",
                        "user": "AI",
                        "retry":f"{status}"
                        },task_name="RESULT")

    return str(result)