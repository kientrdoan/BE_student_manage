from django.db import models

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    major = models.ForeignKey('Major', db_column="major_id", on_delete=models.CASCADE, related_name='specialization')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "specializations"

    def __str__(self):
        return self.name