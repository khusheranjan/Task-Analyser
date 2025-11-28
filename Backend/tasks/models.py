from django.db import models

# Create your models here.
class Task(models.Model):
    
    title = models.CharField(max_length=200)
    due_date = models.DateField(blank=True, null=True)
    estimated_hours = models.FloatField()
    importance = models.IntegerField()
    dependencies = models.JSONField(default=list)

    def __str__(self):
        return self.title