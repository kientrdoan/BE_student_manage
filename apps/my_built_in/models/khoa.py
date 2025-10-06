from django.db import models

class Khoa(models.Model):
    code= models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "khoa"

    def __str__(self):
        return self.name