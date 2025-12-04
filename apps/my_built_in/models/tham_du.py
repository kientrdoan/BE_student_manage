from django.db import models

class ThamDu(models.Model):
    enrollment = models.ForeignKey('DangKy', db_column="enroll_id", on_delete=models.CASCADE)
    time_slot = models.ForeignKey('BuoiHoc', db_column="time_slot_id", on_delete=models.CASCADE)

    status = models.CharField(null=True,max_length=50)
    attendance_image = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        db_table = 'tham_du'

    def __str__(self):
        return f"{self.time_slot} - {self.status}"