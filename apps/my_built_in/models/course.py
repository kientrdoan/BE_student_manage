from django.db import models

from apps.my_built_in.models.subject import Subject

class Course(models.Model):

    semester = models.ForeignKey('Semester', on_delete=models.CASCADE, db_column="semester_id", related_name="courses")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column="subject_id", related_name="courses")
    instructor = models.ForeignKey('Instructor', on_delete=models.CASCADE, db_column="instructor_id", related_name="courses")
    class_st = models.ForeignKey('Class', on_delete=models.CASCADE, db_column="class_id", related_name="courses")

    max_capacity = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'courses'