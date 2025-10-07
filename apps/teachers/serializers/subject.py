from rest_framework import serializers

from apps.my_built_in.models.subject import Subject


class SubjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'