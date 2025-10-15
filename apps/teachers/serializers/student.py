from rest_framework import serializers
from apps.my_built_in.models.sinh_vien import SinhVien

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    # class_student = serializers.SerializerMethodField()
    class Meta:
        model = SinhVien
        fields = ['id', 'student_code', 'class_student', 'user', 'is_deleted']
    
    def get_user(self, obj):
        user = obj.user
        if user:
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "address": user.address,
                "identity_number": user.identity_number,
                "birthday": user.birthday,
                "gender": user.gender,
                "url": user.url
            }
        return None