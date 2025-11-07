from rest_framework import serializers

from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.sinh_vien import SinhVien

class AttendSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    # start_course = serializers.SerializerMethodField()
    # end_course = serializers.SerializerMethodField()

    class Meta:
        model = ThamDu
        fields = ['id', 'status', 'date']

    def get_date(self, obj):
        return obj.time_slot.date if obj.time_slot else None
    
    # def get_start_course(self, obj):
    #     return obj.time_slot.start_course if obj.time_slot else None
    
    # def get_end_course(self, obj):
    #     return obj.time_slot.end_course if obj.time_slot else None
           

