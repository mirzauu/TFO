from .src.market_research_team import main as market_main,chatrun as market_main2
from .src.seo_sem_crew import main as seo_main,chatrun as seo_main2
from .src.social_media_crew import main as social_main,chatrun as social_main2
import asyncio


def market_research_auto(message_id,message):

    return market_main.run(message_id,message) 
  
def market_research_manual(message_id,message):

    message,formate,content = asyncio.run(market_main2.run(message_id, message))
    return message,formate,content

# seo

def seo_auto(message_id,message):

    return seo_main.run(message_id,message) 
  
def seo_manual(message_id,message):

    message,formate,content = asyncio.run(seo_main2.run(message_id, message))
    return message,formate,content

# social

def social_auto(message_id,message):

    return social_main.run(message_id,message) 
  
def social_manual(message_id,message):

    message,formate,content = asyncio.run(social_main2.run(message_id, message))
    return message,formate,content