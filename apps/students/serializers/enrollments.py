
from rest_framework import serializers
from apps.my_built_in.models.dang_ky import DangKy

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['id', 'enrolled_at', 'course']
        read_only_fields = ['id']

    def get_course(self, obj):
        course = obj.course
        if course:
            return {
                "course_id": course.id,
                "course_start_date": course.start_date,
                "course_end_date": course.end_date,
                "course_weekday": course.weekday,
                "subject_code": course.subject.code,
                "subject_name": course.subject.name,
                "subject_credit": course.subject.credit,
                "room": course.room.room_code,
                "start_period": course.start_period,
                "teacher": course.teacher.teacher_code ,
            }
        return None
    
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['student', 'enrolled_at', 'course']
