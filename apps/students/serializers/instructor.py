from rest_framework import serializers

from apps.my_built_in.models.instructors import Instructor


class InstructorDetailSerializer(serializers.ModelSerializer):


    class Meta:
        model = Instructor
        fields = ['id', 'user', 'bio', 'courses']