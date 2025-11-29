from rest_framework.serializers import ModelSerializer, SerializerMethodField
from apps.my_built_in.models.lop_sinh_vien import LopSinhVien

class ClassListSerializer(ModelSerializer):
    major = SerializerMethodField()
    class Meta:
        model = LopSinhVien
        fields = ['id', 'name', 'major', 'start_year', 'end_year', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_major(self, obj):
        major = obj.major
        if major:
            return {
                "major_id": major.id,
                "major_name": major.name,
                "department_id": major.department.id,
            }
        return None


class ClassDetailSerializer(ModelSerializer):
    class Meta:
        model = LopSinhVien
        fields = ['id', 'name', 'major', 'start_year', 'end_year', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClassCreateSerializer(ModelSerializer):
    class Meta:
        model = LopSinhVien
        fields = ['name', 'major', 'start_year', 'end_year']

class ClassUpdateSerializer(ModelSerializer):
    class Meta:
        model = LopSinhVien
        fields = ['name', 'major', 'start_year', 'end_year', 'is_deleted']