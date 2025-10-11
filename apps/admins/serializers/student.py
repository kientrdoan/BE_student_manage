from rest_framework import serializers

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.tai_khoan import TaiKhoan

from apps.authens.serializers.user import UserCreateSerializer, UserUpdateSerializer

class StudentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
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
    
class StudentCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    class Meta:
        model = SinhVien
        fields = ['id', 'student_code', 'class_student', 'user']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserCreateSerializer().create(user_data)
        student = SinhVien.objects.create(user=user, **validated_data)
        return student
    
class StudentUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()
    class Meta:
        model = SinhVien
        fields = ['student_code', 'class_student', 'user', 'is_deleted']
    
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