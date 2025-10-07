from rest_framework.serializers import ModelSerializer

from apps.my_built_in.models.nganh import Nganh

class MajorDetailSerializer(ModelSerializer):
    class Meta:
        model = Nganh
        fields = ['id', 'name', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']