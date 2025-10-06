from rest_framework import serializers

from apps.my_built_in.models.course import Course

class CourseSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    class_st = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'semester', 'subject', 'instructor', 'class_st', 'max_capacity', 'updated_at', 'created_at']
        read_only_fields = ['id', 'updated_at', 'created_at']

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
    
    def get_instructor(self, obj):
        instructor = obj.instructor
        if instructor:
            return {
                "id": instructor.id,
                "instructor_code": instructor.instructor_code,
                "degree": instructor.degree,
                "name": f"{instructor.user.first_name} {instructor.user.last_name}" if instructor.user else "",
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
    
class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['semester', 'subject', 'instructor', 'class_st', 'max_capacity']