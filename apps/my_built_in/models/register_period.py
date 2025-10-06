from django.db import models

class RegisterPeriod(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE, db_column="semester_id", related_name="register_periods")

    class Meta:
        db_table = "registration_periods"