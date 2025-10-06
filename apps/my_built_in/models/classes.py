from django.db import models

class Class(models.Model):
    name = models.CharField(max_length=50, null= True)
    major = models.ForeignKey('Major', on_delete=models.CASCADE ,null=True)
    start_year= models.IntegerField(null=True)
    end_year= models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'