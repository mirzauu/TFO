from django.db import models
from organizations.models import ChatMessage
import uuid
from datetime import datetime
from pymongo import MongoClient



class Onboarding(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="onboarding_sessions")
    employee_id = models.CharField(max_length=50)  # Unique identifier for employees
    employee_name = models.CharField(max_length=50,blank=True, null=True)  # Unique identifier for employees
    employee_email = models.CharField(max_length=255,blank=True, null=True,unique=False)  # Task name
    completed=models.BooleanField(default=False)

class EmployeeDocuments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding = models.OneToOneField(Onboarding, on_delete=models.CASCADE, related_name="employee_documents")
    
    # Document Uploads
    relieving_letter = models.FileField(upload_to='documents/relieving_letters/', blank=True, null=True)
    salary_slip = models.FileField(upload_to='documents/salary_slips/', blank=True, null=True)  # PDF or image

    # Aadhaar & PAN as Image Fields
    aadhaar_image = models.ImageField(upload_to='documents/aadhaar/', blank=True, null=True)
    pan_image = models.ImageField(upload_to='documents/pan/', blank=True, null=True)

    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)

    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Override save method to update the task status when the document is verified.
        """
        super().save(*args, **kwargs)  # Save the document first

        if self.verified:  # Check if verification is marked True
            # Find the 'Document Verification Task' related to this onboarding session
            document_task = EmployeeOnboardingTask.objects.filter(
                onboarding=self.onboarding,
                task_name="Document Verification Task"
            ).first()

            if document_task and document_task.status != "COMPLETED":
                document_task.status = "COMPLETED"
             
                document_task.final_report = f"✅ Document verification completed for {self.onboarding.employee_name}."
                document_task.save(update_fields=['status', 'updated_at', 'final_report'])

    def __str__(self):
        return f"Documents for {self.onboarding.employee_name}"

class EmployeeOnboardingTask(models.Model):
    onboarding = models.ForeignKey(
        Onboarding,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
  
    task_name = models.CharField(max_length=255,blank=True, null=True)  # Task name

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
    error_message = models.TextField(blank=True, null=True)  # Store errors if any
    final_report = models.TextField(blank=True, null=True)  # Store errors if any
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True) 

    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.onboarding.employee_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update onboarding completion status when all tasks are completed.
        """
        super().save(*args, **kwargs)  # Save the task first

        # Check if all related tasks are completed
        all_tasks_completed = not self.onboarding.tasks.exclude(status='COMPLETED').exists()

        # Update the onboarding completed field
        self.onboarding.completed = all_tasks_completed
        self.onboarding.save(update_fields=['completed'])

        # Save the final report to MongoDB if applicable
        if self.final_report:
            self.onboarding.session.save_message_to_mongo({
                "Type": "text",
                "message": self.final_report,
                "task_name": self.task_name,
                "updated_at": datetime.now(),
                "user": "AI",
            }, task_name=self.task_name)


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding_task = models.ForeignKey(
        Onboarding,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    education_qualification = models.FileField(upload_to='documents/education/', blank=True, null=True)
    resume = models.FileField(upload_to='documents/resumes/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Documents for {self.onboarding_task.employee_name}"



class Recruitment(models.Model):
    
    session = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="recruitment_sessions")
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_requirement = models.TextField()
    expected_reach_out = models.IntegerField()
    completed = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  
    
    def __str__(self):
        return self.job_title
    
    def update_completion_status(self):
        all_tasks_completed = all(status == 'COMPLETED' for status in self.tasks.values_list('status', flat=True))
        self.__class__.objects.filter(id=self.id).update(completed=all_tasks_completed)

class Candidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    resume_check = models.BooleanField(default=False)
    ats_score = models.IntegerField(blank=True, null=True, unique=False)
    screening = models.BooleanField(default=False)
    interview_status = models.BooleanField(default=False)
    selected = models.BooleanField(default=False)
    offer_letter = models.BooleanField(default=False)
    offer_letter_document = models.FileField(upload_to='offer_letters/', null=True, blank=True)  # Added field

    def __str__(self):
        return self.name
class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    time_slot = models.TimeField()
    meet_link = models.CharField(max_length=255,blank=True,null=True)
    is_booked = models.BooleanField(default=False)  # To track whether the slot is booked
    
    def __str__(self):
        return f"{self.date} - {self.time_slot} ({'Booked' if self.is_booked else 'Available'})"

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, related_name="booking")  # Ensures only one booking per slot
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="bookings")
    
    def save(self, *args, **kwargs):
        if self.schedule.is_booked:
            raise ValueError("This time slot is already booked.")
        self.schedule.is_booked = True  # Mark the schedule slot as booked
        self.schedule.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking for {self.candidate.name} on {self.schedule.date} at {self.schedule.time_slot}"


class RecruitmentTask(models.Model):
    recruitment = models.ForeignKey(
        Recruitment, on_delete=models.CASCADE, related_name="tasks"
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
    updated_at = models.DateTimeField(auto_now=True)
    output = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.task_name} - {self.status} for {self.recruitment.job_title}"
    

    def save(self, *args, **kwargs):
        """
        Override save method to update Recruitment completion status when all tasks are completed.
        """
        super().save(*args, **kwargs)  # Save the task first

        # Check if all related tasks are completed
        all_tasks_completed = not self.recruitment.tasks.exclude(status='COMPLETED').exists()

        # Update the recruitment completed field
        if all_tasks_completed:
            self.recruitment.completed = True
        else:
            self.recruitment.completed = False
        self.recruitment.save(update_fields=['completed'])

        # Save the final report to MongoDB if applicable
        if self.final_report and self.recruitment.session:
            self.recruitment.session.save_message_to_mongo({
                "Type": "text",
                "message": self.final_report,
                "task_name": self.task_name,
                "updated_at": datetime.now(),
                "user": "AI",
            }, task_name=self.task_name)