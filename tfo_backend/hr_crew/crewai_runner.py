from .src.onboarding.main import main,retry,manual
from .src.recruitment.trying import manual as ma,auto,reload

def run_crewai_onboarding(message_id,form):

    return main(message_id,form)  # Call the main function from main.py
  
def retry_onboarding(message_id):

    return retry(message_id)  # Call the main function from main.py

def retry_recruitment(message_id):

    return reload(message_id)  # Call the main function from main.py
  
def manual_onboarding(message_id,message):

    return manual(message_id,message)  # Call the main function from main.py
  
def manual_recruitment(message_id,message):

    return ma(message_id,message)  # Call the main function from main.py
def auto_recruitment(message_id,form):

    return auto(message_id,form)  # Call the main function from main.py
  
