from rest_framework import serializers

from apps.my_built_in.models.lop_tin_chi import LopTinChi

class CourseSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()
    class_st = serializers.SerializerMethodField()
    # teacher = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    class Meta:
        model= LopTinChi
        fields= ['id', 'semester', 'class_st', 'subject', 'room', 'start_date', 'end_date', 'weekday', 'start_period']

    def get_semester(self, obj):
        semester = obj.semester
        if semester:
           return {
               "id": semester.id,
               "year": semester.year,
               "semester": semester.semesters
           }
        return None

    def get_class_st(self, obj):
        class_st = obj.class_st
        if class_st:
            return {
                "id": class_st.id,
                "name": class_st.name
            }
        return None
    
    def get_subject(self, obj):
        subject= obj.subject
        if subject:
            return {
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
                "credit": subject.credit
            }
        return None
        
    def get_room(self, obj):
        room= obj.room
        if room:
            return {
                "id": room.id,
                "code": room.room_code,
                "building": room.building,
            }
        return None
