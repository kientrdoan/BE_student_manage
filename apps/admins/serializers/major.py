from rest_framework import serializers

from apps.my_built_in.models.nganh import Nganh


class MajorDetailSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField
    class Meta:
        model = Nganh
        fields = ['id', 'name', 'department', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']

class MajorCreateSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField
    class Meta:
        model = Nganh
        fields = ['id', 'name', 'department']

class MajorListSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    class Meta:
        model = Nganh
        fields = ['id', 'name', 'department', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_department(self, obj):
        department = obj.department
        if department:
            return {
                "department_id": department.id,
                "department_name": department.name
            }
        return None