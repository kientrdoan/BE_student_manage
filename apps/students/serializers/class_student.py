from rest_framework.serializers import ModelSerializer
from apps.my_built_in.models.lop_sinh_vien import LopSinhVien

class ClassDetailSerializer(ModelSerializer):
    class Meta:
        model = LopSinhVien
        fields = ['id', 'name', 'major']
        read_only_fields = ['id']