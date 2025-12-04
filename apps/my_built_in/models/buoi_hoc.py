from django.db import models

class BuoiHoc(models.Model):
    course= models.ForeignKey('LopTinChi', on_delete=models.CASCADE, related_name='buoi_hoc')
    # start_period= models.IntegerField()
    date = models.DateField()
    is_attendance_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'buoi_hoc'

    def __str__(self):
        return f"{self.date}"