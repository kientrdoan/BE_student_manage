from rest_framework.serializers import ModelSerializer
from apps.my_built_in.models.lop_sinh_vien import LopSinhVien


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