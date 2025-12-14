from rest_framework.serializers import ModelSerializer

from apps.my_built_in.models.buoi_hoc import BuoiHoc

class TimeSlotSerializer(ModelSerializer):
    class Meta:
        model = BuoiHoc
        fields = ['id', 'course_id', 'date']

class TimeSlotUpdateSerializer(ModelSerializer):
    class Meta:
        model = BuoiHoc
        fields = ['date']
        