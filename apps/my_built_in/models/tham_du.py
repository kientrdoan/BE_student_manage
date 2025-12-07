from django.db import models

class ThamDu(models.Model):
    """
    Bảng lưu trạng thái điểm danh của từng sinh viên.
    """
    STATUS_CHOICES = [
        ('Present', 'Có mặt'),
        ('Absent', 'Vắng mặt'),
        ('Pending', 'Chờ duyệt'),
        ('Late', 'Muộn'),
        ('Excused', 'Có phép'),
    ]
    
    enrollment = models.ForeignKey('DangKy', db_column="enroll_id", on_delete=models.CASCADE)
    time_slot = models.ForeignKey('BuoiHoc', db_column="time_slot_id", on_delete=models.CASCADE)
    
    # URL ảnh điểm danh (nếu sinh viên có mặt trong ảnh nào đó)
    attendance_image = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text='URL ảnh điểm danh có khuôn mặt sinh viên này'
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Absent'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        db_table = 'tham_du'

    def __str__(self):
        return f"{self.time_slot} - {self.status}"