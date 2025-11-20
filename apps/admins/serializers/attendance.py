from rest_framework import serializers
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.sinh_vien import SinhVien


class AttendanceCreateSerializer(serializers.Serializer):
    """
    Serializer để tạo điểm danh từ ảnh có nhiều khuôn mặt
    """
    time_slot_id = serializers.IntegerField(required=True, help_text="ID của buổi học")
    image = serializers.ImageField(required=True, help_text="Ảnh chứa nhiều khuôn mặt sinh viên")
    threshold = serializers.FloatField(
        required=False,
        default=0.8,
        help_text="Ngưỡng để xác định khuôn mặt giống nhau (0.0 - 1.0)"
    )

    def validate_time_slot_id(self, value):
        """Kiểm tra buổi học có tồn tại không"""
        try:
            BuoiHoc.objects.get(id=value)
        except BuoiHoc.DoesNotExist:
            raise serializers.ValidationError("Buổi học không tồn tại")
        return value

    def validate_threshold(self, value):
        """Kiểm tra threshold hợp lệ"""
        if not 0.0 <= value <= 2.0:
            raise serializers.ValidationError("Threshold phải trong khoảng 0.0 - 2.0")
        return value


class AttendanceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer để hiển thị chi tiết điểm danh
    """
    student = serializers.SerializerMethodField()
    time_slot = serializers.SerializerMethodField()

    class Meta:
        model = ThamDu
        fields = [
            'id',
            'enrollment',
            'time_slot',
            'student',
            'status',
            'created_at',
            'update_at'
        ]

    def get_student(self, obj):
        """Lấy thông tin sinh viên"""
        if obj.enrollment and obj.enrollment.student:
            student = obj.enrollment.student
            return {
                'id': student.id,
                'student_code': student.student_code,
                'full_name': f"{student.user.first_name} {student.user.last_name}",
                'email': student.user.email
            }
        return None

    def get_time_slot(self, obj):
        """Lấy thông tin buổi học"""
        if obj.time_slot:
            time_slot = obj.time_slot
            return {
                'id': time_slot.id,
                'date': time_slot.date,
                'course_id': time_slot.course.id if time_slot.course else None,
                'subject_name': time_slot.course.subject.name if time_slot.course and time_slot.course.subject else None
            }
        return None


class AttendanceResultSerializer(serializers.Serializer):
    """
    Serializer cho kết quả điểm danh (với OCR validation)
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    room_code = serializers.CharField(required=False, allow_null=True)
    expected_room_code = serializers.CharField(required=False, allow_null=True)
    room_confidence = serializers.FloatField(required=False, allow_null=True)
    total_students = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    detected_faces = serializers.IntegerField()
    matched_faces = serializers.IntegerField()
    unmatched_faces = serializers.IntegerField()

    present_students = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    absent_students = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    attendance_records = serializers.ListField(
        child=AttendanceDetailSerializer(),
        required=False
    )
    visualized_image = serializers.CharField(required=False, allow_null=True)


class AttendanceListSerializer(serializers.ModelSerializer):
    """
    Serializer để list danh sách điểm danh của 1 buổi học
    """
    student_code = serializers.CharField(source='enrollment.student.student_code', read_only=True)
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='time_slot.course.subject.name', read_only=True)
    date = serializers.DateField(source='time_slot.date', read_only=True)

    class Meta:
        model = ThamDu
        fields = [
            'id',
            'student_code',
            'student_name',
            'status',
            'subject_name',
            'date',
            'created_at'
        ]

    def get_student_name(self, obj):
        if obj.enrollment and obj.enrollment.student and obj.enrollment.student.user:
            user = obj.enrollment.student.user
            return f"{user.first_name} {user.last_name}"
        return ""


class AttendanceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer để cập nhật trạng thái điểm danh thủ công
    """

    class Meta:
        model = ThamDu
        fields = ['status']

    def validate_status(self, value):
        """Validate status"""
        allowed_statuses = ['Present', 'Absent', 'Late', 'Excused']
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Status phải là một trong: {', '.join(allowed_statuses)}"
            )
        return value