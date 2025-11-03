from django.db import models

class HocKy(models.Model):
    semesters = models.CharField(max_length=100)
    year = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    open_date= models.DateField()
    close_date = models.DateField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'hoc_ky'