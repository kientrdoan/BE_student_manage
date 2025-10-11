from rest_framework import serializers

from apps.my_built_in.models.mon_hoc import MonHoc

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['id', 'code', 'name', 'credit', 'description', 'total_period', 'major', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id']


class SubjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description', 'total_period', 'major']

class SubjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description', 'total_period', 'major', 'is_deleted']