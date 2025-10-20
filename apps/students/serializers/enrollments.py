
from rest_framework import serializers
from apps.my_built_in.models.dang_ky import DangKy

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['id', 'enrolled_at', 'course']
        read_only_fields = ['id']

    # def get_student(self, obj):
    #     student = obj.student
    #     if student:
    #         return {
    #             "id": student.id,
    #             "student_code": student.student_code,
    #             "user": {
    #                 "first_name": student.user.first_name,
    #                 "last_name": student.user.last_name,
    #                 "email": student.user.email,
    #             }
    #         }
    #     return None

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
            }
        return None
    
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['student', 'enrolled_at', 'course']

class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    # student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['is_deleted']