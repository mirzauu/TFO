#!/usr/bin/env python
import sys
import warnings
from django.shortcuts import get_object_or_404
from sales_crew.src.sales_strategy_team.crew import SalesStrategyTeam
from crewai import Agent, Crew, Process, Task
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

def run(message_id, message):
    print("Reached to sales")
    global lead_id

    chat_message = get_object_or_404(ChatMessage, id=message_id)
    lead, created = SalesStrategy.objects.update_or_create(
        session=chat_message,  
        industry_sector=message.get("industry_sector"),
        target_market=message.get("target_market"),
        timeframe=message.get("timeframe"),
        data_source=message.get("data_source")
    )
    lead_id = lead

    task_name_mapping = {
        "market_research_analyst_task": "Market Research Analyst",
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

    pending_tasks = SalesStrategyTask.objects.filter(sales_strategy=lead, status="PENDING").order_by("id")

    # Compose the topic
    industry_sector = message.get("industry_sector")
    target_market = message.get("target_market")
    timeframe = message.get("timeframe")
    data_source = message.get("data_source")

    topic = (
        f"Analyze the {industry_sector} with a focus on {target_market} over {timeframe}, "
        f"using data from {data_source}."
    )

    inputs = {"topic": topic}
    message_result = {}

    # Initialize the crew team and agents once
    try:
        crew_instance = SalesStrategyTeam()
        agent_list = [
            crew_instance.market_analyst(),
            crew_instance.swot_analyst(),
            crew_instance.competitor_analyst(),
            crew_instance.pricing_strategist(),
            crew_instance.sales_pitch_specialist(),
        ]
    except Exception as e:
        print(f"Error creating SalesStrategyTeam instance or agents: {e}")
        return f"Error: {str(e)}"

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

    # Save result message
    message_data_string = json.dumps(message_result)

    lead.session.save_message_to_mongo({
        "Type": "box",
        "message": message_data_string,
        "task_name": "RESULT",
        "user": "AI",
        "retry": "True"
    }, task_name="Task Status")

    return str(message_result)
