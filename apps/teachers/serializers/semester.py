from rest_framework import serializers

from apps.my_built_in.models.hoc_ky import HocKy

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HocKy
        fields = ['id', 'year', 'semesters']