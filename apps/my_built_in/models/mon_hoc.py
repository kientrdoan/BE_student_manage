from django.db import models

class MonHoc(models.Model):
    code= models.CharField(max_length=50)
    name= models.CharField(max_length=50)
    credit= models.IntegerField()
    description= models.CharField(max_length=500, null=True, blank=True)
    total_period= models.IntegerField()

    major = models.ForeignKey('Nganh', on_delete=models.CASCADE, db_column="major_id", related_name="mon_hoc")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "mon_hoc"