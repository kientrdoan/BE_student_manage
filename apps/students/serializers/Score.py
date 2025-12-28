from rest_framework import serializers

from apps.my_built_in.models.dang_ky import DangKy

class ScoreSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = [
            'id',
            'mid_score',
            'discuss_score',
            'project_scoure',
            'final_score',
            'attendance_score',
            'exercise_score',
            'semester',
            'subject',
        ]
    def get_semester(self, obj):
        semester = obj.course.semester
        if semester:
            return {
                "semester_id": semester.id,
                "semester_name": semester.semesters,
                'year': semester.year,
                "start_date": semester.start_date,
                "end_date": semester.end_date,
            }
        return None
    def get_subject(self, obj):
        subject = obj.course.subject
        if subject:
            return {
                "subject_id": subject.id,
                "subject_code": subject.code,
                "subject_name": subject.name,
                "subject_credit": subject.credit,
            }
        return None