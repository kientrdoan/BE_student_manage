from django.db import models

class Class(models.Model):
    major_id= models.ForeignKey('Major', on_delete=models.CASCADE)
    specialization_id= models.ForeignKey('Specialization', on_delete=models.CASCADE) 
    start_year= models.IntegerField()
    end_year= models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'