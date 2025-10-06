from rest_framework.serializers import ModelSerializer
from apps.my_built_in.models.classes import Class


class ClassDetailSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'major', 'start_year', 'end_year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']