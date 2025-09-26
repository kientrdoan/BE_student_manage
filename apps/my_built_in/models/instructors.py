from django.db import models

class Instructor(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    instructor_code = models.CharField(max_length=50)
    degree = models.CharField(max_length=100)
    title= models.CharField(max_length=100)
    deparmtment_id = models.ForeignKey('Department', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        db_table = "instructors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"