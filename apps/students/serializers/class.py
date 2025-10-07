from rest_framework import serializers
from apps.my_built_in.models.class_ import Class

class ClassDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class  # Replace with your Class model
        fields = ['id', 'name', 'major', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']