from django.db import models
from datetime import datetime
# Create your models here.
from organizations.models import ChatMessage
# Create your models here.
import json

class LeadGeneration(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="lead_generation_sessions")
    topic = models.CharField(max_length=50)
    complete = models.BooleanField(default=False)  # New boolean field

    def __str__(self):
        return f"Lead Generation for {self.topic}"

    def check_completion_status(self):
      
        all_completed = self.lead_generation_tasks.filter(status="COMPLETED").count() == self.lead_generation_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])  # Avoid infinite recursion

class LeadGenerationTask(models.Model):
    lead_generation = models.ForeignKey(
        LeadGeneration,
        on_delete=models.CASCADE,
        related_name="lead_generation_tasks"
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
        return f"{self.task_name} - {self.status} for {self.lead_generation.topic}"

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
            
                self.lead_generation.session.save_message_to_mongo({
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
            
                self.lead_generation.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
            elif self.formate=="social media lead":   
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
            
                self.lead_generation.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
           
        # Check if the LeadGeneration should be marked as complete
        self.lead_generation.check_completion_status()




class ContentCreation(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="content_creation_sessions")
    topic = models.CharField(max_length=50)
    complete = models.BooleanField(default=False)  

    def __str__(self):
        return f"Content Creation for {self.topic}"

    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.content_creation_tasks.filter(status="COMPLETED").count() == self.content_creation_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])  

class ContentCreationTask(models.Model):
    content_creation = models.ForeignKey(
        ContentCreation,
        on_delete=models.CASCADE,
        related_name="content_creation_tasks"
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
    final_content = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)
    formate = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.content_creation.topic}"

    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_content changes.
        """
        super().save(*args, **kwargs)  # Call original save method
        
        # Ensure output exists and is a dictionary
        print("reached 1st")
        print("self.output:", self.output, type(self.output))
        if self.output:
            if self.formate == "brochure":
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
            
                self.content_creation.session.save_message_to_mongo({
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
            
                self.content_creation.session.save_message_to_mongo({
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
            
                self.content_creation.session.save_message_to_mongo({
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
            
                self.content_creation.session.save_message_to_mongo({
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
            
                self.content_creation.session.save_message_to_mongo({
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
            
                self.content_creation.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)


        # Check if the ContentCreation should be marked as complete
        self.content_creation.check_completion_status()

class SalesStrategy(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="sales_strategy_sessions")
    industry_sector = models.TextField()  # Description of the product or service
    target_market = models.CharField(max_length=100)  # Specific sales strategy topic (e.g., "Cold Email Outreach")
    timeframe = models.TextField()  # Description of the ideal audience
    data_source = models.CharField(max_length=100)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Sales Strategy for {self.industry_sector[:30]} - {self.target_market}"

    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.sales_strategy_tasks.filter(status="COMPLETED").count() == self.sales_strategy_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])


class SalesStrategyTask(models.Model):
    sales_strategy = models.ForeignKey(
        SalesStrategy,
        on_delete=models.CASCADE,
        related_name="sales_strategy_tasks"
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
    final_content = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)
    formate = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.sales_strategy.industry_sector}"

    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_content changes.
        """
        super().save(*args, **kwargs)  # Call original save method

        # If final_content exists, save it as a message in MongoDB

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
            
                self.sales_strategy.session.save_message_to_mongo({
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
            
                self.sales_strategy.session.save_message_to_mongo({
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
            
                self.sales_strategy.session.save_message_to_mongo({
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
            
                self.sales_strategy.session.save_message_to_mongo({
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
            
                self.sales_strategy.session.save_message_to_mongo({
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
                
                self.sales_strategy.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)

        # Check if the SalesStrategy should be marked as complete
        self.sales_strategy.check_completion_status()


class CustomerRelationshipManagement(models.Model):
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="crm_sessions")
    topic = models.CharField(max_length=100)  # Topic of the CRM strategy (e.g., "Customer Retention Plan")
    customer_segment = models.CharField(max_length=255)  # E.g., "Enterprise Clients", "Small Businesses"
    interaction_history = models.CharField(max_length=255) # Stores previous customer interactions
    preferred_communication_channel =models.CharField(max_length=255)
    business_goal = models.TextField()  # E.g., "Increase customer retention by 20% in Q2"
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"CRM Strategy: {self.topic} for {self.customer_segment}"

    def check_completion_status(self):
        """
        Check if all related tasks are completed and update the 'complete' status.
        """
        all_completed = self.crm_tasks.filter(status="COMPLETED").count() == self.crm_tasks.count()
        if all_completed:
            self.complete = True
            self.save(update_fields=["complete"])


class CRMTask(models.Model):
    crm_strategy = models.ForeignKey(
        CustomerRelationshipManagement,
        on_delete=models.CASCADE,
        related_name="crm_tasks"
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
    final_content = models.TextField(blank=True, null=True)
    formate = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.crm_strategy.topic}"

    def save(self, *args, **kwargs):
        """
        Override save method to update MongoDB when final_content changes.
        """
        super().save(*args, **kwargs)  # Call original save method

        # If final_content exists, save it as a message in MongoDB
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
            
                self.crm_strategy.session.save_message_to_mongo({
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
            
                self.crm_strategy.session.save_message_to_mongo({
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
                    brochure_text = self.output.get("details", "No brochure available")
                    print("reached 2nd", response_text, brochure_text)
            
                self.crm_strategy.session.save_message_to_mongo({
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
            
                self.crm_strategy.session.save_message_to_mongo({
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
            
                self.crm_strategy.session.save_message_to_mongo({
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
            
                self.crm_strategy.session.save_message_to_mongo({
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
            
                self.crm_strategy.session.save_message_to_mongo({
                    "Type": self.formate,
                    "message": response_text,
                    "content": brochure_text,
                    "task_name": self.task_name,
                    "updated_at": datetime.now(),
                    "user": "AI",
                }, task_name=self.task_name)
        
        # Check if the CRM strategy should be marked as complete
        self.crm_strategy.check_completion_status()
