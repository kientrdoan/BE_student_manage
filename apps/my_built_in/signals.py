from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.my_built_in.models import BuoiHoc, DangKy, ThamDu


@receiver(post_save, sender=BuoiHoc)
def create_attendance_records(sender, instance, created, **kwargs):
    """
    Tự động tạo bản ghi ThamDu với status='Absent' cho tất cả sinh viên
    khi tạo BuoiHoc mới.
    """
    if created:
        # Lấy tất cả sinh viên đã đăng ký lớp này
        enrollments = DangKy.objects.filter(
            course=instance.course,
            is_deleted=False
        )
        
        # Tạo bản ghi ThamDu cho từng sinh viên
        attendance_records = [
            ThamDu(
                enrollment=enrollment,
                time_slot=instance,
                status='Absent',
                is_deleted=False
            )
            for enrollment in enrollments
        ]
        
        # Bulk create để tối ưu performance
        ThamDu.objects.bulk_create(attendance_records, ignore_conflicts=True)
