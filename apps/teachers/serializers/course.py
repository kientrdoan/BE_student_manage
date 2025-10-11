from rest_framework import serializers

from apps.my_built_in.models.lop_tin_chi import LopTinChi


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LopTinChi
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']