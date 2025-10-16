
from rest_framework import serializers
from apps.my_built_in.models.dang_ky import DangKy

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    sinh_vien = serializers.SerializerMethodField()
    mon_hoc = serializers.SerializerMethodField()
    class Meta:
        model = DangKy
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_sinh_vien(self, obj):
        sinh_vien = obj.sinh_vien
        if sinh_vien:
            return {
                "id": sinh_vien.id,
                "student_code": sinh_vien.student_code,
                "user": {
                    "first_name": sinh_vien.user.first_name,
                    "last_name": sinh_vien.user.last_name,
                    "email": sinh_vien.user.email,
                }
            }
        return None

    def get_mon_hoc(self, obj):
        mon_hoc = obj.mon_hoc
        if mon_hoc:
            return {
                "id": mon_hoc.id,
                "code": mon_hoc.code,
                "name": mon_hoc.name,
                "credit": mon_hoc.credit,
            }
        return None