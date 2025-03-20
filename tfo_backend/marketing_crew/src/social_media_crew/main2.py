#!/usr/bin/env python
import sys
import warnings

from marketing_crew.src.social_media_crew.manager import SocialMediaCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = inputs = {
        
        'competitors': "",
        'campaign_theme': "",
        'target_audience': "",
        'platform': "",
        'goal': "",
        'current_year':"",
        "human_task": "Can you come up with some catchy Instagram captions and hashtag ideas for a fitness brand’s New Year campaign? The goal is to get Gen Z excited about setting and achieving their fitness resolutions!"

    }
    SocialMediaCrew().crew().kickoff(inputs=inputs)

