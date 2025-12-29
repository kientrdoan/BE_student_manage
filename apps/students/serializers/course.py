from rest_framework import serializers

from apps.my_built_in.models.lop_tin_chi import LopTinChi
from apps.my_built_in.models.dang_ky import DangKy

class CourseSerializer(serializers.ModelSerializer):

    subject = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    class_st = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    remain_slot = serializers.SerializerMethodField()

    def get_remain_slot(self, obj):
        if obj.max_capacity is not None:
            dang_ky = DangKy.objects.filter(course=obj, is_deleted=False)
            enrolled_count = dang_ky.count()
            return obj.max_capacity - enrolled_count
        return None

    class Meta:
        model = LopTinChi
        fields = ['id', 'subject', 'remain_slot', 'teacher', 'class_st', 'room', 'max_capacity', 'start_date', 'end_date', 'weekday', 'start_period']
    def get_subject(self, obj):
        subject = obj.subject
        if subject:
            return {
                "code": subject.code,
                "name": subject.name,
                "credit": subject.credit,
            }
        return None
    def get_teacher(self, obj):
        teacher = obj.teacher
        if teacher:
            return {
                "teacher_code": teacher.teacher_code,
                "user": {
                    "first_name": teacher.user.first_name,
                    "last_name": teacher.user.last_name,
                }
            }
        return None
    def get_class_st(self, obj):
        class_st = obj.class_st
        if class_st:
            return {
                "name": class_st.name,
                "major": {
                    "name": class_st.major.name,
                }
            }
        return None
    
    def get_room(self, obj):
        room = obj.room
        if room is not None and hasattr(room, "room_code"):
            return {
                "room_code": room.room_code,
            }
        return None


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LopTinChi
        fields = ['id', 'start_date', 'end_date', 'weekday']