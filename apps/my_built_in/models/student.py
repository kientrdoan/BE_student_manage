from django.db import models

class Student(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    student_code = models.CharField(max_length=50)
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE)

    class Meta:
        db_table = "students"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"