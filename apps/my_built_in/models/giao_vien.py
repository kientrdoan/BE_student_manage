from django.db import models

class GiaoVien(models.Model):
    user = models.ForeignKey('TaiKhoan', db_column="user_id", on_delete=models.CASCADE, related_name="giao_vien")
    department = models.ForeignKey('Khoa', db_column="department_id", on_delete=models.CASCADE, related_name="giao_vien", null=True)
    teacher_code = models.CharField(max_length=50)
    degree = models.CharField(max_length=100)
    title= models.CharField(max_length=100)
    
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        db_table = "giao_vien"

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"