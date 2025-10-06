from django.db import models

class Instructor(models.Model):
    user = models.ForeignKey('User', db_column="user_id", on_delete=models.CASCADE)
    instructor_code = models.CharField(max_length=50)
    degree = models.CharField(max_length=100)
    title= models.CharField(max_length=100)
    department = models.ForeignKey('Department', db_column="department_id", on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    class Meta:
        db_table = "instructors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"