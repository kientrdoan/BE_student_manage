from rest_framework import serializers

from apps.my_built_in.models.sinh_vien import Student
from apps.my_built_in.models.tai_khoan import User

from apps.authens.serializers.user import UserCreateSerializer, UserUpdateSerializer

class StudentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = ['id', 'student_code', 'classes', "user"]
    
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
                "date_of_birth": user.date_of_birth,
                "gender": user.gender,
                "url": user.url
            }
        return None
    
class StudentCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    class Meta:
        model = Student
        fields = ['id', 'student_code', 'classes', "user"]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserCreateSerializer().create(user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student
    
class StudentUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()
    class Meta:
        model = Student
        fields = ['id', 'student_code', 'classes', "user"]
    
    def update(self, instance, validated_data):
        # Lấy dữ liệu user
        user_data = validated_data.pop('user', None)

        # Update Student trước
        instance.student_code = validated_data.get('student_code', instance.student_code)
        instance.classes = validated_data.get('classes', instance.classes)
        instance.save()

        # Update User nếu có dữ liệu
        if user_data:
            user_instance = instance.user
            user_serializer = UserUpdateSerializer(user_instance, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return instance