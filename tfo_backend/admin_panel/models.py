from django.db import models

class APIKey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    value = models.TextField()  # Store plain API key

    def __str__(self):
        return self.name
