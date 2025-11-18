from rest_framework import serializers

from apps.my_built_in.models.mon_hoc import MonHoc

class SubjectListSerializer(serializers.ModelSerializer):
    major = serializers.SerializerMethodField()
    class Meta:
        model = MonHoc
        fields = ['id', 'code', 'name', 'credit', 'description', 'total_period', 'major', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id']
    
    def get_major(self, obj):
        major = obj.major
        if major:
            return {
                "major_id": major.id,
                "major_name": major.name
            }
        return None

class SubjectSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    class Meta:
        model = MonHoc
        fields = ['id', 'code', 'name', 'credit', 'description', 'total_period', 'major', 'department', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id']

    def get_department(self, obj):
        department = obj.major.department
        if department:
            return department.id
        return None

class SubjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description', 'total_period', 'major']
    

class SubjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description', 'total_period', 'major', 'is_deleted']