from rest_framework import serializers

from apps.my_built_in.models.course_session import CourseSession


class CourseSessionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = '__all__'