from rest_framework import serializers

class StudentDetailSerializer(serializers.Serializer):

    class Meta:
        fields = ['id', 'user', 'enrolled_courses']