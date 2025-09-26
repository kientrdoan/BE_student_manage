from rest_framework.serializers import ModelSerializer

from apps.my_built_in.models.major import Major

class MajorDetailSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'name', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']