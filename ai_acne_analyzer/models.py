# Remove the Questionnaire model
from django.db import models

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    aws_url = models.URLField(blank=True, null=True)
    analysis_results = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
