from django.db import models

class Semester(models.Model):
    semesters = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'semesters'