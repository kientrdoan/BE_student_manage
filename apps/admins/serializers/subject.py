from rest_framework import serializers

from apps.my_built_in.models.mon_hoc import MonHoc

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = ['id', 'code', 'name', 'credit', 'description', 'total_period', 'theory_period', 'lab_period', 'major']
        read_only_fields = ['id']