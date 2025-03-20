from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Role(models.Model):
    """
    Role model to define permissions and categories of roles.
    """
    ROLE_CHOICES = [
        ('company_admin', 'Company Admin'),
        ('company_staff', 'Company Staff'),
        ('organization_admin', 'Organization Admin'),
        ('organization_staff', 'Organization Staff'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()  # Better readability for choices


class User(AbstractUser):
    """
    Custom User model supporting multiple user types through role assignments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(
        'Role',  # Replace 'Role' with your related model
        on_delete=models.CASCADE,
        null=False,
        default=1,  # Replace with an appropriate default value
    )
    entity_id = models.UUIDField(null=True, blank=True)  # Links to Company or Organization
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    

    def __str__(self):
        return f"{self.email} ({self.role.name})"

class Company(models.Model):
    """
    Company model to represent organizations owning the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CompanyStaff(models.Model):
    """
    CompanyStaff model for employees working under a company.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)  # Links to the User model
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name