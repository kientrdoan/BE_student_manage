from django.db import models

class SinhVien(models.Model):
    user = models.ForeignKey('TaiKhoan', db_column="user_id", related_name="sinh_vien", on_delete=models.CASCADE)
    class_student = models.ForeignKey('LopSinhVien', db_column="class_id", related_name="sinh_vien", on_delete=models.CASCADE)
    student_code = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = "sinh_vien"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"