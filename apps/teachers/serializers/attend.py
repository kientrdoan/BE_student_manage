from rest_framework import serializers

from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.sinh_vien import SinhVien

class AttendSerializer(serializers.ModelSerializer):
    attends = serializers.SerializerMethodField()
    class Meta:
        model = SinhVien
        fields = ['id', 'student_code', 'attends']
    
    def get_attends(self, obj):
        try:
            attend = ThamDu.objects.filter(
                enrollment__student__id = obj.id,
                enrollment__is_deleted = False,
            )
            return attend.values("id", "status", "time_slot__date")
        except ThamDu.DoesNotExist:
            return None
        
class AttendCreateSerializer(serializers.ModelSerializer):
    attends = serializers.SerializerMethodField()
    class Meta:
        model = ThamDu
        fields = ['enroll_id', 'time_slot_id', 'status']

           

