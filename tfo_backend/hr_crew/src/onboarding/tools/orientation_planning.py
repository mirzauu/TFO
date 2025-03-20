import os
from datetime import datetime, timedelta
from langchain.tools import tool
from typing import Dict
@tool
def check_orientation_schedule(newhireinfo: Dict) -> str:
    """
    Checks the status of the orientation schedule in the newhireinfo dictionary.

    Args:
        newhireinfo (Dict): Dictionary containing the new hire's onboarding details.

    Returns:
        str: Status of the orientation schedule - "completed", "pending", or "invalid".
    """
    orientation_status = newhireinfo.get("orientation_schedule", "N/A").strip().lower()
    if orientation_status in ["completed", "successful"]:
        return "completed"
    elif orientation_status in ["pending", "not started", "in progress"]:
        return "pending"
    else:
        return "invalid"

@tool("TaskSchedulerTool")
def schedule_task(task_name: str = "Default Task", 
                  start_date: str = None, 
                  duration_days: int = 30) -> str:
    """
    Schedules a task using individual arguments. Default values are used if arguments are missing.

    Args:
        task_name (str, optional): Name of the task. Defaults to "Default Task".
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to today's date.
        duration_days (int, optional): Duration of the task in days. Defaults to 30.

    Returns:
        str: Confirmation message about the scheduled task or an error message if validation fails.
    """
    # Set default start date if not provided
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")

    # Validate duration_days
    try:
        duration_days = int(duration_days)
    except ValueError:
        return f"Error: 'duration_days' must be an integer. Received: {duration_days}"

    # Parse dates and calculate the schedule
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = start_date_obj + timedelta(days=duration_days)
        return (
            f"Task '{task_name}' scheduled from {start_date_obj.strftime('%Y-%m-%d')} "
            f"to {end_date_obj.strftime('%Y-%m-%d')}."
        )
    except ValueError as e:
        return f"Error parsing dates: {e}"




# class MentorshipAssignmentTool:
#     @tool("MentorshipAssignmentTool")
#     def assign_mentor(self, new_hire: str, mentor: str, start_date: str) -> str:
#         """
#         Assigns a mentor to a new hire starting from a specified date.

#         Args:
#             new_hire (str): Name or ID of the new hire.
#             mentor (str): Name of the mentor.
#             start_date (str): Start date of the mentorship in 'YYYY-MM-DD' format.

#         Returns:
#             str: Confirmation message about the mentor assignment.
#         """
#         try:
#             datetime.strptime(start_date, "%Y-%m-%d")  # Validate date format
#             return (f"Mentor '{mentor}' assigned to '{new_hire}' starting on {start_date}.")
#         except ValueError as e:
#             return f"Error parsing date: {e}"



# mentorship_assignment_tool = MentorshipAssignmentTool()

# # # Create instances of the tools
# # schedule_task_tool = TaskSchedulerTool(task_name="Orientation", start_date="2025-01-15", duration_days=7)
# # mentorship_assignment_tool = MentorshipAssignmentTool(new_hire="Jane Smith", mentor="John Doe", start_date="2025-01-16")
