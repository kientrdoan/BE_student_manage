from rest_framework import serializers
from apps.my_built_in.models.buoi_hoc import BuoiHoc

class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuoiHoc
        fields = ['id', 'course', 'date', 'is_open']