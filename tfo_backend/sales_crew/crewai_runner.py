from .src.lead_generation_team import main as lead_main ,main2 as lead_main2,chatrun
from .src.content_creation_team import main as content_main ,chat2 as content_main2
from .src.sales_strategy_team import main as sales_main ,chatrun as sales_main2
from .src.crm_team import main as crm_main ,chatrun as crm_main2

import asyncio



def lead_generation_auto(message_id,message):

    return lead_main.run(message_id=message_id,message=message) 

def lead_generation_manual(message_id,message):

    message,formate,content = asyncio.run(chatrun.run(message_id, message))
    return message,formate,content

def lead_generation_retry(message_id):

    return lead_main.retry(message_id) 

# content creation

def content_generation_auto(message_id,message):

    return content_main.run(message_id=message_id,message=message) 


def content_generation_manual(message_id, message):
    print("content reached")

    # Ensure the async function is awaited
    message,formate,content = asyncio.run(content_main2.run(message_id, message))
    return message,formate,content
def content_generation_retry(message_id):

    return content_main.retry(message_id) 

# sales strategy

def sales_auto(message_id,message):

    return sales_main.run(message_id=message_id,message=message) 

def sales_manual(message_id,message):

    message,formate,content = asyncio.run(sales_main2.run(message_id, message))
    return message,formate,content

def sales_retry(message_id):

    return sales_main.retry(message_id) 

# crm 

def crm_auto(message_id,message):

    return crm_main.run(message_id=message_id,message=message) 

def crm_manual(message_id,message):

    message,formate,content = asyncio.run(crm_main2.run(message_id, message))
    return message,formate,content

def crm_retry(message_id):

    return crm_main.retry(message_id) 