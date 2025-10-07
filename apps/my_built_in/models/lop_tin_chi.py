from django.db import models

# from apps.my_built_in.models.mon_hoc import Subject
from apps.my_built_in.models.phong_hoc import PhongHoc

class LopTinChi(models.Model):

    semester = models.ForeignKey('HocKy', on_delete=models.CASCADE, db_column="semester_id", related_name="lop_tin_chi")
    subject = models.ForeignKey("MonHoc", on_delete=models.CASCADE, db_column="subject_id", related_name="lop_tin_chi")
    teacher = models.ForeignKey('GiaoVien', on_delete=models.CASCADE, db_column="teacher_id", related_name="lop_tin_chi")
    class_st = models.ForeignKey('LopTinChi', on_delete=models.CASCADE, db_column="class_id", related_name="lop_tin_chi")
    room = models.ForeignKey(PhongHoc, on_delete=models.CASCADE, db_column="room_id", related_name="lop_tin_chi")

    max_capacity = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted= models.BooleanField(default=False)

    class Meta:
        db_table = 'lop_tin_chi'