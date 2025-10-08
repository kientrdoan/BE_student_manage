from django.db import models

class LopSinhVien(models.Model):
    name = models.CharField(max_length=50, null= True)
    major = models.ForeignKey('Nganh', db_column="major_id", on_delete=models.CASCADE ,null=True, related_name="lop_sinh_vien")
    start_year= models.IntegerField(null=True)
    end_year= models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'lop_sinh_vien'
        # verbose_name = 'Class'
        # verbose_name_plural = 'Classes'