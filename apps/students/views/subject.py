from rest_framework.views import APIView

from apps.my_built_in.models.lop_sinh_vien import LopSinhVien
from apps.my_built_in.models.mon_hoc import MonHoc as Subject
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.subject import SubjectDetailSerializer


class SubjectView(APIView):
    def get(self, request, user_id):
        try:
            lop_sv = LopSinhVien.objects.get(sinh_vien__user__id=user_id)
            subjects = Subject.objects.filter(major=lop_sv.major)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = SubjectDetailSerializer(subjects, many=True)
        return ResponseFormat.response(data=serializer.data)
