from rest_framework import serializers

from apps.my_built_in.models.mon_hoc import MonHoc


class SubjectDetailSerializer(serializers.ModelSerializer):

    major = serializers.SerializerMethodField()

    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description', 'major', 'total_period']
    
    def get_major(self, obj):
        major = obj.major
        if major:
            return {
                "name": major.name,
            }
        return None