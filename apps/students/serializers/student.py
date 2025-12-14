from rest_framework import serializers

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.authens.serializers.user import UserUpdateSerializer


class StudentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class_student = serializers.SerializerMethodField()
    class Meta:
        model = SinhVien
        fields = ['id', 'student_code', 'class_student', 'user']
    def get_user(self, obj):
        user = obj.user
        if user:
            return {
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
    def get_class_student(self, obj):
        class_student = obj.class_student
        if class_student:
            return {
                "name": class_student.name,
            }
        return None
    
class StudentUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()
    class Meta:
        model = SinhVien
        fields = ['student_code', "user"]
    
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

