from django.db import models

# from apps.my_built_in.models.mon_hoc import Subject
from apps.my_built_in.models.phong_hoc import PhongHoc

class LopTinChi(models.Model):

    semester = models.ForeignKey('HocKy', on_delete=models.CASCADE, db_column="semester_id", related_name="lop_tin_chi")
    subject = models.ForeignKey("MonHoc", on_delete=models.CASCADE, db_column="subject_id", related_name="lop_tin_chi")
    teacher = models.ForeignKey('GiaoVien', null=True, blank=True, on_delete=models.CASCADE, db_column="teacher_id", related_name="lop_tin_chi")
    class_st = models.ForeignKey('LopSinhVien', on_delete=models.CASCADE, db_column="class_id", related_name="lop_tin_chi")
    room = models.ForeignKey(PhongHoc, null=True, on_delete=models.CASCADE, db_column="room_id", related_name="lop_tin_chi")

    max_capacity = models.IntegerField()

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    weekday = models.CharField(max_length=20, null=True, blank=True)
    start_period = models.IntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted= models.BooleanField(default=False)

    class Meta:
        db_table = 'lop_tin_chi'