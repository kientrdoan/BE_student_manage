from django.db import models

class Major(models.Model):
    name = models.CharField(max_length=100, null=True)
    department = models.ForeignKey('Department', db_column="department_id", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "majors"

    def __str__(self):
        return self.name