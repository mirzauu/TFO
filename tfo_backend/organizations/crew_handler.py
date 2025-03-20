from datetime import datetime
from django.http import JsonResponse
from .models import ChatMessage,EODReport,Organization
from hr_crew.crewai_runner import (
    run_crewai_onboarding, manual_onboarding, retry_onboarding,
    manual_recruitment, auto_recruitment, retry_recruitment
)
from marketing_crew.crewai_runner import (
    market_research_manual, market_research_auto, seo_auto, seo_manual,
    social_auto, social_manual
)
from sales_crew.crewai_runner import (
    lead_generation_auto, lead_generation_manual, lead_generation_retry,
    content_generation_auto, content_generation_manual, content_generation_retry,
    sales_auto, sales_manual, sales_retry, crm_auto, crm_manual, crm_retry
)

from django.utils.timezone import now
from django.db.models import F
from django.db import transaction

def update_agent_usage(agent_id, org):
    """
    Updates the agent usage count and total messages in the EODReport 
    for the given organization and agent_id.
    If no report exists for today, it creates one.
    """
    organization = Organization.objects.get(id=org)
    
    agent_mapping = {
        1: "onboarding",
        2: "recruitment",
        3: "seo",
        4: "market_research",
        5: "lead_generation",
        6: "content_generation",
        7: "social",
        8: "crm",
        9: "sales",
    }

    agent_name = agent_mapping.get(agent_id)
    if not agent_name:
        raise ValueError("Invalid agent_id")

    today = now().date()

    with transaction.atomic():
        report, created = EODReport.objects.get_or_create(
            organization=organization,
            date=today,
            defaults={"agent_usage": {}, "total_messages": 0}
        )

        # Update agent usage count
        agent_usage = report.agent_usage
        agent_usage[agent_name] = agent_usage.get(agent_name, 0) + 1
        report.agent_usage = agent_usage

        # Increment total_messages count
        report.total_messages = report.total_messages + 1

        # Update the number of unique agents used
        report.total_agents_used = len(agent_usage)

        report.save(update_fields=["agent_usage", "total_messages", "total_agents_used"])
    
    return report
def _get_agent_function(agent_id, mode="auto"):
    """
    Returns the appropriate function based on the agent_id and mode.
    """
    agent_functions = {
        1: {"auto": run_crewai_onboarding, "manual": manual_onboarding, "retry": retry_onboarding},
        2: {"auto": auto_recruitment, "manual": manual_recruitment, "retry": retry_recruitment},
        3: {"auto": seo_auto, "manual": seo_manual},
        4: {"auto": market_research_auto, "manual": market_research_manual},
        5: {"auto": lead_generation_auto, "manual": lead_generation_manual, "retry": lead_generation_retry},
        6: {"auto": content_generation_auto, "manual": content_generation_manual, "retry": content_generation_retry},
        7: {"auto": social_auto, "manual": social_manual},
        8: {"auto": crm_auto, "manual": crm_manual, "retry": crm_retry},
        9: {"auto": sales_auto, "manual": sales_manual, "retry": sales_retry},
    }

    return agent_functions.get(agent_id, {}).get(mode, content_generation_auto if mode == "auto" else content_generation_manual)

def handle_crew_view(message_id, form_data):
    """
    Handle automated agent processes based on message_id.
    """
    org=get_organization_id_from_chat_message(message_id)
    try:
        chat_message = ChatMessage.objects.get(id=message_id)
        agent_id = chat_message.session.agent.id

        # Store the message in MongoDB
        chat_message.message_to_mongo({'user': 'user', 'form': form_data})

        # Execute the corresponding function
        agent_function = _get_agent_function(agent_id, "auto")
        result = agent_function(message_id, form_data)
        update_agent_usage(agent_id,org)

        return JsonResponse({
            "status": "success",
            "message": result,
            "agent_id": agent_id,
            "timestamp": datetime.now(),
        })

    except ChatMessage.DoesNotExist:
        return JsonResponse({"error": "ChatMessage not found"}, status=404)
    except AttributeError as e:
        return JsonResponse({"error": str(e)}, status=500)

def handle_crew_manual_view(message, message_id):
    """
    Handle manual agent processes based on message_id.
    """
    org=get_organization_id_from_chat_message(message_id)
    try:
        chat_message = ChatMessage.objects.get(id=message_id)
        agent_id = chat_message.session.agent.id

        # Store the message in MongoDB
        chat_message.message_to_mongo({'user': 'user', 'message': message})

        # Execute the corresponding function
        agent_function = _get_agent_function(agent_id, "manual")

        if agent_id in [3, 4, 5, 6, 7, 8, 9]:  # Agents returning a tuple
            response_message, response_type, response_content = agent_function(message_id, message)
            response = {
                "status": "success",
                "message": response_message,
                "content": response_content,
                "Type": response_type,
            }
        else:
            response = {
                "status": "success",
                "message": agent_function(message_id, message),
                "Type": "text",
            }
        update_agent_usage(agent_id,org)
        response.update({"user": "AI", "timestamp": datetime.now()})
        chat_message.message_to_mongo(response)

        return JsonResponse(response)

    except ChatMessage.DoesNotExist:
        return JsonResponse({"error": "ChatMessage not found"}, status=404)
    except AttributeError as e:
        return JsonResponse({"error": str(e)}, status=500)

def handle_crew_retry_view(message_id):
    """
    Handle retry agent processes based on message_id.
    """
    org=get_organization_id_from_chat_message(message_id)
    try:
        chat_message = ChatMessage.objects.get(id=message_id)
        agent_id = chat_message.session.agent.id

        # Store the retry request in MongoDB
        chat_message.message_to_mongo({'user': 'user', 'message': "retry"})

        # Execute the retry function
        agent_function = _get_agent_function(agent_id, "retry")
        result = agent_function(chat_message)
        update_agent_usage(agent_id,org)

        return JsonResponse({
            "status": "success",
            "message": result,
            "agent_id": agent_id,
            "timestamp": datetime.now(),
        })

    except ChatMessage.DoesNotExist:
        return JsonResponse({"error": "ChatMessage not found"}, status=404)
    except AttributeError as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_agent_usage(agent_id, org):
    """
    Updates the agent usage count and total messages in the EODReport 
    for the given organization and agent_id.
    If no report exists for today, it creates one.
    """
    organization = Organization.objects.get(id=org)
    
    agent_mapping = {
        1: "onboarding",
        2: "recruitment",
        3: "seo",
        4: "market_research",
        5: "lead_generation",
        6: "content_generation",
        7: "social",
        8: "crm",
        9: "sales",
    }

    agent_name = agent_mapping.get(agent_id)
    if not agent_name:
        raise ValueError("Invalid agent_id")

    today = now().date()

    with transaction.atomic():
        report, created = EODReport.objects.get_or_create(
            organization=organization,
            date=today,
            defaults={"agent_usage": {}, "total_messages": 0}
        )

        # Update agent usage count
        agent_usage = report.agent_usage
        agent_usage[agent_name] = agent_usage.get(agent_name, 0) + 1
        report.agent_usage = agent_usage

        # Increment total_messages count
        report.total_messages = report.total_messages + 1

        # Update the number of unique agents used
        report.total_agents_used = len(agent_usage)

        report.save(update_fields=["agent_usage", "total_messages", "total_agents_used"])
    
    return report

def get_organization_id_from_chat_message(chat_message_id):
    """
    Given a chat message ID, returns the corresponding organization's ID.
    """
    try:
        chat_message = ChatMessage.objects.select_related('session__organization').get(id=chat_message_id)
        return chat_message.session.organization.id
    except ChatMessage.DoesNotExist:
        return None  # or raise an exception if needed


