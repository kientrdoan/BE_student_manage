from rest_framework import serializers

from apps.my_built_in.models.giao_vien import GiaoVien 

from apps.authens.serializers.user import UserCreateSerializer, UserUpdateSerializer

class TeacherDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = GiaoVien
        fields = ['id', "teacher_code", "degree", "title", "department", "user", "start_date", "end_date", "is_deleted"]
    
    def get_department(self, obj):
        department = obj.department
        if department:
            return {
                "department_id": department.id,
                "department_name": department.name
            }
        return None

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
    
class TeacherCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    class Meta:
        model = GiaoVien
        fields = ["teacher_code", "degree", "title", "department", "user", "start_date", "end_date"]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserCreateSerializer().create(user_data)
        student = GiaoVien.objects.create(user=user, **validated_data)
        return student
    
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