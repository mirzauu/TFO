from django.db import models
from datetime import datetime
# Create your models here.
from organizations.models import ChatMessage
import json
class MarketResearch(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="market_research_sessions")
    topic = models.CharField(max_length=50)
    complete = models.BooleanField(default=False)
      # Unique identifier for companies

    def __str__(self):
        return f"Market Research for {self.topic}"
    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.research_tasks.filter(status="COMPLETED").count() == self.research_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])


class MarketResearchTask(models.Model):
    research = models.ForeignKey(
        MarketResearch,
        on_delete=models.CASCADE,
        related_name="research_tasks"
    )
  
    task_name = models.CharField(max_length=255, blank=True, null=True)  

    status = models.CharField(
        max_length=50,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    error_message = models.TextField(blank=True, null=True)  
    final_report = models.TextField(blank=True, null=True)  
    formate = models.TextField(blank=True, null=True)  
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)  

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.research.topic}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_report changes.
        """
        super().save(*args, **kwargs)  # Call original save method

        # If final_report exists, save it as a message in MongoDB
        if self.output:
        
            if self.formate == "Analysis report":
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="survey out":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No descriptions available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)    

            elif self.formate=="competitor analyst":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No templates available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)    

            elif self.formate=="text":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("brochure", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="email templates":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("templates", "No templates available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="discription":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("descriptions", "No descriptions available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="price report":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No descriptions available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
                    
            elif self.formate=="slides":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("topic", "No response available")
                    brochure_text = self.output.get("slides", "No slides available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="sales pitch":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No slides available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)    

            elif self.formate=="posts":  
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("posts", "No ppt available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
                    
        self.research.check_completion_status()    


class SEOResearch(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="seo_research_sessions")
    website_name = models.CharField(max_length=255)
    competitors = models.TextField(help_text="List of competitors, separated by commas")
    target_audience = models.TextField(help_text="Description of the target audience")
    ad_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Ad budget in USD")
    primary_goals = models.TextField(help_text="Primary goals for the SEO campaign")
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"SEO Research for {self.website_name}"

    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.seo_tasks.filter(status="COMPLETED").count() == self.seo_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])


class SEOResearchTask(models.Model):
    research = models.ForeignKey(
        SEOResearch,
        on_delete=models.CASCADE,
        related_name="seo_tasks"
    )
    task_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    error_message = models.TextField(blank=True, null=True)
    final_report = models.TextField(blank=True, null=True)
    formate = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.research.website_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_report changes.
        """
        super().save(*args, **kwargs)  # Call original save method

        # If final_report exists, save it as a message in MongoDB
        if self.output:
            if self.formate == "Analysis report":
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="posts":  
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("posts", "No ppt available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="swot analysis":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="competitor analyst":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No templates available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="price report":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No descriptions available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="sales pitch":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No slides available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="posts":  
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("posts", "No ppt available")
                    print("reached 2nd", response_text, brochure_text)
                
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

        self.research.check_completion_status()


class SocialMediaResearch(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="social_media_research_sessions")
    competitors = models.TextField(help_text="List of competitors, separated by commas")
    campaign_theme = models.CharField(max_length=255, help_text="Theme of the campaign")
    target_audience = models.CharField(max_length=255, help_text="Target audience for the campaign")
    platform = models.TextField(help_text="Platforms where the campaign will be run, separated by commas")
    goal = models.TextField(help_text="Objective of the campaign")
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Social Media Research for {self.campaign_theme}"

    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.social_media_tasks.filter(status="COMPLETED").count() == self.social_media_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])


class SocialMediaResearchTask(models.Model):
    research = models.ForeignKey(
        SocialMediaResearch,
        on_delete=models.CASCADE,
        related_name="social_media_tasks"
    )
    task_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    error_message = models.TextField(blank=True, null=True)
    final_report = models.TextField(blank=True, null=True)
    formate = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.research.campaign_theme}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_report changes.
        """
        super().save(*args, **kwargs)  # Call original save method

        # If final_report exists, save it as a message in MongoDB
        if self.output:
          
            if self.formate == "Analysis report":
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="competitor analyst":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No templates available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)    

            elif self.formate=="text":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("brochure", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="email templates":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("templates", "No templates available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="discription":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("descriptions", "No descriptions available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="slides":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("topic", "No response available")
                    brochure_text = self.output.get("slides", "No slides available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

            elif self.formate=="sales pitch":   
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("details", "No slides available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)    

            elif self.formate=="posts":  
                if isinstance(self.output, str):  # If it's a JSON string, convert to dict
                    try:
                        self.output = json.loads(self.output)
                    except json.JSONDecodeError as e:
                        print("JSON decoding error:", e)
                        self.output = {}

                if isinstance(self.output, dict):  # Now check if it's a dict
                    response_text = self.output.get("response", "No response available")
                    brochure_text = self.output.get("posts", "No ppt available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.research.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

        self.research.check_completion_status()
