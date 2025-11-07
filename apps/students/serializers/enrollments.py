from rest_framework import serializers
from apps.my_built_in.models.dang_ky import DangKy


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = DangKy
        fields = ["id", "enrolled_at", "course"]
        read_only_fields = ["id"]

    def get_course(self, obj):
        course = obj.course
        
        if course:
            subject = getattr(course, "subject", None)
            teacher = getattr(course, "teacher", None)
            room = getattr(course, "room", None)
            return {
                "course_id": course.id,
                "course_start_date": course.start_date,
                "course_end_date": course.end_date,
                "course_weekday": course.weekday,
                "subject_code": getattr(subject, "code", None),
                "subject_name": getattr(subject, "name", None),
                "subject_credit": getattr(subject, "credit", None),
                "room": getattr(room, "room_code", None),
                "start_period": course.start_period,
                "teacher": getattr(teacher, "teacher_code", None),
            }
        return None


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()

    class Meta:
        model = DangKy
        fields = ["student", "enrolled_at", "course"]
