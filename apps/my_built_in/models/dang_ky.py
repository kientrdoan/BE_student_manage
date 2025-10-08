from django.db import models

class DangKy(models.Model):
    student = models.ForeignKey('SinhVien', db_column="student_id", on_delete=models.CASCADE, related_name="dang_ky")
    course = models.ForeignKey('LopTinChi', db_column="course_id", on_delete=models.CASCADE, related_name="dang_ky")
    status = models.CharField(max_length=50)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "dang_ky"

    def __str__(self):
        return f"Enrollment of {self.student} in {self.course}"