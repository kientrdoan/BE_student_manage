from rest_framework import serializers

from apps.my_built_in.models.dang_ky import DangKy

class ScoreStudentSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = ['id', 'attendance_score', 'discuss_score', 'exercise_score', 
                  'project_score', 'mid_score', 'final_score', 'student', 'subject']
        read_only_fields = ['id']

    def get_student(self, obj):
        student = obj.student
        if student:
            user = student.user
            return {
                "student_code": student.student_code,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        return None
    
    def get_subject(self, obj):
        course = obj.course
        if course:
            subject = course.subject
            if subject:
                return {
                    "code": subject.code,
                    "name": subject.name,
                }
        return None

