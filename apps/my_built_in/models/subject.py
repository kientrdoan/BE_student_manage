from django.db import models

class Subject(models.Model):
    code= models.CharField(max_length=50)
    name= models.CharField(max_length=50)
    credit= models.IntegerField()
    description= models.CharField(500)
    total_period= models.IntegerField()
    theory_period= models.IntegerField()
    lab_period= models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subjects"