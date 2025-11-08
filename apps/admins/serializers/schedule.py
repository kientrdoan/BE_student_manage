from rest_framework import serializers
from apps.my_built_in.models.lop_tin_chi import LopTinChi
from apps.my_built_in.models.giao_vien import GiaoVien
from apps.my_built_in.models.phong_hoc import PhongHoc
from apps.my_built_in.models.hoc_ky import HocKy


class ScheduleInputSerializer(serializers.Serializer):
    """Serializer cho input của scheduling"""
    semester_id = serializers.IntegerField(required=True)
    excel_file = serializers.FileField(required=False, allow_null=True)

    # GA Parameters (optional)
    population_size = serializers.IntegerField(required=False, default=100)
    generations = serializers.IntegerField(required=False, default=200)
    crossover_rate = serializers.FloatField(required=False, default=0.8)
    mutation_rate = serializers.FloatField(required=False, default=0.05)

    def validate_semester_id(self, value):
        """Validate semester exists"""
        try:
            HocKy.objects.get(id=value, is_deleted=False)
        except HocKy.DoesNotExist:
            raise serializers.ValidationError("Học kỳ không tồn tại")
        return value

    def validate_excel_file(self, value):
        """Validate Excel file format"""
        if value:
            if not value.name.endswith(('.xlsx', '.xls')):
                raise serializers.ValidationError("File phải có định dạng .xlsx hoặc .xls")

            # Kiểm tra kích thước file (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Kích thước file không được vượt quá 5MB")

        return value


class CourseScheduleSerializer(serializers.ModelSerializer):
    """Serializer cho kết quả xếp lịch của một lớp"""
    semester = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    class_st = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model = LopTinChi
        fields = [
            'id', 'semester', 'subject', 'teacher', 'class_st', 'room',
            'max_capacity', 'weekday', 'start_period',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]

    def get_semester(self, obj):
        semester = obj.semester
        if semester:
            return {
                "id": semester.id,
                "semesters": semester.semesters,
            }
        return None

    def get_subject(self, obj):
        subject = obj.subject
        if subject:
            return {
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
                "credits": subject.credit,
            }
        return None

    def get_teacher(self, obj):
        teacher = getattr(obj, "teacher", None)
        if teacher:
            return {
                "id": teacher.id,
                "teacher_code": teacher.teacher_code,
                "degree": teacher.degree,
                "name": f"{teacher.user.first_name} {teacher.user.last_name}" if teacher.user else "",
            }
        return None

    def get_class_st(self, obj):
        class_st = obj.class_st
        if class_st:
            return {
                "id": class_st.id,
                "name": class_st.name,
            }
        return None

    def get_room(self, obj):
        room = getattr(obj, "room", None)
        if room:
            return {
                "id": room.id,
                "room_code": room.room_code,
            }
        return None


class ScheduleResultSerializer(serializers.Serializer):
    """Serializer cho kết quả tổng thể của thuật toán"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    scheduled_courses = CourseScheduleSerializer(many=True, required=False)
    statistics = serializers.DictField(required=False)
    violations = serializers.DictField(required=False)
    fitness_score = serializers.FloatField(required=False)
    generations_run = serializers.IntegerField(required=False)
    hard_assignments_count = serializers.IntegerField(required=False)


class HardAssignmentSerializer(serializers.Serializer):
    """Serializer để validate hard assignment từ Excel"""
    course_id = serializers.IntegerField()
    teacher_id = serializers.IntegerField()
    room_id = serializers.IntegerField()
    day_idx = serializers.IntegerField(min_value=0, max_value=5)  # 0-5: Thứ 2-7
    slot = serializers.IntegerField(min_value=1, max_value=6)  # 1-6: Tiết học
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_course_id(self, value):
        """Validate course exists"""
        try:
            LopTinChi.objects.get(id=value, is_deleted=False)
        except LopTinChi.DoesNotExist:
            raise serializers.ValidationError(f"Lớp tín chỉ ID {value} không tồn tại")
        return value

    def validate_teacher_id(self, value):
        """Validate teacher exists"""
        try:
            GiaoVien.objects.get(id=value, is_deleted=False)
        except GiaoVien.DoesNotExist:
            raise serializers.ValidationError(f"Giáo viên ID {value} không tồn tại")
        return value

    def validate_room_id(self, value):
        """Validate room exists"""
        try:
            PhongHoc.objects.get(id=value, is_active=True)
        except PhongHoc.DoesNotExist:
            raise serializers.ValidationError(f"Phòng học ID {value} không tồn tại")
        return value