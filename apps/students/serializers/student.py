from rest_framework import serializers

from apps.my_built_in.models.sinh_vien import SinhVien


class StudentDetailSerializer(serializers.Serializer):
    class Meta:
        model = SinhVien
        fields = ['id', 'student_code', 'class_id', 'user_id']
