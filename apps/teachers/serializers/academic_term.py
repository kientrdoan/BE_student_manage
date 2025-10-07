from rest_framework import serializers

from apps.my_built_in.models.academic_term import AcademicTerm


class AcademicTermDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicTerm
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')