from django.db import models

class Nganh(models.Model):
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey('Khoa', db_column="department_id", on_delete=models.CASCADE, related_name="nganh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "nganh"

    def __str__(self):
        return self.name