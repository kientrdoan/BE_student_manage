from rest_framework import serializers

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course

class CourseSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    class_st = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'semester', 'subject', 'teacher', 'class_st', 'room', 'max_capacity', 'start_date', 'end_date', 'weekday', 'start_period', 'updated_at', 'created_at', 'is_deleted']
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
                "major_id": class_st.major.id,
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
    
class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['semester', 'subject', 'class_st', 'max_capacity']

class CourseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['semester', 'subject', 'teacher', 'class_st', 'room', 'max_capacity', 'start_date', 'end_date', 'weekday', 'start_period', 'is_deleted']