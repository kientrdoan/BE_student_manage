from django.db import models

class Student(models.Model):
    user = models.ForeignKey('User', related_name="user", on_delete=models.CASCADE)
    student_code = models.CharField(max_length=50)
    classes = models.ForeignKey('Class', db_column="class_id", related_name="classes", on_delete=models.CASCADE)

    class Meta:
        db_table = "students"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"