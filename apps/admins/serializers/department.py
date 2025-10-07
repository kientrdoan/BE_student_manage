from rest_framework.serializers import ModelSerializer

from apps.my_built_in.models.khoa import Khoa

class DepartmentDetailSerializer(ModelSerializer):
    class Meta:
        model = Khoa
        fields = ['id', 'code', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

