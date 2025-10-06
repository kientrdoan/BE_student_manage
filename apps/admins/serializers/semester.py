from rest_framework import serializers

from apps.my_built_in.models.hoc_ky import Semester


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'semesters', 'start_date', 'end_date']
        read_only_fields = ['id']