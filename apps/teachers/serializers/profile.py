from rest_framework import serializers

from apps.my_built_in.models.giao_vien import GiaoVien 
from apps.authens.serializers.user import UserUpdateSerializer

class TeacherDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department= serializers.SerializerMethodField()
    class Meta:
        model = GiaoVien
        fields = ['id', "teacher_code", "degree", "title", "department", "user", "start_date", "end_date", "is_deleted"]
    
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
                "url": user.url.url if user.url and hasattr(user.url, 'url') else None,
            }
        return None
    
    def get_department(self, obj):
        department = obj.department
        if department:
            return {
                "id": department.id,
                "code": department.code,
                "name": department.name
            }
        return None
    
class TeacherUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()
    class Meta:
        model = GiaoVien
        fields = ["teacher_code", "degree", "title", "department", "user", "start_date", "end_date", "is_deleted"]
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            user_instance = instance.user
            user_serializer = UserUpdateSerializer(
                user_instance, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance